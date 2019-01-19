from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from random import randint


class Falling_spike(Widget):

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    damage = NumericProperty(10)

    def __init__(self, pos, **kwargs):
        super(Falling_spike, self).__init__(**kwargs)

        self.pos = pos, 600
        self.size = 37,105
        self.velocity_y = -randint(3,6)
        self.fallen = False

    def move(self, fallen):
        if not fallen:
            self.pos = Vector(*self.velocity) + self.pos