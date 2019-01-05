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
    
    def grow(self):
        self.weight +=1
        self.center = self.center_x- 0.5, self.center_y - 0.5
        print(self.center_x, self.center_y)


    def fade(self):
        if self.weight > 0:
            self.weight -=7
            self.center = self.center_x+ 3.5, self.center_y + 3.5
            

class ClickerGame(Widget):
    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    timer = NumericProperty(0)
    def update(self, dt):
        if self.timer % 2 == 0:
            self.cell.fade()
        self.timer += 1


class ClickerApp(App):
    def build(self):
        self.game= ClickerGame()
        self.game.feed.bind(on_press=self.grow)
        Clock.schedule_interval(self.game.update, 1)
        return self.game

    def grow(self, obj):
        self.game.cell.grow()
        


        

if __name__ == '__main__':
    ClickerApp().run()