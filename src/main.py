import kivy
kivy.require('1.10.1') 

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint


class Enemy(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    enemy_weight=randint(2,10)
    enemy_size=50,50

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def collide(self,cell,game):
        if self.collide_widget(cell):
            cell.weight -= self.weight
            game.remove_widget(self)


class AutoClicker(Widget):
    feed_per_second = NumericProperty(0)
    amount = NumericProperty(0)
    buy_cost = NumericProperty(0)
    tier = NumericProperty(0)

    def __init__(self, tier, **kwargs):
        super(AutoClicker, self).__init__(**kwargs)
        self.tier = tier
    def autofeed(self):
        return self.feed_per_second * self.amount


class ClickerCell(Widget):
    cell_weight = NumericProperty(101)
    fade_factor =  50
    growth_factor = 1
    fade_list = [15*k for k in range(100)]
    cell_size=ReferenceListProperty(cell_weight,cell_weight)

    
    def grow(self):
        self.cell_weight += self.growth_factor
        self.center = self.center_x - self.growth_factor/2, self.center_y - self.growth_factor/2



    def fade(self,game):
        if self.cell_weight > 0:
            if self.cell_weight-self.fade_factor > 0:
                self.cell_weight -= self.fade_factor
                self.center = self.center_x + self.fade_factor/2, self.center_y + self.fade_factor/2
            else:
                self.cell_weight = 1
                self.pos= game.width * 3 / 8, game.height * 5 / 8

    def autofeed(self, autoclicker):
        self.cell_weight += autoclicker.autofeed()
            

class ClickerGame(Widget):

    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    auto_tier1 = AutoClicker(1)
    timer = NumericProperty(0)
    gameover=""
    enemy_list = []
    phase2 = False

    def spawn_enemy(self):
        enemy = Enemy()
        self.add_widget(enemy)
        return enemy


    def update(self, dt):
        self.timer += 1
        if self.timer > 5:
            self.phase2= True
        if self.timer in self.cell.fade_list:
            self.cell.fade_factor +=1
        if self.timer % 2 == 0:
            self.cell.fade(self)
        if self.phase2:
            if self.timer % 5 == 0:
                enemy=self.spawn_enemy()
                self.enemy_list.append(enemy)
            for enemy in self.enemy_list:
                enemy.collide(self.cell, self)
                enemy.move()
        if self.cell.cell_weight == 1:
            self.gameover="Game Over"

        self.cell.autofeed(self.auto_tier1)
        
        print(self.cell.cell_weight == 1)
        print(self.gameover)
        #print(self.cell.center)


class ClickerApp(App):
    def build(self):
        self.game= ClickerGame()
        Clock.schedule_interval(self.game.update, int(1))
        return self.game


if __name__ == '__main__':
    ClickerApp().run()