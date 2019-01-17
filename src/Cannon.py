from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.image import Image
from random import randint

class Cannonball(Widget):

    velocity_x, velocity_y = NumericProperty(0), NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    damage = NumericProperty(25)

    def __init__(self, x_min, x_max, Y_max, **kwargs):

        super(Cannonball, self).__init__(**kwargs)

        self.x_min = x_min
        self.x_max = x_max
        self.Y_max = Y_max
        self.pos = x_min, 0
        if self.x_min == 5:
            self.side = 1
        else:
            self.side = -1
        self.velocity_x = 3*self.side

        #self.x_min = randint(5,50)
        #self.x_max = randint(400,550)
        #self.Y_max = randint (400,600)

    def move(self):
        self.pos[0] += self.velocity_x
        self.pos[1] = ((-4*(self.Y_max))/(self.x_max-self.x_min)**2)*(self.pos[0]-self.x_min)*(self.pos[0]-self.x_max)

class Cannon(Image):


