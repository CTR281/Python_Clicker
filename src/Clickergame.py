from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BoundedNumericProperty
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock, ClockBaseBehavior
from kivy.vector import Vector
from functools import partial
from random import randint, choice, random
from math import isclose

from Enemy import Enemy
from Autoclicker import AutoClicker
from Clickercell import ClickerCell
from Treasure import Treasure
from Cannon import Cannon, Cannonball
from Falling_spike import Falling_spike
from Resetdecay import ResetDecay

class ClickerGame(Widget):

    cell = ObjectProperty(None)
    right_cannon = ObjectProperty(None)
    left_cannon = ObjectProperty(None)

    feed = ObjectProperty(None)
    feedpower = NumericProperty(1)
    feedpower_upgrade_cost = NumericProperty(200)

    tresor = ObjectProperty(None)

    resetdecay = ObjectProperty(None)

    #auto_tier1 = ObjectProperty(None)
    #auto_tier2 = ObjectProperty(None)

    fade_factor_Lvl1 = NumericProperty(0.1/3.0)
    fade_factor_Lvl2 = NumericProperty(0.2/3.0)
    fade_factor_Lvl3 = NumericProperty(0.3/3.0)
    fade_factor_Lvlmax = NumericProperty(1.0/3.0)
    fade_factor = 0.1/3.0

    fade_factor_list = {"Lvl1": 0.1/3.0 , "Lvl2": 0.2/3.0, "Lvl3": 0.3/3.0, "Lvlmax": 1/3.0}#NumericProperty(0.1/3.0)
    fade_timer_list = {"Lvl1": 0, "Lvl2": 20, "Lvl3": 40, "Lvlmax": 60, "Timer": 0, "Counter": 0}
    fade_jauge = NumericProperty(0)
    fade_jauge_color = NumericProperty(0)

    fade_timer_Lvl1 = NumericProperty(fade_timer_list['Lvl1']/fade_timer_list['Lvlmax'])
    fade_timer_Lvl2 = NumericProperty(fade_timer_list['Lvl2']/fade_timer_list['Lvlmax'])
    fade_timer_Lvl3 = NumericProperty(fade_timer_list['Lvl3']/fade_timer_list['Lvlmax'])

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

    enemy_red={"Class":"Enemy","Type":'red',"Tmin":8,"Tmax":13.6,"Timer":0, "Counter":0}
    enemy_blue={"Class":"Enemy","Type":'blue',"Tmin":30,"Tmax":40.6, "Timer":0, "Counter":0}
    enemy_yellow={"Class":"Enemy","Type":'yellow',"Tmin":40, "Tmax":50.6, "Timer":0, "Counter":0}
    cannon = {"Class":"Cannonball","Type":'cannon',"Tmin":12, "Tmax":18.6, "Timer":0, "Counter":0}
    falling_spike = {"Class":"Falling_spike","Type":'spike',"Tmin":3, "Tmax":8.6, "Timer":0, "Counter":0}

    enemy_type={'red':enemy_red, 'blue':enemy_blue, 'yellow':enemy_yellow,'cannon': cannon, 'spike': falling_spike}


    spawn_list = ['red']

    def __init__(self, **kwargs):
        super(ClickerGame, self).__init__(**kwargs)
        self.spikes = Image(source="../Graphics/Spike.png").texture
        self.spikes.wrap = 'repeat'
        self.spikes.uvsize = 10,-1
        self.dirt = Image(source="../Graphics/Background.png").texture
        self.dirt.wrap = 'repeat'
        self.dirt.uvsize = 25,25
        self.bridge = Image(source="../Graphics/Bridge.png").texture
        self.bridge.wrap = 'repeat'
        self.bridge.uvsize = 7,1

        self.spike_pos_autorise = [(16*36)*k/16 for k in range(17)]
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def add_gold(self,amount):
        self.gold += amount

    def add_weight(self, amount):
        self.cell.add_weight(amount)
        if self.cell.cell_weight < 100:
            self.cell.center = self.cell.center_x - amount / 2, 25+30+self.height * 1 / 8+ (self.cell.cell_weight/100)*self.height*4/8
            self.health.color = [1,1,1,1]
        if self.cell.cell_weight == 100 and self.tresor.center_x - 50 < self.cell.center_x < self.tresor.center_x + 50:
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

    def buy_resetdecay(self,resetdecay):
        if self.gold >= resetdecay.get_cost():
            self.add_gold(-resetdecay.get_cost())
            resetdecay.buy_reset(self)

   # def buy_auto(self, autoclicker):
   #     if self.cell.cell_weight >= autoclicker.get_cost():
   #         self.add_weight(-autoclicker.get_cost())
   #         autoclicker.buy_auto()
   #     else:
   #         print("Not Enought weight")

    def cannon_shoot(self):                         #decide which cannon shoots
        if self.cell.pos[0] < self.width * 3 / 8:
            return self.right_cannon
        else:
            return self.left_cannon

    def fade(self):                                 #ce qui fait que la plateforme descend
        self.add_weight(-self.fade_factor)

    def hit_treasure(self, amount):                 #permet de gagner de l'or et anime le coffre à l'écran
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
        if enemy.__class__.__name__ == "Enemy":
            if enemy.type == 'yellow':
                center = enemy.center
                self.spawn_enemy('red', center)
                self.spawn_enemy('red', center)
                self.spawn_enemy('red', center)
        if enemy.__class__.__name__ == 'Falling_spike':
            self.refresh_spike(enemy, enemy.pos[0])
        if killed == 1:
            self.add_gold(enemy.max*4)
        self.remove_widget(enemy)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.right_cannon.aim(self)
        self.left_cannon.aim(self)
        if keycode[1] == 'q' and self.cell.pos[0] > 0:
            self.cell.center_x -= 15
        elif keycode[1] == 'd' and self.cell.pos[0] + self.cell.size[0] < self.width * self.limit_x:
            self.cell.center_x += 15
        return True

   # def on_key_down(self, key):
   #     if key == 'right':
   #         print("OK")
   #         self.cell.move(1)
   #     if key == 'left':
   #         self.cell.move(-1)

    def on_touch_down(self, touch):
        for child in self.children:
            if child.__class__.__name__ == "Enemy":
                child.on_touch(touch, self.feedpower)
                if child.enemy_weight <= 0:
                    self.kill_enemy(child, 1)
            else:
                child.on_touch_down(touch)

    def spawn_cannonball(self):
        self.right_cannon.fire(self)
        self.left_cannon.fire(self)
        self.add_widget(Cannonball(self.cannon_shoot().firing_point_x, self.cell.pos[0], randint(400,600), self.cannon_shoot().firing_point_y))

    def spawn_spike(self):
        pos = choice(self.spike_pos_autorise)
        self.add_widget(Falling_spike(pos = pos))
        self.spike_pos_autorise.remove(pos)

    def refresh_spike(self, spike, pos, *args):
        if pos not in self.spike_pos_autorise:
            self.spike_pos_autorise.append(pos)
        self.remove_widget(spike)
        return False

    def remove_spike(self,spike):
        if spike.pos[1] < self.height * 1 / 8 + 10:
            spike.pos[1]+=5
            Clock.schedule_once(partial(self.refresh_spike, spike, spike.pos[0]), 5)
            spike.fallen = True


    def spawn_enemy(self,type, center):
        self.add_widget(Enemy(type, center = center))

    def upgrade_feedpower(self):
        if self.gold >= self.feedpower_upgrade_cost and self.feedpower < 3:
            self.add_gold(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 4)
        elif self.gold < self.feedpower_upgrade_cost:
            print("Not Enough Gold")
        elif self.feedpower == 3:
            print("Max Upgrade Reached")

    def update_time(self):
        self.counter += 1
        if self.fade_timer_list["Timer"] < self.fade_timer_list["Lvlmax"]:
            self.fade_timer_list["Counter"]+=1
        for key in self.spawn_list:
            self.enemy_type[key]['Counter'] += 1
        if self.counter % 60 == 0:
            self.timer +=1
            if self.fade_timer_list["Timer"] < self.fade_timer_list["Lvlmax"]:
                self.fade_timer_list["Timer"]+=1
            for key in self.spawn_list:
                self.enemy_type[key]['Timer'] += 1

    def update_phase(self):
        if self.timer % 60 == 0 and self.counter % 60 == 0:
            self.phase += 1

    def load_phase(self, phase=1):   #update Tmin, Tmax, spawn_list, fade_factor_list, fade_timer_list
        self.phase = phase
        if self.phase == 1:
            self.spawn_list = ['red', 'cannon']# 'spike']

        elif self.phase == 2:
            self.spawn_list.append('blue')
            #self.enemy_type['red']['Tmin']= 5
            #self.enemy_type['red']['Tmax']= 8.6
            self.fade_timer_list = {"Lvl1":0, "Lvl2": 15, "Lvl3": 35, "Lvlmax":55, "Timer": 0, "Counter": 0}
            self.fade_factor_list = {"Lvl1": 0.2 / 3.0, "Lvl2": 0.3 / 3.0, "Lvl3": 0.4 / 3.0, "Lvlmax": 2 / 3.0}
            self.fade_timer_Lvl1 = self.fade_timer_list['Lvl1'] / self.fade_timer_list['Lvlmax']
            self.fade_timer_Lvl2 = self.fade_timer_list['Lvl2'] / self.fade_timer_list['Lvlmax']
            self.fade_timer_Lvl3 = self.fade_timer_list['Lvl3'] / self.fade_timer_list['Lvlmax']

        elif self.phase == 3:
            self.spawn_list.append('yellow')
            #self.enemy_type['red']['Tmin'] = 3
            #self.enemy_type['red']['Tmax'] = 6.6
            #self.enemy_type['blue']['Tmin'] = 15
            #self.enemy_type['blue']['Tmax'] = 25.6
            self.fade_timer_list = {"Lvl1": 0, "Lvl2": 12, "Lvl3": 25, "Lvlmax": 50, "Timer": 0, "Counter": 0}
            self.fade_factor_list = {"Lvl1": 0.3 / 3.0, "Lvl2": 0.4 / 3.0, "Lvl3": 0.5 / 3.0, "Lvlmax": 3 / 3.0}

        elif self.phase == 4:
            self.spawn_list = ['red', 'cannon', 'spike']
            self.enemy_type['red']['Tmin'] = 5.1
            self.enemy_type['red']['Tmax'] = 8.6
            self.cannon['Tmin'] = 4
            self.cannon['Tmax'] = 7.6
            self.fade_timer_list = {"Lvl1": 0, "Lvl2": 10, "Lvl3": 20, "Lvlmax": 30, "Timer": 0, "Counter": 0}

        elif self.phase == 5:
            self.spawn_list.append('blue')
            self.enemy_type['blue']['Tmin'] = 15
            self.enemy_type['blue']['Tmax'] = 25.6

        elif self.phase == 6:
            self.spawn_list.append('yellow')
            self.enemy_type['yellow']['Tmin'] = 25
            self.enemy_type['yellow']['Tmax'] = 35.6

        elif self.phase == 7:

         self.spawn_list = ['cannon', 'spike']
         self.cannon['Tmin'] = 0.5
         self.cannon['Tmax'] = 1.5
         self.falling_spike['Tmin'] = 0.5
         self.falling_spike['Tmax'] = 1.5

         self.fade_timer_list = {"Lvl1": 1, "Lvl2": 1, "Lvl3": 1, "Lvlmax": 1, "Timer": 1, "Counter": 60}
         self.fade_factor_list = {"Lvl1": 0, "Lvl2": 0, "Lvl3": 0, "Lvlmax": 0}

    # elif self.phase == 7:
       #     #self.enemy_type['red']['Tmin'] = 3
       #     #self.enemy_type['red']['Tmax'] = 6.6
       #     #self.enemy_type['blue']['Tmin'] = 8
       #     #self.enemy_type['blue']['Tmax'] = 18.6
       #     self.enemy_type['yellow']['Tmin'] = 25
       #     self.enemy_type['yellow']['Tmax'] = 35.6
       #     self.fade_timer_list = {"Lvl1": 0, "Lvl2": 15, "Lvl3": 30, "Lvlmax": 45, "Timer": 0, "Counter": 0}
       #     self.fade_factor_list = {"Lvl1": 0.3 / 3.0, "Lvl2": 0.4 / 3.0, "Lvl3": 0.5 / 3.0, "Lvlmax": 1 / 3.0}

    def on_phase(self, instance, value):
        for enemy in self.children:
            if enemy.__class__.__name__ == 'Enemy':
                self.remove_widget(enemy)
        self.load_phase(self.phase)

    def will_spawn(self,enemy_type):  #Espérance: <t>=Tmin + 0.7*(Tmax-Tmin)**(5/6)
        if enemy_type['Timer'] > enemy_type['Tmin']:
            f=(enemy_type['Counter']/(60*(enemy_type['Tmax']-enemy_type['Tmin'])))**5
            r=random()
            if r<f:
                if enemy_type['Class'] == "Enemy":
                    self.spawn_enemy(enemy_type['Type'], center = None)
                if enemy_type['Class'] == "Cannonball":
                    self.spawn_cannonball()
                if enemy_type['Class'] == "Falling_spike":
                    self.spawn_spike()
                enemy_type['Timer'] = 0
                enemy_type ['Counter'] = 0

    def update_enemy(self):
        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)
            if enemy.__class__.__name__ == "Cannonball":
                enemy.move()
                self.cell.collide(enemy, self)
                if enemy.pos[1] < self.height * 1/8 - 10:
                    self.remove_widget(enemy)
            if enemy.__class__.__name__ == "Falling_spike":
                enemy.move(enemy.fallen)
                self.cell.collide(enemy, self)
                self.remove_spike(enemy)
        for key in self.spawn_list:
            self.enemy_type[key]['Counter'] += 1
            self.will_spawn(self.enemy_type[key])

    def update_cell(self):
        self.fade()
        #if self.counter % 60 == 0:
        #    self.autofeed()

    def update_fade(self):
        self.fade_jauge = (self.fade_timer_list["Counter"]/(self.fade_timer_list["Lvlmax"]*60))*self.height* 1 / 2
        self.fade_jauge_color =(self.fade_timer_list["Counter"]/(self.fade_timer_list["Lvlmax"]*60))*0.8
        if self.fade_timer_list["Lvl1"] <= self.fade_timer_list["Timer"] < self.fade_timer_list["Lvl2"]:
            self.fade_factor = self.fade_factor_list["Lvl1"]
        elif self.fade_timer_list["Lvl2"] <= self.fade_timer_list["Timer"] < self.fade_timer_list["Lvl3"]:
            self.fade_factor = self.fade_factor_list["Lvl2"]
        elif self.fade_timer_list["Lvl3"] <= self.fade_timer_list["Timer"] < self.fade_timer_list["Lvlmax"]:
            self.fade_factor = self.fade_factor_list["Lvl3"]
        elif self.fade_timer_list["Timer"] == self.fade_timer_list["Lvlmax"]:
            self.fade_factor = self.fade_factor_list["Lvlmax"]

    def update(self, dt):
        self.is_gameover()
        self.update_phase()
        self.update_enemy()
        self.update_cell()
        self.update_fade()
        self.update_time()





    #    self.count += 1
    #    self.fade()
    #    for key in self.enemy_type.keys():
    #        self.enemy_type[key]['Counter']+=1
    #        self.will_spawn(self.enemy_type[key])
       # if self.count % 60 == 0:
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
