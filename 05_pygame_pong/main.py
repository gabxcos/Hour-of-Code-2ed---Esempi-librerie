import pygame
from pygame.locals import *

import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Paddle():

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.direction = 0

        self.speed = 10

    def getRect(self):
        return Rect(self.x-4, self.y-70, 8, 140)

    def updateDirection(self, direction):
        self.direction = self.direction + direction

    def setDirection(self, direction):
        self.direction = direction

    def move(self):
        self.y = min(720, max(0, self.y + self.speed * self.direction))

class Ball():

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y

        self.dirx, self.diry = direction

        self.speed = 3

    def getRect(self):
        return Rect(self.x-5, self.y-5, 10, 10)

    def bounce(self, bounceX=False, bounceY=False):
        if bounceX:
            self.dirx = self.dirx*(-1)
        if bounceY:
            self.diry = self.diry*(-1)

        self.speed = max(5, self.speed + 0.15)

    def move(self):
        self.x = self.x + self.dirx * self.speed
        self.y = self.y + self.diry * self.speed

class Game():

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.screen = pygame.display.set_mode([1280, 720])

        self.clock = pygame.time.Clock()

        self.running = True

        self.ball = Ball(640, 360, (random.randrange(-1, 2, 2), random.randrange(-1, 2, 2)))

        self.player = Paddle(80, 360)
        self.playerScore = 0

        self.enemy = Paddle(1200, 360)
        self.enemyScore = 0

    def loop(self):

        # Bounding boxes
        ballRect = self.ball.getRect()
        playerRect = self.player.getRect()
        enemyRect = self.enemy.getRect()

        # Player
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.updateDirection(-1)
                if event.key == pygame.K_DOWN:
                    self.player.updateDirection(+1)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.updateDirection(+1)
                if event.key == pygame.K_DOWN:
                    self.player.updateDirection(-1)

        # Ball
        if ballRect.top < 0 or ballRect.bottom > 720:
            self.ball.bounce(bounceY=True)
        #   Bounce player
        if (playerRect.left - 5) < ballRect.left < playerRect.right and playerRect.top < ballRect.top and playerRect.bottom > ballRect.bottom:
            self.ball.bounce(bounceX=True)

        #   Bounce enemy
        if enemyRect.left < ballRect.right < (enemyRect.right + 5) and enemyRect.top < ballRect.top and enemyRect.bottom > ballRect.bottom:
            self.ball.bounce(bounceX=True)

        #   Enemy point
        if ballRect.left < 0:
            self.ball = Ball(640, 360, (1, random.randrange(-1, 2, 2)))
            self.enemyScore += 1

        #   Player point
        if ballRect.right > 1250:
            self.ball = Ball(640, 360, (-1, random.randrange(-1, 2, 2)))
            self.playerScore += 1

        
        # Enemy
        if (ballRect.top - 30) < enemyRect.top and self.enemy.direction != -1:
            self.enemy.setDirection(-1)
        elif (ballRect.bottom + 30) > enemyRect.bottom and self.enemy.direction != +1:
            self.enemy.setDirection(+1)
        elif self.enemy.direction != 0:
            self.enemy.setDirection(0)

        # Move all
        self.enemy.move()
        self.player.move()
        self.ball.move()


    def render(self):
        # Field
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, (634, 0, 10, 720))

        # Scores
        player_score_surface = self.font.render(str(self.playerScore), False, WHITE)
        self.screen.blit(player_score_surface, (100, 20))

        enemy_score_surface = self.font.render(str(self.enemyScore), False, WHITE)
        self.screen.blit(enemy_score_surface, (1180, 20))

        # Ball
        pygame.draw.circle(self.screen, WHITE, (self.ball.x, self.ball.y), 5)

        # Player and Enemy
        pygame.draw.rect(self.screen, WHITE, self.player.getRect())
        pygame.draw.rect(self.screen, WHITE, self.enemy.getRect())

        pygame.display.flip()
        self.clock.tick(60)

    def isRunning(self):
        return self.running

    def quit(self):
        self.running = False



if __name__ == "__main__":

    game = Game()

    while game.isRunning():
        game.loop()
        game.render()