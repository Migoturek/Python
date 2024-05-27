import random
import pygame


class Ball:

    def __init__(self, screen, left_player, right_player):
        self.screen = screen
        self.left_player = left_player
        self.right_player = right_player
        pass

    size = 20
    ball = pygame.Rect(350, 200, size, size)

    def draw_ball(self):
        pygame.draw.rect(self.screen, (0, 255, 0), self.ball)

    def move_ball(self, x, y):
        self.ball.x = x
        self.ball.y = y

    def start_position(self):
        self.ball.x = 350
        self.ball.y = 200
