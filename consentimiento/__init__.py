from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'Consentimiento'
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
    crt_celular = models.StringField( 
        label='''
        Introduzca su número de celular asociado a yape/plin'''
    )
    consentimiento = models.StringField(
        choices=[['Sí', 'Sí'], ['No', 'No']],
        label='Al aceptar, expreso que deseo participar de manera voluntaria y conozco las condiciones previamente mencionadas. ¿Acepta participar?',
        widget=widgets.RadioSelect,
    )
    payment = models.StringField(
        choices=[['Yape', 'Yape'], ['Plin', 'Plin'], ['Transferencia', 'Transferencia']],
        label='¿Entendi?',
        widget=widgets.RadioSelect,
    )
    civil = models.StringField(
        choices=[['Soltero/a', 'Soltero/a'], ['Casado/a', 'Casado/a'], ['Viudo/a', 'Viudo/a'], ['Divorciado/a', 'Divorciado/a']],
        label='¿Cuál es su estado civil?',
        widget=widgets.RadioSelect,
    )
    preg1 = models.StringField(
        choices=[['Jugador A', 'Jugador A'], ['Jugador B', 'Jugador B']],
        label='¿Cuál jugador decidirá cómo repartir el premio?',
        widget=widgets.RadioSelect,
    )
    preg2 = models.StringField(
        choices=[['Si', 'Si'], ['No', 'No']],
        label='¿Los jugadores A participarán del juego de las flechas?',
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

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you qcould make uiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(consentimiento='Sí')
        # error_message can return a dict whose keys are field names and whose
        # values are error messages
        errors = {f: 'Error' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 1:
                player.failed_too_many = True
                # we don't return any error here; just let the user proceed to the
                # next page, but the next page is the 'failed' page that boots them
                # from the experiment.
            else:
                return errors

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
            if player.num_failed_attempts >= 1:
                player.failed_too_many = True
                # we don't return any error here; just let the user proceed to the
                # next page, but the next page is the 'failed' page that boots them
                # from the experiment.
            else:
                return errors



class Failed(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.failed_too_many


page_sequence = [Consent, Failed]

