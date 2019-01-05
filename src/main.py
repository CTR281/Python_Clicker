import kivy
kivy.require('1.10.1') 

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint

class ClickerCell(Widget):
    weight = NumericProperty(100)
    fade_factor =  2
    growth_factor = 1
    fade_list = [15,30,45,60,75,90]
    dead=""
    
    def grow(self):
        self.weight += self.growth_factor
        self.center = self.center_x- self.growth_factor/2, self.center_y - self.growth_factor/2
        print(self.center_x, self.center_y)


    def fade(self):
        if self.weight > 0:
            if self.weight-self.fade_factor > 0:
                self.weight -= self.fade_factor
                self.center = self.center_x + self.fade_factor/2, self.center_y + self.fade_factor/2
            else:
                self.weight = 0
            

class ClickerGame(Widget):

    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    timer = NumericProperty(0)

    def update(self, dt):
        self.timer += 1
        if self.timer in self.cell.fade_list:
            self.cell.fade_factor +=1
        if self.timer % 2 == 0:
            self.cell.fade()
        if self.cell.weight == 0:
            self.cell.dead="Game Over"
        print(self.cell.weight)
        print(self.cell.dead)
        print(self.cell.center)
        


class ClickerApp(App):
    def build(self):
        self.game= ClickerGame()
        self.game.feed.bind(on_press=self.grow)
        Clock.schedule_interval(self.game.update, int(1))
        return self.game

    def grow(self, obj):
        self.game.cell.grow()
        


        

if __name__ == '__main__':
    ClickerApp().run()