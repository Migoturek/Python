import time
import pygame


class Player:

    def __init__(self, name, screen, left):
        self.name = name
        self.screen = screen
        self.left = left
        self.player_velocity = 5
        if left:
            self.player = pygame.Rect(10, 250, 10, 50)
        else:
            self.player = pygame.Rect(680, 250, 10, 50)

    player = pygame.Rect(10, 250, 10, 50)

    def start_position(self):
        self.player.y = 250

    def draw_player(self):
        pygame.draw.rect(self.screen, 'white', self.player)

    def move_up(self, sock):
        if self.player.top > 0:
            self.player.y -= self.player_velocity
            if sock is not None:
                sock.sendall(("posy " + str(self.player.y) + ";").encode())

    def move_down(self, sock):
        if self.player.bottom < 500:
            self.player.y += self.player_velocity
            if sock is not None:
                sock.sendall(("posy " + str(self.player.y) + ";").encode())

    def set_posy(self, posy):
        self.player.y = posy
