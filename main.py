
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line
from random import randint
from math import hypot

class BattleGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = [0.5, 0.25]
        self.enemies = []
        self.bullets = []
        self.health = 100
        self.score = 0
        self.direction = [0, 0]
        self.shooting = False
        self.game_over = False
        self.bind(size=self.draw, pos=self.draw)

        Clock.schedule_interval(self.update, 1 / 30)
        Clock.schedule_once(self.start_game, 0.5)

    def start_game(self, dt):
        for i in range(5):
            self.enemies.append([
                randint(10, 90) / 100,
                randint(60, 95) / 100
            ])
        self.draw()

    def move(self, x, y):
        self.direction = [x, y]

    def fire(self, *args):
        if not self.game_over:
            px, py = self.player
            if self.enemies:
                target = min(
                    self.enemies,
                    key=lambda e: hypot(e[0]-px, e[1]-py)
                )
                dx, dy = target[0]-px, target[1]-py
                distance = max(hypot(dx, dy), 0.001)
                self.bullets.append([
                    px, py, dx/distance, dy/distance
                ])

    def update(self, dt):
        if self.game_over or self.width <= 0:
            return

        px, py = self.player
        px += self.direction[0] * dt * 0.45
        py += self.direction[1] * dt * 0.45

        self.player = [
            max(0.05, min(0.95, px)),
            max(0.05, min(0.95, py))
        ]

        for bullet in self.bullets[:]:
            bullet[0] += bullet[2] * dt * 1.1
            bullet[1] += bullet[3] * dt * 1.1

            hit = None
            for enemy in self.enemies:
                if hypot(
                    bullet[0]-enemy[0],
                    bullet[1]-enemy[1]
                ) < 0.055:
                    hit = enemy
                    break

            if hit:
                self.enemies.remove(hit)
                self.bullets.remove(bullet)
                self.score += 10

                if len(self.enemies) < 5:
                    self.enemies.append([
                        randint(5, 95) / 100,
                        randint(60, 95) / 100
                    ])

            elif not (0 <= bullet[0] <= 1 and
                      0 <= bullet[1] <= 1):
                self.bullets.remove(bullet)

        for enemy in self.enemies:
            dx = self.player[0] - enemy[0]
            dy = self.player[1] - enemy[1]
            distance = max(hypot(dx, dy), 0.001)

            if distance > 0.07:
                enemy[0] += dx/distance * dt * 0.06
                enemy[1] += dy/distance * dt * 0.06
            else:
                self.health -= 15 * dt

        if self.health <= 0:
            self.health = 0
            self.game_over = True

        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        w, h = self.width, self.height
        if w <= 0 or h <= 0:
            return

        with self.canvas:
            Color(0.15, 0.38, 0.18)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.28, 0.30, 0.28)
            Rectangle(pos=(w*.08, 0), size=(w*.84, h))

            Color(0.7, 0.7, 0.7)
            for y in range(0, int(h), 70):
                Line(points=[w*.5, y, w*.5, y+30], width=1)

            # Enemies
            for ex, ey in self.enemies:
                Color(0.95, 0.12, 0.10)
                Ellipse(
                    pos=(ex*w-18, ey*h-18),
                    size=(36, 36)
                )

            # Bullets
            for bx, by, dx, dy in self.bullets:
                Color(1, 0.9, 0.1)
                Ellipse(
                    pos=(bx*w-5, by*h-5),
                    size=(10, 10)
                )

            # Player
            px, py = self.player
            Color(0.1, 0.55, 1)
            Rectangle(
                pos=(px*w-17, py*h-17),
                size=(34, 34)
            )

            # Crosshair
            Color(1, 1, 1)
            Line(
                points=[w*.5-10, h*.5, w*.5+10, h*.5],
                width=1
            )
            Line(
                points=[w*.5, h*.5-10, w*.5, h*.5+10],
                width=1
            )

class BattleApp(App):
    def build(self):
        root = FloatLayout()
        self.game = BattleGame(size_hint=(1, 1))
        root.add_widget(self.game)

        self.info = Label(
            text="BATTLE ARENA",
            size_hint=(0.8, 0.08),
            pos_hint={"x": 0.1, "top": 1},
            font_size=20
        )
        root.add_widget(self.info)

        Clock.schedule_interval(self.update_info, 0.2)

        controls = [
            ("LEFT", 0.02, 0.02, -1, 0),
            ("RIGHT", 0.23, 0.02, 1, 0),
            ("UP", 0.12, 0.12, 0, 1),
            ("DOWN", 0.12, 0.02, 0, -1)
        ]

        for text, x, y, dx, dy in controls:
            btn = Button(
                text=text,
                size_hint=(0.19, 0.09),
                pos_hint={"x": x, "y": y}
            )
            btn.bind(
                on_press=lambda b, a=dx, c=dy:
                self.game.move(a, c)
            )
            btn.bind(
                on_release=lambda b: self.game.move(0, 0)
            )
            root.add_widget(btn)

        fire = Button(
            text="FIRE 🔫",
            size_hint=(0.25, 0.14),
            pos_hint={"right": 0.98, "y": 0.04},
            background_color=(0.85, 0.12, 0.1, 1)
        )
        fire.bind(on_press=self.game.fire)
        root.add_widget(fire)

        restart = Button(
            text="RESTART",
            size_hint=(0.23, 0.08),
            pos_hint={"right": 0.98, "top": 0.98}
        )
        restart.bind(on_press=self.restart)
        root.add_widget(restart)

        return root

    def update_info(self, dt):
        self.info.text = (
            f"❤️ HP: {int(self.game.health)}"
            f"     🏆 Score: {self.game.score}"
            f"     Enemies: {len(self.game.enemies)}"
        )
        if self.game.game_over:
            self.info.text += "   GAME OVER!"

    def restart(self, *args):
        self.game.player = [0.5, 0.25]
        self.game.enemies = []
        self.game.bullets = []
        self.game.health = 100
        self.game.score = 0
        self.game.game_over = False
        self.game.start_game(0)

if __name__ == "__main__":
    BattleApp().run()
