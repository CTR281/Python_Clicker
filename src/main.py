import kivy

kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint


class Enemy(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self,**kwarg):
        super(Enemy, self).__init__(**kwarg)
        self.velocity_x = randint(1,5)
        self.velocity_y = randint(1,5)
        self.velocity = self.velocity_x, self.velocity_y
        self.pos = (5, randint (210,790))
        self.enemy_weight = randint(2,10)
        self.size = self.enemy_weight * 5 + 20, self.enemy_weight * 5 + 20

    def __name__(self):
        return("Enemy")

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def collide(self, cell, game):
        if self.collide_widget(cell):
            cell.cell_weight -= self.enemy_weight
            game.children.remove_widget(self)


class AutoClicker(Widget):
    feed_per_second = NumericProperty(0)
    amount = NumericProperty(0)
    buy_cost = NumericProperty(0)
    cost_increase = NumericProperty(1.2)
    tier = NumericProperty(1)

    def __name__(self):
        return "Autoclicker"

    def autofeed(self):
        return self.feed_per_second * self.amount

    def get_cost(self):
        return self.buy_cost

    def buy_auto(self):
        self.amount += 1
        self.buy_cost = int(self.buy_cost*self.cost_increase)


class ClickerCell(Widget):
    feedpower = NumericProperty(1)
    feedpower_upgrade_cost = NumericProperty(10)

    cell_weight = NumericProperty(101)
    fade_factor = NumericProperty(0)
    fade_list = [15 * k for k in range(100)]

    def __init__(self,**kwargs):
        super(ClickerCell, self).__init__(**kwargs)
        self.size = self.cell_weight, self.cell_weight

    def add_weight(self, amount):
        self.cell_weight += amount
        self.size = self.cell_weight, self.cell_weight
        self.center = self.center_x - amount / 2, self.center_y - amount / 2

    def collide(self, enemy, game):
        if self.collide_widget(enemy):
            self.add_weight(-enemy.enemy_weight)
            game.remove_widget(enemy)

    def grow(self):
        self.add_weight(self.feedpower)
        
        
    def fade(self, game):
        if self.cell_weight > 0:
            if self.cell_weight - self.fade_factor > 0:
                self.add_weight(-self.fade_factor)
            else:
                self.cell_weight = 1
                self.pos = game.width * 3 / 8, game.height * 5 / 8

    def upgrade_feedpower(self):
        if self.cell_weight >= self.feedpower_upgrade_cost:
            self.add_weight(-self.feedpower_upgrade_cost)
            self.feedpower += 1
            self.feedpower_upgrade_cost = int(self.feedpower_upgrade_cost * 1.15)
        else:
            print("Not Enought Weight")

class ClickerGame(Widget):
    cell = ObjectProperty(None)
    feed = ObjectProperty(None)
    auto_tier1 = ObjectProperty(tier=StringProperty("1"))
    auto_tier2 = ObjectProperty(tier=StringProperty("2"))



    timer = NumericProperty(0)
    gameover = StringProperty("")
    enemy_list = []
    count = 0
    phase2 = False

    def autofeed(self):
        self.cell.add_weight(self.auto_tier1.autofeed())
        self.cell.add_weight(self.auto_tier2.autofeed())

    def buy_auto(self, autoclicker):
        if self.cell.cell_weight >= autoclicker.get_cost():
            self.cell.add_weight(-autoclicker.get_cost())
            autoclicker.buy_auto()
        else:
            print("Not Enought weight")

    def spawn_enemy(self):
        # enemy = Enemy()
        # enemy.enemy_weight = randint(2, 10)
        # enemy.pos = 5, randint(210, 400)
        # enemy.velocity = Vector(5, 0).rotate(randint(-90, 90))

        self.add_widget(Enemy())
        # self.enemy_list.append()

    def bounce(self, enemy):
        # bounce off top and bottom
        if (enemy.pos[1] < self.height * 1 / 4) or (enemy.pos[1] + enemy.size[0] > self.height):
            enemy.velocity_y *= -1

        # bounce off left and right
        if (enemy.pos[0] < 0) or (enemy.pos[0] + enemy.size[0] > self.width * 3 / 4):
            enemy.velocity_x *= -1

    def update(self, dt):
        if self.gameover == "Game Over":
            return
        self.count += 1
        if self.count % 30 == 0:
            self.timer += 1
            if self.timer > 0:
                self.phase2 = True
            if self.timer in self.cell.fade_list:
                self.cell.fade_factor += self.timer/5
            if int(self.timer) % 2 == 0:
                self.cell.fade(self)
            if self.phase2:
                if int(self.timer) % 5 == 0:
                    self.spawn_enemy()
            if self.cell.cell_weight == 1:
                self.gameover = "Game Over"

            self.autofeed()

        for enemy in self.children:
            if enemy.__class__.__name__ == "Enemy":
                enemy.move()
                self.cell.collide(enemy, self)
                self.bounce(enemy)

                print(self.cell.pos)
                print(self.cell.size)
                print(enemy.pos)
                print(enemy.size)
                print(self.cell.collide_widget(enemy))
                print("\n")

class ClickerApp(App):
    def build(self):
        self.game = ClickerGame()
        Clock.schedule_interval(self.game.update, 1 / 60)
        return self.game


if __name__ == '__main__':
    ClickerApp().run()
    enemy1 = Enemy()
    enemy2 = Enemy()
    print(enemy1.pos)
    print(enemy2.pos)


