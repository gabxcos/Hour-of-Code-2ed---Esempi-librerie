# Appunti:
# - OOP come framework e come libreria
# - OOP per ereditarietà (framework) e per organizzazione (libreria)

# Repo originale: https://github.com/pokepetter/ursina/blob/master/samples/pong.py

from library import *

app = Ursina()


# SETUP campo di gioco e telecamera
window.color = color.black
camera.orthographic = True
camera.fov = 1

info_text = Text("press space to play", y=-.45)


# Players
Player = Paddle(side=LEFT)
Enemy = Paddle(side=RIGHT)

# Le quattro mura
floor = Wall(side=BOTTOM)
ceiling = Wall(side=TOP)
left_wall = Wall(side=LEFT)
right_wall = Wall(side=RIGHT)

# PALLA
ball = Ball()

#-----------------------------------------------------------------------------------

# FUNZIONI FRAMEWORK - UPDATE e INPUT

def update():
    # Aggiorna posizione palla, e cooldown di collisione
    ball.collision_cooldown -= time.dt
    ball.position += ball.right * time.dt * ball.speed

    # Aggiorna posizione players
    Player.y += (held_keys['w'] - held_keys['s']) * time.dt * Player.speed
    Enemy.y += (held_keys['up arrow'] - held_keys['down arrow']) * time.dt * Enemy.speed

    # Attendi cooldown di collisione per la palla
    if ball.collision_cooldown > 0:
        return

    # LOGICA DI COLLISIONE
    hit_info = ball.intersects()
    if hit_info.hit:
        ball.collision_cooldown = .15 # Resetta il timer

        # Giocatori
        if hit_info.entity in (Player, Enemy):
            hit_info.entity.collision = False
            invoke(setattr, hit_info.entity, 'collision', False, delay=.1)
            
            direction_multiplier = 1
            
            if hit_info.entity == Player:
                direction_multiplier = -1

                Player.collision = False # disable collision for the current paddle so it doesn't collide twice in a row
                Enemy.collision = True
            elif hit_info.entity == Enemy:
                Enemy.collision = False
                Player.collision = True

            # Rimbalza
            ball.rotation_z += 180 * direction_multiplier
                # Modifica in base all'angolo dell'oggetto colpito
            ball.rotation_z -= (hit_info.entity.world_y - ball.y) * 20 * 32 * direction_multiplier
                # Aumenta la velocità
            ball.speed *= 1.1

        elif hit_info.entity in (floor, ceiling):   # hit wall
            ball.rotation_z *= -abs(hit_info.world_normal.normalized()[1])

        elif hit_info.entity in (left_wall, right_wall):   # lose
            reset()


def reset():
    ball.position = (0,0,0)
    ball.rotation = (0,0,0)
    ball.speed = 10
    for paddle in (Player, Enemy):
        paddle.collision = True
        paddle.y = 0

def input(key):
    if key == 'space':
        info_text.enabled = False
        reset()

    if key == 't':
        ball.speed += 5

app.run()