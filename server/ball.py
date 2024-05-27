import random
import pygame


class Ball:

    def __init__(self, left_player, right_player):
        self.left_player = left_player
        self.right_player = right_player
        pass

    size = 20
    starting_direction = random.choice([1, 2, 3, 4])
    ball = pygame.Rect(350, 200, size, size)

    velocity_x = 2
    velocity_y = 2

    def start_position(self):
        self.starting_direction = random.choice([1, 2, 3, 4])
        self.ball.x = 350
        self.ball.y = 200
        self.velocity_x = 2
        self.velocity_y = 2

    def move_ball(self):
        if self.starting_direction == 1:
            self.ball.x -= self.velocity_x
            self.ball.y -= self.velocity_y
        if self.starting_direction == 2:
            self.ball.x -= self.velocity_x
            self.ball.y += self.velocity_y
        if self.starting_direction == 3:
            self.ball.x += self.velocity_x
            self.ball.y -= self.velocity_y
        if self.starting_direction == 4:
            self.ball.x += self.velocity_x
            self.ball.y += self.velocity_y
        self.left_player.send("ball " + str(self.ball.x) + " " + str(self.ball.y))
        self.right_player.send("ball " + str(700-self.size-self.ball.x) + " " + str(self.ball.y))
        if self.ball.top <= 0 or self.ball.bottom >= 500:
            self.velocity_y *= -1
        if self.ball.colliderect(self.left_player.player):
            # change direction and speed up
            self.velocity_x *= -1.05
            self.velocity_y *= 1.05
        if self.ball.colliderect(self.right_player.player):
            # change direction and speed up
            self.velocity_x *= -1.05
            self.velocity_y *= 1.05
