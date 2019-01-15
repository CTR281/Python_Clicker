from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.image import Image
from random import randint, choice



class Enemy(Image):

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

    def __init__(self,type, pos, **kwarg):
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

        if self.type == 'yellow':
            while self.velocity_x == 0 or self.velocity_y == 0:
                self.velocity_x = 1*self.side
                self.velocity_y = randint(-1,1)
            self.velocity = self.velocity_x, self.velocity_y
            self.enemy_weight = randint(15,22)
            self.color= 1,1,0,1

        if self.type == 'blue':
            while self.velocity_y == 0:
                self.velocity_y = 10*randint(-1,1)
            self.velocity_x = 6*self.side
            self.enemy_weight = randint(1,3)
            self.color = 0, 0.2, 1, 1
        if pos != None:
            self.pos = pos
        else:
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
