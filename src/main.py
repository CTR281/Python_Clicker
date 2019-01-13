import kivy

kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button, Label
import kivy.uix.label
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty, BoundedNumericProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.animation import *
from random import randint, choice
from math import *


class Enemy(Widget):

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    enemy_weight = NumericProperty(0)
    pv= NumericProperty(0)
    max=NumericProperty(0)
    color_1 = NumericProperty(0)
    color_2 = NumericProperty(0)
    color_3 = NumericProperty(0)
    color_4 = NumericProperty(0)
    color = ReferenceListProperty(color_1,color_2,color_3,color_4)

    def __init__(self,type, **kwarg):
        super(Enemy, self).__init__(**kwarg)
        self.type = type
        self.side = choice([-1,1])

        if self.type == 'red':
            while -2<self.velocity_x<2 or -2<self.velocity_y<2:
                self.velocity_x = randint(2, 4)*self.side
                self.velocity_y = randint(-4, 4)
            self.velocity = self.velocity_x, self.velocity_y
            self.enemy_weight = randint(4, 8)
            self.color = 1, 0, 0, 1

        if self.type == 'purple':
            while self.velocity_x == 0 or self.velocity_y == 0:
                self.velocity_x = 1*self.side
                self.velocity_y = randint(-1,1)
            self.velocity = self.velocity_x, self.velocity_y
            self.enemy_weight = randint(15,22)
            self.color= 1,1,0,1

        if self.type == 'blue':
            while self.velocity_y == 0:
                self.velocity_y = 8*randint(-1,1)
            self.velocity_x = 6*self.side
            self.enemy_weight = randint(1,3)
            self.color = 0, 0.2, 1, 1

        self.pos = (5 if self.side == 1 else 450, randint(210, 450))
        self.size = self.enemy_weight * 5 + 20, self.enemy_weight * 5 + 20
        self.pv = self.size[0]
        self.max = self.enemy_weight

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def on_touch(self, touch, feedpower):
        if self.collide_point(*touch.pos):
                self.enemy_weight -= feedpower
                self.pv = (self.enemy_weight/self.max)*self.size[0]



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

    cell_weight = BoundedNumericProperty(100, min=0, max= 200, errorhandler= lambda x: 200 if x >200 else 0)
    cell_size = BoundedNumericProperty(101, min=50, max= 150, errorhandler=lambda x: 150 if x > 150 else 50)

    fade_factor = NumericProperty(0.1)
    fade_list = [0 * k for k in range(100)]

    jauge_pv = NumericProperty(0)

    gold = NumericProperty(0)

    game = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ClickerCell, self).__init__(**kwargs)
        self.size = self.cell_size, self.cell_size

    def add_score(self, amount):
        self.gold += amount

    def hit_treasure(self, amount):
        self.center_y = 25 + 10 + self.game.height * 5/8
        self.game.health.color = [1, 0.8, 0, 1]
        self.add_score(amount)
        self.game.tresor.pos[0] = self.game.width * 3 / 8 - 50
        anim = Animation(x=self.game.tresor.pos[0] + 8, y=self.game.tresor.pos[1], duration=0.2) + Animation(
            x=self.game.tresor.pos[0] - 8, y=self.game.tresor.pos[1], duration=0.2) + Animation(
            x=self.game.tresor.pos[0], y=self.game.tresor.pos[1], duration=0.2)
        anim.start(self.game.tresor)


    def add_weight(self, amount):
        self.cell_weight += amount
        self.cell_size += amount
        self.size = self.cell_size, self.cell_size
        if self.cell_weight < 200:
            self.center = self.game.width*3/8, 25+10+self.game.height*1/8+ (self.cell_weight/200)*self.game.height*4/8
            self.game.health.color = [1,1,1,1]
        if self.cell_weight == 200:
            self.hit_treasure(amount)

    def collide(self, enemy, game):
        if self.collide_widget(enemy):
            self.add_weight(-enemy.max)
            game.remove_widget(enemy)

    def grow(self):
        self.add_weight(self.feedpower)

    def fade(self):
        if self.cell_weight > 0:
            if self.cell_weight - self.fade_factor > 0:
                self.add_weight(-self.fade_factor)
            else:
                self.cell_weight = 1

    def upgrade_feedpower(self):
        if self.cell_weight >= self.feedpower_upgrade_cost:
            self.add_weight(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 1.15)
        else:
            print("Not Enough Weight")

class Tresor(Widget):
    pass

class ClickerGame(Widget):
    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    tresor = ObjectProperty(None)
    auto_tier1 = ObjectProperty(tier=StringProperty("1"))
    auto_tier2 = ObjectProperty(tier=StringProperty("2"))

    timer = NumericProperty(0)
    limit_x, limit_y =  6/8, 1/8

    spikes = ObjectProperty()
    dirt = ObjectProperty()
    bridge = ObjectProperty()

    gameover = StringProperty("")
    count = 0
    phase2 = False

    def __init__(self, **kwargs):
        super(ClickerGame, self).__init__(**kwargs)
        self.spikes = Image(source="Graphics/Spike.png").texture
        self.spikes.wrap = 'repeat'
        self.spikes.uvsize = 10,-1
        self.dirt = Image(source="Graphics/Background.png").texture
        self.dirt.wrap = 'repeat'
        self.dirt.uvsize = 20,20
        self.bridge = Image(source="Graphics/Bridge.png").texture
        self.bridge.wrap = 'repeat'
        self.bridge.uvsize = 7,1

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
        type = ['red','blue','purple']
        self.add_widget(Enemy(choice(type)))


    def bounce(self, enemy):
        if (enemy.pos[1] < self.height * 1 / 8 + 10) or (enemy.top > self.height):
            enemy.velocity_y *= -1
        if (enemy.pos[0] < 0) or (enemy.pos[0] + enemy.size[0] > self.width * 3 / 4):
            enemy.velocity_x *= -1

    def kill_enemy(self, enemy):
        if enemy.type == 'yellow':
            self.add_widget()
        self.remove_widget(enemy)

    def on_touch_down(self, touch):
        for child in self.children:
            if child.__class__.__name__ == "Enemy":
                child.on_touch(touch, self.cell.feedpower)
                if child.enemy_weight <= 0:
                    self.kill_enemy(child)
            else:
                child.on_touch_down(touch)

    def update(self, dt):
        if self.cell.cell_weight == 0:
            self.gameover = "Game Over"
        if self.gameover == "Game Over":
            return

        self.count += 1
        if self.count % 3 == 0:
            self.cell.fade()
        if self.count % 30 == 0:
            self.timer += 1
            if self.timer >= 0:
                self.phase2 = True
            if self.timer in self.cell.fade_list:
                self.cell.fade_factor += self.timer / 5
            if int(self.timer) % 1 == 0:
                self.cell.fade()
            if self.phase2:
                if int(self.timer) % 5 == 0:
                    self.spawn_enemy()
            self.autofeed()

        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)


class ClickerApp(App):
    def build(self):
        self.game = ClickerGame()
        Clock.schedule_interval(self.game.update, 1 / 30)
        return self.game


if __name__ == '__main__':
    ClickerApp().run()