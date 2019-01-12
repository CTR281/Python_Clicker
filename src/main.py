import kivy

kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button, Label
import kivy.uix.label
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from math import *


class Enemy_Label(Label):
    pos_x= NumericProperty(0)
    pos_y=NumericProperty(0)
    pos = ReferenceListProperty(pos_x, pos_y)

    def __init__(self,enemy, **kwargs):
        super(Label, self).__init__(**kwargs)
        self.pos_x = enemy.pos[0]
        self.pos_y = enemy.pos[1]
        self.pos = self.pos[0], self.pos[1]
        self.color = [0,0,1,1]
        self.text = str(enemy.enemy_weight)



class Enemy(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    enemy_weight = NumericProperty(0)

    def __init__(self,game, feedpower, **kwarg):
        super(Enemy, self).__init__(**kwarg)
        self.velocity_x = randint(2, 5)
        self.velocity_y = randint(2, 5)
        self.velocity = self.velocity_x, self.velocity_y
        self.pos = (5, randint(210, 500))
        self.enemy_weight = randint(2, 10)
        self.size = self.enemy_weight * 5 + 20, self.enemy_weight * 5 + 20

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def on_touch(self, touch, feedpower):
        if self.collide_point(*touch.pos):
            self.enemy_weight -= feedpower


class AutoClicker(Widget):
    feed_per_second = NumericProperty(0)
    amount = NumericProperty(0)
    buy_cost = NumericProperty(0)
    cost_increase = NumericProperty(1.2)
    tier = NumericProperty(1)

    def autofeed(self):
        return self.feed_per_second * self.amount

    def get_cost(self):
        return self.buy_cost

    def buy_auto(self):
        self.amount += 1
        self.buy_cost = int(self.buy_cost * self.cost_increase)


class ClickerCell(Widget):
    feedpower = NumericProperty(1)
    feedpower_upgrade_cost = NumericProperty(10)

    cell_weight = NumericProperty(101)
    fade_factor = NumericProperty(0)
    fade_list = [0 * k for k in range(100)]

    def __init__(self, **kwargs):
        super(ClickerCell, self).__init__(**kwargs)
        self.size = self.cell_weight, self.cell_weight

    def add_weight(self, amount):
        self.cell_weight += amount
        self.size = self.cell_weight, self.cell_weight
        self.center = self.center_x - amount / 2, self.center_y - amount / 2

    def collide(self, enemy, game):
        if sqrt((self.center_x-enemy.center_x)**2 + (self.center_y-enemy.center_y)**2) < (self.size[0]+enemy.size[0])/2:
            self.add_weight(-enemy.enemy_weight)
            game.remove_widget(enemy)

    def grow(self):
        self.add_weight(self.feedpower)

    def fade(self, game):
        if self.cell_weight > 0:
            if self.cell_weight - self.fade_factor > 0:
                self.add_weight(-self.fade_factor)
            else:
                self.cell_weight = 1
                self.pos = game.width * 3 / 8, game.height * 5 / 8

    def upgrade_feedpower(self):
        if self.cell_weight >= self.feedpower_upgrade_cost:
            self.add_weight(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 1.15)
        else:
            print("Not Enought Weight")


class ClickerGame(Widget):
    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    auto_tier1 = ObjectProperty(tier=StringProperty("1"))
    auto_tier2 = ObjectProperty(tier=StringProperty("2"))

    timer = NumericProperty(0)
    limit_x, limit_y =  6/8, 1/8

    gameover = StringProperty("")
    count = 0
    phase2 = False

    def autofeed(self):
        self.cell.add_weight(self.auto_tier1.autofeed())
        self.cell.add_weight(self.auto_tier2.autofeed())

    def buy_auto(self, autoclicker):
        if self.cell.cell_weight >= autoclicker.get_cost():
            self.cell.add_weight(-autoclicker.get_cost())
            autoclicker.buy_auto()
        else:
            print("Not Enought weight")

    def spawn_enemy(self):

        self.add_widget(Enemy(self, self.cell.feedpower))

    def bounce(self, enemy):

        if (enemy.pos[1] < self.height * 1 / 8 + 10) or (enemy.top > self.height):
            enemy.velocity_y *= -1


        if (enemy.pos[0] < 0) or (enemy.pos[0] + enemy.size[0] > self.width * 3 / 4):
            enemy.velocity_x *= -1

    def update(self, dt):
        if self.gameover == "Game Over":
            return
        self.count += 1
        if self.count % 30 == 0:
            self.timer += 1
            if self.timer >= 0:
                self.phase2 = True
            if self.timer in self.cell.fade_list:
                self.cell.fade_factor += self.timer / 5
            if int(self.timer) % 2 == 0:
                self.cell.fade(self)
            if self.phase2:
                if int(self.timer) % 5 == 0:
                    self.spawn_enemy()
            if self.cell.cell_weight == 1:
                self.gameover = "Game Over"

            self.autofeed()

        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)

    def on_touch_down(self, touch):
         for child in self.children:
             if child.__class__.__name__ == "Enemy":
                 child.on_touch(touch, self.cell.feedpower)
                 if child.enemy_weight <= 0:
                     self.remove_widget(child)
                 return True
             else:
                 child.on_touch_down(touch)



class ClickerApp(App):
    def build(self):
        self.game = ClickerGame()
        Clock.schedule_interval(self.game.update, 1 / 30)
        return self.game


if __name__ == '__main__':
    ClickerApp().run()

