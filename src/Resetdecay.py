from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty



class ResetDecay(Widget):

    reset_level = NumericProperty(0)
    amount = NumericProperty(0)
    buy_cost = NumericProperty(0)
    cost_increase = NumericProperty(1.6)


    def reset_decay(self,game):
        game.fade_timer_list["Timer"], game.fade_timer_list["Counter"] = 0, 0
        for enemy in game.children:
            if enemy.__class__.__name__ == 'Enemy':
                game.remove_widget(enemy)

    def get_cost(self):
        return self.buy_cost

    def buy_reset(self, game):
        self.reset_decay(game)
        self.amount += 1
        self.buy_cost = int(self.buy_cost * self.cost_increase)

