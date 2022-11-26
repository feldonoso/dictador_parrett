from otree.api import *



doc = """
This application provides a webpage instructing participants how to get paid.
Examples are given for the lab and Amazon Mechanical Turk (AMT).
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment_info'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
# PAGES
class PaymentA(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        return dict(redemption_code=participant.label or participant.code)

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class PaymentB(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        return dict(redemption_code=participant.label or participant.code)
    
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2


page_sequence = [PaymentA, PaymentB]
