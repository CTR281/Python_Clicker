from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty,NumericProperty
from kivy.clock import Clock



class ClickerCell(Widget):

    cell_weight = BoundedNumericProperty(50, min=0, max= 100, errorhandler= lambda x: 100 if x >100 else 0)
    cell_size = BoundedNumericProperty(101, min=50, max= 150, errorhandler=lambda x: 150 if x > 150 else 50)

    jauge_pv = NumericProperty(0)
    invulnerable = NumericProperty(0)

    color2 = NumericProperty(1)
    color= NumericProperty(1)

    def __init__(self, **kwargs):
        super(ClickerCell, self).__init__(**kwargs)
        self.size = self.cell_size, self.cell_size


    def add_weight(self, amount):
        if self.cell_weight - amount < 0:
            self.cell_weight = 0
        else:
            self.cell_weight += amount
        self.cell_size += amount
        self.size = self.cell_size, self.cell_size


    def collide(self, enemy, game):
        def switch(dt):
            self.invulnerable = 0
            self.color, self.color2 = 1, 1
        if self.invulnerable == 0:
            if self.collide_widget(enemy):
                self.invulnerable = 1
                self.color, self.color2= 0, 0.8
                if enemy.__class__.__name__ == "Enemy":
                    game.add_weight(-enemy.max)
                    if enemy.type != 'blue':
                        game.kill_enemy(enemy, 0)
                if enemy.__class__.__name__ == "Cannonball":
                    game.add_weight(-enemy.damage)
                    game.kill_enemy(enemy, 0)
                Clock.schedule_once(switch, self.invulnerable)

   # def move(self,direction):
   #     self.pos[0] += 1*direction

    def on_invulnerable(self, instance, value):
        pass
