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
    velocity_x = NumericProperty(4)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    enemy_weight = randint(2, 10)
    # enemy_weight_prop = NumericProperty(enemy_weight)
    enemy_weight_temp = NumericProperty(enemy_weight * 5 + 20)
    enemy_size = ReferenceListProperty(enemy_weight_temp, enemy_weight_temp)
    pos_x = NumericProperty(5)
    pos_y = NumericProperty(randint(210, 790))
    pos = ReferenceListProperty(pos_x, pos_y)
    size = enemy_size

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
    cost_increase = NumericProperty(1.5)
    tier = NumericProperty(1)

    def autofeed(self):
        return self.feed_per_second * self.amount

    def get_cost(self):
        return self.buy_cost

    def buy_auto(self):
        self.amount += 1
        self.buy_cost += int(self.buy_cost * self.cost_increase)


class ClickerCell(Widget):
    cell_weight = NumericProperty(101)
    fade_factor = NumericProperty(2)
    growth_factor = 1
    fade_list = [15 * k for k in range(100)]
    cell_size = ReferenceListProperty(cell_weight, cell_weight)

    def change_weight(self, amount):
        self.cell_weight += amount
        self.center = self.center_x - amount / 2, self.center_y - amount / 2

    def collide(self, enemy, game):
        if self.collide_widget(enemy):
            self.cell_weight -= self.enemy_weight
            game.children.remove_widget(enemy)

    def grow(self):
        self.cell_weight += self.growth_factor
        self.center = self.center_x - self.growth_factor / 2, self.center_y - self.growth_factor / 2

    def fade(self, game):
        if self.cell_weight > 0:
            if self.cell_weight - self.fade_factor > 0:
                self.cell_weight -= self.fade_factor
                self.center = self.center_x + self.fade_factor / 2, self.center_y + self.fade_factor / 2
            else:
                self.cell_weight = 1
                self.pos = game.width * 3 / 8, game.height * 5 / 8


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
        self.cell.change_weight(self.auto_tier1.autofeed())
        self.cell.change_weight(self.auto_tier2.autofeed())

    def buy_auto(self, autoclicker):
        if self.cell.cell_weight >= autoclicker.get_cost():
            self.cell.change_weight(-autoclicker.get_cost())
            autoclicker.buy_auto()
        else:
            print("Not Enought weight")

    def spawn_enemy(self):
        enemy = Enemy()
        enemy.enemy_weight = randint(2, 10)
        enemy.pos = 5, randint(210, 400)
        enemy.velocity = Vector(5, 0).rotate(randint(-90, 90))

        self.add_widget(enemy)
        self.enemy_list.append(enemy)

    def bounce(self, enemy):
        # bounce off top and bottom
        if (enemy.pos_y < self.height * 1 / 4) or (enemy.pos_y + enemy.enemy_size[0] > self.height):
            enemy.velocity_y *= -1

        # bounce off left and right
        if (enemy.pos_x < 0) or (enemy.pos_x + enemy.enemy_size[0] > self.width * 3 / 4):
            enemy.velocity_x *= -1

    def update(self, dt):
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

        for enemy in self.enemy_list:
            enemy.move()
            self.cell.collide(enemy, self)
            self.bounce(enemy)

            print(self.children)

            print(self.enemy_list)
            #
            print(self.cell)
            #
            print(self.enemy_list[-1].collide_widget(self.cell))
            #
            # print(self.enemy_list[-1].enemy_size[0])
            #
            # print(self.enemy_list[-1].pos)
            #
            # print(self.cell.cell_size[0])
            #
            # print(self.cell.pos)

            # print((self.enemy_list[0].x < 0) or (self.enemy_list[0].right > self.width))

            # print(self.enemy_list[0].x)

            # print(self.enemy_list[0].right)
        # print(int(self.timer*10000)+1)
        # print(int(self.timer+1)*10000)
        # print(self.timer)


class ClickerApp(App):
    def build(self):
        self.game = ClickerGame()
        Clock.schedule_interval(self.game.update, 1 / 30)
        return self.game


if __name__ == '__main__':
    ClickerApp().run()



