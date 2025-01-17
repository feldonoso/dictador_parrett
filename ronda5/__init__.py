import time
import statistics as st
from otree import settings
from otree.api import *

from .image_utils import encode_image

doc = """
Real-effort tasks. The different tasks are available in task_matrix.py, task_transcription.py, etc.
You can delete the ones you don't need. 
"""
myList=[]
lista=[0]
monto=[0]
transferencia=[0]

def get_task_module(player):
    """
    This function is only needed for demo mode, to demonstrate all the different versions.
    You can simplify it if you want.
    """
    from . import task_matrix, task_transcription, task_decoding

    session = player.session
    task = session.config.get("task")
    if task == "matrix":
        return task_matrix
    if task == "transcription":
        return task_transcription
    if task == "decoding":
        return task_decoding
    # default
    return task_matrix


class Constants(BaseConstants):
    name_in_url = "ronda5"
    players_per_group = 2 
    num_rounds = 1
    instructions_template = __name__ + "/instructions.html"
    captcha_length = 3

    ####################################################
    dictator_role = 'Jugador A'
    agent_role = 'Jugador B'
    ENDOWMENT = cu(150)

    ####################################################


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    session = subsession.session
    defaults = dict(
        retry_delay=1.0, puzzle_delay=1.0, attempts_per_puzzle=1, max_iterations=None
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])


#class Group(BaseGroup):
#    pass


class Player(BasePlayer):
    iteration = models.IntegerField(initial=0)
    num_trials = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    premio = models.IntegerField(initial=0)
    monto_generado = models.IntegerField(initial=0)
    tiebreaker = models.IntegerField(initial=3)
    mensaje = models.StringField(label="")
    mediana = models.FloatField()



class Puzzle(ExtraModel):
    """A model to keep record of all generated puzzles"""

    player = models.Link(Player)
    iteration = models.IntegerField(initial=0)
    attempts = models.IntegerField(initial=0)
    timestamp = models.FloatField(initial=0)
    # can be either simple text, or a json-encoded definition of the puzzle, etc.
    text = models.LongStringField()
    # solution may be the same as text, if it's simply a transcription task
    solution = models.LongStringField()
    response = models.LongStringField()
    response_timestamp = models.FloatField()
    is_correct = models.BooleanField()

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
class Group(BaseGroup):
    transferencia = models.CurrencyField(
        doc="""Cantidad que el jugador A decide repartirle al jugador B""",
        min=0,
        max=Constants.ENDOWMENT,

        label="Le entregaré:",
    )


def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = 0    
    p2.payoff = 0       


class AgentPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.role == Constants.agent_role

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class MyWaitPage(WaitPage):
    wait_for_all_groups=True


class ResultsA(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player_b = player.group.get_player_by_id(1)
        group = player.group
        return dict(offer=player_b.premio - group.transferencia)

    #Dictador
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

class InicioA(Page):

    #Dictador
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

class ResultsB(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player_b = player.group.get_player_by_id(1)
        group = player.group
        return dict(offer=player_b.premio - group.transferencia)

     #Agente
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

class InicioB(Page):

     #Agente
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

class Offer(Page):
    form_model = 'group'
    form_fields = ['transferencia']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1
    
    

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    task_module = get_task_module(player)
    fields = task_module.generate_puzzle_fields()
    player.iteration += 1
    return Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(), **fields
    )


def get_current_puzzle(player):
    puzzles = Puzzle.filter(player=player, iteration=player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle


def encode_puzzle(puzzle: Puzzle):
    """Create data describing puzzle to send to client"""
    task_module = get_task_module(puzzle.player)  # noqa
    # generate image for the puzzle
    image = task_module.render_image(puzzle)
    data = encode_image(image)
    return dict(image=data)


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        num_trials=player.num_trials,
        num_correct=player.num_correct,
        premio=player.premio,
        iteration=player.iteration,
    )


def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from vrowser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'puzzle': data} -- in case of midgame page reload

    - receive: {'type': 'next'} -- request for a next/first puzzle
    - generate new puzzle
    - respond: {'type': 'puzzle', 'puzzle': data}

    - receive: {'type': 'answer', 'answer': ...} -- user answered the puzzle
    - check if the answer is correct
    - respond: {'type': 'feedback', 'is_correct': true|false, 'retries_left': ...} -- feedback to the answer

    If allowed by config `attempts_pre_puzzle`, client can send more 'answer' messages
    When done solving, client should explicitely request next puzzle by sending 'next' message

    Field 'progress' is added to all server responses to indicate it on page.

    To indicate max_iteration exhausted in response to 'next' server returns 'status' message with iterations_left=0
    """
    session = player.session
    my_id = player.id_in_group
    params = session.params
    task_module = get_task_module(player)

    now = time.time()
    # the current puzzle or none
    current = get_current_puzzle(player)

    message_type = message['type']

    # page loaded
    if message_type == 'load':
        p = get_progress(player)
        if current:
            return {
                my_id: dict(type='status', progress=p, puzzle=encode_puzzle(current))
            }
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "cheat" and settings.DEBUG:
        return {my_id: dict(type='solution', solution=current.solution)}

    # client requested new puzzle
    if message_type == "next":
        if current is not None:
            if current.response is None:
                raise RuntimeError("trying to skip over unsolved puzzle")
            if now < current.timestamp + params["puzzle_delay"]:
                raise RuntimeError("retrying too fast")
            if current.iteration == params['max_iterations']:
                return {
                    my_id: dict(
                        type='status', progress=get_progress(player), iterations_left=0
                    )
                }
        # generate new puzzle
        z = generate_puzzle(player)
        p = get_progress(player)
        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    # client gives an answer to current puzzle
    if message_type == "answer":
        if current is None:
            raise RuntimeError("trying to answer no puzzle")

        if current.response is not None:  # it's a retry
            if current.attempts >= params["attempts_per_puzzle"]:
                raise RuntimeError("no more attempts allowed")
            if now < current.response_timestamp + params["retry_delay"]:
                raise RuntimeError("retrying too fast")

            # undo last updation of player progress
            player.num_trials -= 1
            if current.is_correct:
                player.num_correct -= 1
            else:
                player.premio -= 0

        # check answer
        answer = message["answer"]

        if answer == "" or answer is None:
            raise ValueError("bogus answer")

        current.response = answer
        current.is_correct = task_module.is_correct(answer, current)
        current.response_timestamp = now
        current.attempts += 1

        # update player progress
        if current.is_correct:
            player.num_correct += 1
        else:
            player.premio += 0
        player.num_trials += 1

        retries_left = params["attempts_per_puzzle"] - current.attempts
        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                is_correct=current.is_correct,
                retries_left=retries_left,
                progress=p,
            )
        }

    raise RuntimeError("unrecognized message from client")


class Game(Page):
    timeout_seconds =60

    live_method = play_game

    @staticmethod
    def js_vars(player: Player):
        return dict(params=player.session.params)

    @staticmethod
    def vars_for_template(player: Player):
        task_module = get_task_module(player)
        return dict(DEBUG=settings.DEBUG,
                    input_type=task_module.INPUT_TYPE,
                    placeholder=task_module.INPUT_HINT)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened and not player.session.params['max_iterations']:
            raise RuntimeError("malicious page submission")

    ################ CAMBIOS ###################
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

class Results(Page):
    ################ CAMBIOS ###################
    #form_model = 'group'
    #form_fields = ['transferencia']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    myList.clear()

    @staticmethod 
    def vars_for_template(player: Player):
        player_b = player.group.get_player_by_id(2)

        output = {"b_num_trials": player_b.num_trials,
                  "b_num_correct": player_b.num_correct}
        myList.append(output["b_num_correct"])
        print(myList)
        return output

class Choice(Page):
    form_model = 'group'
    form_fields = ['transferencia']
    

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


    @staticmethod
    def vars_for_template(player):
        player_b = player.group.get_player_by_id(2)
        player_a = player.group.get_player_by_id(1)

        mediana=st.median(myList)
        player.mediana = st.median(myList)
        m=float(mediana)
        

        if (player_b.num_correct>mediana):
            player.mensaje="su <strong>Jugador B</strong> es parte del 50% <strong>superior</strong>, por lo que a usted se le ha asignado el premio de"
            player.monto_generado=150
            player.premio=150
            
        elif((player_b.num_correct==mediana)and(player.tiebreaker==3)):
            if((player.tiebreaker==3)&(lista[0]==0)):
                player.mensaje="su <strong>Jugador B</strong> es parte del 50% <strong>superior</strong>, por lo que a usted se le ha asignado el premio de"
                player.monto_generado=150
                player.tiebreaker=1
                player.premio=150
                lista[0]=1
            elif((player.tiebreaker==3)&(lista[0]==1)):
                player.mensaje="su <strong>Jugador B</strong> es parte del 50% <strong>inferior</strong>, por lo que a usted se le ha asignado el premio de"
                player.monto_generado=100
                player.tiebreaker=0
                player.premio=100  
                lista[0]=0
            
        elif(player_b.num_correct<mediana):
            player.mensaje="su <strong>Jugador B</strong> es parte del 50% <strong>inferior</strong>, por lo que a usted se le ha asignado el premio de"
            player.monto_generado=100
            player.premio=100

    
        return dict(
            a=player.mensaje,
            b=player.monto_generado
        )

page_sequence = [InicioA,InicioB,Game,ResultsWaitPage,MyWaitPage,Results,Choice,ResultsWaitPage,ResultsA,ResultsB]