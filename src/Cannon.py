from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.uix.image import Image
from random import randint

class Cannonball(Widget):

    velocity_x, velocity_y = NumericProperty(0), NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    damage = NumericProperty(25)

    def __init__(self, x_min, x_max, Y_max, Y_min, **kwargs):

        super(Cannonball, self).__init__(**kwargs)

        self.x_min = x_min
        self.x_max = x_max
        self.Y_max = Y_max
        self.Y_min =Y_min
        self.pos = x_min, Y_min
        self.velocity_x = (x_max-x_min)/(4*30)

        #self.x_min = randint(5,50)
        #self.x_max = randint(400,550)
        #self.Y_max = randint (400,600)

    def move(self):
        self.pos[0] += self.velocity_x
        self.pos[1] = ((-4*(self.Y_max))/(self.x_max-self.x_min)**2)*(self.pos[0]-self.x_min)*(self.pos[0]-self.x_max)+self.Y_min

class Cannon(Widget):

    source = StringProperty()
    firing_point_x = NumericProperty(0)
    firing_point_y = NumericProperty(0)
    firing_point = ReferenceListProperty(firing_point_x, firing_point_y)
    type = StringProperty()

    def aim(self, game):
        if game.cell.pos[0] < game.width * 2/8:
            if self.type == 'right_cannon':
                self.source = '../graphics/Cannon/Cannon_1_right.png'
            else:
                self.source = '../graphics/Cannon/Cannon_3_left.png'

        if game.width * 2/8 <= game.cell.pos[0] < game.width * 4/8:
            if self.type == 'right_cannon':
                self.source = '../graphics/Cannon/Cannon_2_right.png'
            else:
                self.source = '../graphics/Cannon/Cannon_2_left.png'

        if  game.width * 4/8 <= game.cell.pos[0] <= game.width * 6/8:
            if self.type == 'right_cannon':
                self.source = '../graphics/Cannon/Cannon_3_right.png'
            else:
                self.source = '../graphics/Cannon/Cannon_1_left.png'

    def fire(self, game):
        if self.type == 'right_cannon':
            self.firing_point_x = self.pos[0]
            self.firing_point_y = game.height * 1 / 8 + 5 + self.size[0]
        if self.type == 'left_cannon':
            self.firing_point_x = self.size[0]
            self.firing_point_y = game.height * 1 / 8 + 5 + self.size[0]




