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
from random import randint, choice, random
from math import *

from Clickergame import ClickerGame



class ClickerApp(App):
    def build(self):
        self.game = ClickerGame()
        Clock.schedule_interval(self.game.update, 1 / 60)
        return self.game


if __name__ == '__main__':
    ClickerApp().run()