from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty



class AutoClicker(Widget):

    feed_per_second = NumericProperty(0)
    amount = NumericProperty(0)
    buy_cost = NumericProperty(0)
    cost_increase = NumericProperty(1.2)
    tier = StringProperty(1)

    def autofeed(self):
        return self.feed_per_second * self.amount

    def get_cost(self):
        return self.buy_cost

    def buy_auto(self):
        self.amount += 1
        self.buy_cost = int(self.buy_cost * self.cost_increase)
