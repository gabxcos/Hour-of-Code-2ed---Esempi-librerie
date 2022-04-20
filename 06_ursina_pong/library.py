# cheatsheet: https://www.ursinaengine.org/cheat_sheet_dark.html

from ursina import *

# COSTANTI
LEFT = 0
RIGHT = 1
TOP = 2
BOTTOM = 4

# CLASSI

class Paddle(Entity):
    def __init__(self, side=LEFT):
        super().__init__(scale=(1/32,6/32), model='quad', origin_x=.5, collider='box', speed=1)
        if side==LEFT:
            self.x = -.75
            self.rotation_z = 0
        elif side==RIGHT:
            self.x = .75
            self.rotation_z = 180


class Wall(Entity):
    def __init__(self, side=LEFT):
        super().__init__(model="quad", origin_y=.5, collider="box", scale=(2,10), visible=False)
        if side==BOTTOM:
            self.y = -.5
        if side==TOP:
            self.y = .5
            self.rotation_z = 180
        if side==LEFT:
            self.x = -.5 * window.aspect_ratio
            self.rotation_z = 90
        if side==RIGHT:
            self.x = .5 * window.aspect_ratio
            self.rotation_z = -90


class Ball(Entity):
    def __init__(self):
        super().__init__(model='circle', scale=.05, collider='box', speed=0, collision_cooldown=.15)

