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
    fade_factor = NumericProperty(0.1)
    fade_list = [10 * k for k in range(1,10)]
    timer = NumericProperty(0)
    gold = NumericProperty(0)
    limit_x, limit_y =  6/8, 1/8

    spikes = ObjectProperty()
    dirt = ObjectProperty()
    bridge = ObjectProperty()

    gameover = StringProperty("")
    count = 0
    phase2 = False

    enemy_red={"Type":'red',"Tmin":8,"Tmax":13.6,"Timer":0, "Counter":0} # type,Tmin, Tmax, Timer
    enemy_blue={"Type":'blue',"Tmin":30,"Tmax":40.6, "Timer":0, "Counter":0}
    enemy_yellow={"Type":'yellow',"Tmin":40, "Tmax":50.6, "Timer":0, "Counter":0}
    enemy_type={'red':enemy_red, 'blue':enemy_blue, 'yellow':enemy_yellow}

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
            self.cell.center_y = 25 + 30 + self.height * 5 / 8
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

    def isgameover(self):
        if isclose(self.cell.cell_weight, 0, abs_tol = 0.001):
            self.gameover = "Game Over"

    def is_spawn(self,enemy_type):
        if enemy_type['Timer'] > enemy_type['Tmin']:
            f=(enemy_type['Counter']/(30*(enemy_type['Tmax']-enemy_type['Tmin'])))**5
            r=random()
            if r<f:
                self.spawn_enemy(enemy_type['Type'], pos = None)
                enemy_type['Timer']=0
                enemy_type['Counter']=0

    def kill_enemy(self, enemy):
        if enemy.type == 'yellow':
            pos = enemy.pos
            self.spawn_enemy('red', pos)
            self.spawn_enemy('red',pos)
            self.spawn_enemy('red',pos)
        self.add_gold(enemy.max)
        self.remove_widget(enemy)

    def on_touch_down(self, touch):
        for child in self.children:
            if child.__class__.__name__ == "Enemy":
                child.on_touch(touch, self.feedpower)
                if child.enemy_weight <= 0:
                    self.kill_enemy(child)
            else:
                child.on_touch_down(touch)

    def spawn_enemy(self,type, pos):
        self.add_widget(Enemy(type, pos = pos))

    def upgrade_feedpower(self):
        if self.cell.cell_weight >= self.feedpower_upgrade_cost:
            self.add_weight(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 1.15)
        else:
            print("Not Enough Weight")

    def update(self, dt):
        print(self.cell.cell_weight)
        self.isgameover()
        if self.gameover == "Game Over":
            return

        self.count += 1
        for key in self.enemy_type.keys():
            self.enemy_type[key]['Counter']+=1
            self.is_spawn(self.enemy_type[key])

        if self.count % 3 == 0:
            self.fade()
        if self.count % 30 == 0:
            self.timer += 1
            for key in self.enemy_type.keys():
                self.enemy_type[key]['Timer'] += 1
            if self.timer >= 0:
                self.phase2 = True
            if self.timer in self.fade_list:
                self.fade_factor += 0.1
          #  if self.phase2:
          #     if int(self.timer) % 5 == 0:
          #          self.spawn_enemy('yellow', pos = None)
            self.autofeed()

        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)
