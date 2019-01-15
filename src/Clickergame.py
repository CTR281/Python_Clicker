from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.vector import Vector
from random import randint, choice, random
from math import isclose

from Enemy import Enemy
from Autoclicker import AutoClicker
from Clickercell import ClickerCell
from Treasure import Treasure



class ClickerGame(Widget):

    cell = ObjectProperty(None)

    feed = ObjectProperty(None)
    feedpower = NumericProperty(1)
    feedpower_upgrade_cost = NumericProperty(10)
    tresor = ObjectProperty(None)
    auto_tier1 = ObjectProperty(None)
    auto_tier2 = ObjectProperty(None)
    fade_factor = NumericProperty(0.1/3.0)
    fade_list = [10 * k for k in range(1,10)]
    gold = NumericProperty(0)
    limit_x, limit_y =  6/8, 1/8

    spawn_point_left = NumericProperty(0)
    spawn_point_x_right = NumericProperty(0)
    spawn_point_y_top = NumericProperty(0)
    spawn_point_y_bottom = NumericProperty(0)

    spikes = ObjectProperty()
    dirt = ObjectProperty()
    bridge = ObjectProperty()

    gameover = StringProperty("")
    counter = 0
    timer = NumericProperty(0)
    phase = NumericProperty(0)

    enemy_red={"Type":'red',"Tmin":8,"Tmax":13.6,"Timer":0, "Counter":0}
    enemy_blue={"Type":'blue',"Tmin":30,"Tmax":40.6, "Timer":0, "Counter":0}
    enemy_yellow={"Type":'yellow',"Tmin":40, "Tmax":50.6, "Timer":0, "Counter":0}
    enemy_type={'red':enemy_red, 'blue':enemy_blue, 'yellow':enemy_yellow}

    spawn_list = ['red']

    def __init__(self, **kwargs):
        super(ClickerGame, self).__init__(**kwargs)
        self.spikes = Image(source="../Graphics/Spike.png").texture
        self.spikes.wrap = 'repeat'
        self.spikes.uvsize = 10,-1
        self.dirt = Image(source="../Graphics/Background.png").texture
        self.dirt.wrap = 'repeat'
        self.dirt.uvsize = 20,20
        self.bridge = Image(source="../Graphics/Bridge.png").texture
        self.bridge.wrap = 'repeat'
        self.bridge.uvsize = 7,1


    def add_gold(self,amount):
        self.gold += amount

    def add_weight(self, amount):
        self.cell.add_weight(amount)
        if self.cell.cell_weight < 100:
            self.cell.center = self.cell.center_x - amount / 2, 25+30+self.height*1/8+ (self.cell.cell_weight/100)*self.height*4/8
            self.health.color = [1,1,1,1]
        if self.cell.cell_weight == 100:
            self.health.color = [1, 0.8, 0, 1]
            self.hit_treasure(amount)

    def autofeed(self):
        self.add_weight(self.auto_tier1.autofeed())
        self.add_weight(self.auto_tier2.autofeed())

    def bounce(self, enemy):
        if (enemy.pos[1] < self.height * 1 / 8 + 10) or (enemy.top > self.height):
            enemy.velocity_y *=-1
        if (enemy.pos[0] < 0) or (enemy.pos[0] + enemy.size[0] > self.width * 3 / 4):
            enemy.velocity_x *= -1

    def buy_auto(self, autoclicker):
        if self.cell.cell_weight >= autoclicker.get_cost():
            self.add_weight(-autoclicker.get_cost())
            autoclicker.buy_auto()
        else:
            print("Not Enought weight")

    def fade(self):
        self.add_weight(-self.fade_factor)

    def hit_treasure(self, amount):
        self.add_gold(amount)
        self.tresor.pos[0] = self.width * 3 / 8 - 50
        anim = Animation(x=self.tresor.pos[0] + 8, y=self.tresor.pos[1], duration=0.2) + Animation(
            x=self.tresor.pos[0] - 8, y=self.tresor.pos[1], duration=0.2) + Animation(
            x=self.tresor.pos[0], y=self.tresor.pos[1], duration=0.2)
        anim.start(self.tresor)

    def is_gameover(self):
        if isclose(self.cell.cell_weight, 0, abs_tol = 0.001):
            self.gameover = "Game Over"
            return

    def kill_enemy(self, enemy, killed):
        if enemy.type == 'yellow':
            center = enemy.center
            self.spawn_enemy('red', center)
            self.spawn_enemy('red',center)
            self.spawn_enemy('red',center)
        if killed == 1:
            self.add_gold(enemy.max)
        self.remove_widget(enemy)

    def on_touch_down(self, touch):
        for child in self.children:
            if child.__class__.__name__ == "Enemy":
                child.on_touch(touch, self.feedpower)
                if child.enemy_weight <= 0:
                    self.kill_enemy(child, 1)
            else:
                child.on_touch_down(touch)

    def spawn_enemy(self,type, center):
        self.add_widget(Enemy(type, center = center))

    def upgrade_feedpower(self):
        if self.cell.cell_weight >= self.feedpower_upgrade_cost:
            self.add_weight(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 1.15)
        else:
            print("Not Enough Weight")

    def will_spawn(self,enemy_type):
        if enemy_type['Timer'] > enemy_type['Tmin']:
            f=(enemy_type['Counter']/(30*(enemy_type['Tmax']-enemy_type['Tmin'])))**5
            r=random()
            if r<f:
                self.spawn_enemy(enemy_type['Type'], center = None)
                enemy_type['Timer']=0
                enemy_type['Counter']=0

    def update_time(self):
        self.counter += 1
        if self.counter % 30 == 0:
            self.timer +=1
            for key in self.enemy_type.keys():
                self.enemy_type[key]['Timer'] += 1

    def update_phase(self):
        if self.timer % 60 == 0 and self.counter % 30 == 0:
            self.phase += 1

    def load_phase(self):   #update Tmin, Tmax, spawn_list, fade_factor,
        if self.phase == 1:
            self.spawn_list = ['red']

        if self.phase == 2:
            self.spawn_list = ['red', 'blue']
            self.enemy_type['red']['Tmin']= 5
            self.enemy_type['red']['Tmax']= 8.6
            self.fade_factor = 0.2/3

        if self.phase == 3:
            self.spawn_list = ['red', 'blue', 'yellow']
            self.enemy_type['red']['Tmin'] = 3
            self.enemy_type['red']['Tmax'] = 6.6
            self.enemy_type['blue']['Tmin'] = 15
            self.enemy_type['blue']['Tmax'] = 25.6
            self.fade_factor = 0.3/3

        if self.phase == 4:
            self.enemy_type['red']['Tmin'] = 3
            self.enemy_type['red']['Tmax'] = 6.6
            self.enemy_type['blue']['Tmin'] = 8
            self.enemy_type['blue']['Tmax'] = 18.6
            self.enemy_type['yellow']['Tmin'] = 25
            self.enemy_type['yellow']['Tmax'] = 35.6
            self.fade_factor = 0.4 / 3


    def on_phase(self, instance, value):
        self.load_phase()

    def update_enemy(self):
        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)
        for key in self.spawn_list:
            self.enemy_type[key]['Counter'] += 1
            self.will_spawn(self.enemy_type[key])

    def update_cell(self):
        self.fade()
        if self.counter % 30 == 0:
            self.autofeed()

    def update(self, dt):
        self.is_gameover()
        self.update_phase()
        self.update_enemy()
        self.update_cell()
        self.update_time()

    #    self.count += 1
    #    self.fade()
    #    for key in self.enemy_type.keys():
    #        self.enemy_type[key]['Counter']+=1
    #        self.will_spawn(self.enemy_type[key])
       # if self.count % 30 == 0:
       #     self.timer += 1
      #      for key in self.enemy_type.keys():
      #          self.enemy_type[key]['Timer'] += 1
      #      if self.timer >= 0:
      #          self.phase2 = True
      #       if self.timer in self.fade_list:
      #          self.fade_factor += 0.1
       #     self.autofeed()

     #   for enemy in self.children:
     #       if enemy.__class__.__name__ == "Enemy":
     #           enemy.move()
     #           self.cell.collide(enemy, self)
     #           self.bounce(enemy)
