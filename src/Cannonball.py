from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from random import randint

class Cannonball(Widget):

    velocity_x, velocity_y = NumericProperty(0), NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):

        super(Cannonball, self).__init__(**kwargs)

        self.velocity_x = randint(3,7)
        self.x_min = randint(5,50)
        self.x_max = randint(400,550)
        self.Y_max = randint (400,600)

    def move(self):
        self.pos[0] += self.velocity_x
        self.pos[1] = ((-4*(self.Y_max))/(self.x_max-self.x_min)**2)*(self.pos[0]-self.x_min)*(self.pos[0]-self.x_max)

        
