from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'Survey'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label='¿Cuál es su edad?', min=13, max=125)
    
    gender = models.StringField(
        choices=[['Hombre', 'Hombre'], ['Mujer', 'Mujer'], ['Otro', 'Otro']],
        label='¿Cuál es su género?',
        widget=widgets.RadioSelect,
    )
    payment = models.StringField(
        choices=[['Yape', 'Yape'], ['Plin', 'Plin'], ['Transferencia', 'Transferencia']],
        label='¿Cuál método de pago prefiere?',
        widget=widgets.RadioSelect,
    )
    civil = models.StringField(
        choices=[['Soltero/a', 'Soltero/a'], ['Casado/a', 'Casado/a'], ['Viudo/a', 'Viudo/a'], ['Divorciado/a', 'Divorciado/a']],
        label='¿Cuál es su estado civil?',
        widget=widgets.RadioSelect,
    )
    ingresos = models.StringField(
        choices=[['Si', 'Si'], ['No', 'No']],
        label='¿Actualmente tiene alguna fuente de ingresos?',
        widget=widgets.RadioSelect,
    )
    mesero = models.StringField(
        choices=[['Si', 'Si'], ['No', 'No']],
        label='¿Alguna vez ha trabajado de mesero/a en un restaurante?',
        widget=widgets.RadioSelect,
    )

    educacion = models.IntegerField(
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
        label='¿Qué ciclo de la carrera se encuentra cursando? (Si actualmente no está estudiando, coloque 0)',
    )
    norma = models.StringField(
        choices=[['0-5%', '0-5%'], ['6-10%', '6-10%'], ['11-15%', '11-15%'], ['16-20%', '16-20%'], ['más de 20%', 'más de 20%']], 
        label='¿Qué porcentaje de la cuenta considera apropiado dejar como propina en un restaurante?',
        widget=widgets.RadioSelect,
    )   
    residencia = models.StringField(
        choices=[['Lima Metropolitana', 'Lima Metropolitana'], ['Lima Provincia', 'Lima Provincia'], ['Resto del Perú', 'Resto del Perú'], ['Extranjero', 'Extranjero'] ], 
        label='Lugar de residencia',
        widget=widgets.RadioSelect,
    )


    crt_bat = models.IntegerField(
        label='''
        A bat and a ball cost 22 dollars in total.
        The bat costs 20 dollars more than the ball.
        How many dollars does the ball cost?'''
    )
    crt_widget = models.IntegerField(
        label='''
        If it takes 5 machines 5 minutes to make 5 widgets,
        how many minutes would it take 100 machines to make 100 widgets?
        '''
    )
    crt_lake = models.IntegerField(
        label='''
        In a lake, there is a patch of lily pads.
        Every day, the patch doubles in size.
        If it takes 48 days for the patch to cover the entire lake,
        how many days would it take for the patch to cover half of the lake?
        '''
    )


# FUNCTIONS
# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'educacion', 'ingresos', 'mesero', 'norma']

class Infopagos(Page):
    form_model = 'player'
    form_fields = ['payment', 'crt_celular', 'crt_cci']


class CognitiveReflectionTest(Page):
    form_model = 'player'
    form_fields = ['crt_bat', 'crt_widget', 'crt_lake']


page_sequence = [Demographics]

