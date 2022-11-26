from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'Intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    age = models.IntegerField(label='¿Cuál es su edad?', min=13, max=125)
    crt_cci = models.StringField( 
        label='''
        Introduzca su número de cuenta interbancaria'''
    )
    preg1 = models.StringField(
        choices=[['Jugador A', 'Jugador A'], ['Jugador B', 'Jugador B']],
        label='¿Cuál jugador decidirá cómo repartir el monto obtenido?',
        widget=widgets.RadioSelect,
    )
    preg2 = models.StringField(
        choices=[['Si', 'Si'], ['No', 'No']],
        label='¿Los jugadores A participarán del juego cognitivo?',
        widget=widgets.RadioSelect,
    )
    preg3 = models.StringField(
        choices=[['La primera', 'La primera'], ['La última', 'La última'], ['Una ronda aleatoria', 'Una ronda aleatoria'], ['Niguna de las anteriores', 'Niguna de las anteriores']], 
        label='¿Cuál de las rondas se usará para definir los pagos?',
        widget=widgets.RadioSelect,
    )
    



# FUNCTIONS
# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = ['consentimiento']

class Brief(Page):
    form_model = 'player'
    form_fields = ['preg1', 'preg2', 'preg3']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you qcould make uiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(preg1='Jugador A',preg2='No',preg3='Una ronda aleatoria')
        # error_message can return a dict whose keys are field names and whose
        # values are error messages
        errors = {f: 'Error' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 40:
                player.failed_too_many = True
                # we don't return any error here; just let the user proceed to the
                # next page, but the next page is the 'failed' page that boots them
                # from the experiment.
            else:
                return errors



class CognitiveReflectionTest(Page):
    form_model = 'player'
    form_fields = ['crt_bat', 'crt_widget', 'crt_lake']


page_sequence = [Brief]

