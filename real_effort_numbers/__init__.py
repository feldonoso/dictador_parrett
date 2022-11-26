from otree.api import *
import random

c=Currency
doc = """
Your app description
"""



class Constants(BaseConstants):
    name_in_url = 'real_effort_numbers'
    players_per_group = None
    num_rounds = 1
    payment_per_correct_answer = cu(1)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    number_entered = models.IntegerField()
    sum_of_numbers = models.IntegerField()



# PAGES
class AddNumbers(Page):
    form_model ="player"
    form_fields=["number_entered"]
    @staticmethod
    def vars_for_template(player:Player):
        number_1 = random.randint(1, 100)
        number_2 = random.randint(1, 100)
        player.sum_of_numbers=number_1+number_2
        return{
            "number_1":number_1,
            "number_2":number_2
        }
    
    @staticmethod
    def before_next_page(player:Player, timeout_happened):
        if player.sum_of_numbers==player.number_entered:
            player.payoff=Constants.payment_per_correct_answer

class Results(Page):
    pass
   

class CombinedResults(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number==Constants.num_rounds
    @staticmethod
    def vars_for_template(player:Player):
        all_players = player.in_all_rounds()
        combined_payoff=0
        for temp_player in all_players:
            combined_payoff += temp_player.payoff
        return{
            "combined_payoff":combined_payoff
        }
page_sequence = [AddNumbers,Results, CombinedResults]
