from socket import socket
from threading import Thread

import pygame


class Player:

    def __init__(self, sock, addr, left):
        self.sock = sock
        self.addr = addr
        self.left = left
        self.running = True
        if left:
            self.player = pygame.Rect(10, 250, 10, 50)
        else:
            self.player = pygame.Rect(680, 250, 10, 50)
        self.points = 0

    opponent = None
    player = pygame.Rect(10, 250, 10, 50)

    def start_position(self):
        self.player.y = 250

    def set_opponent(self, opponent):
        self.opponent = opponent

    def add_point(self):
        self.points += 1

    def play(self):
        client_thread = Thread(target=self.run)
        client_thread.start()
        self.sock.sendall(b"hello;")

    def stop(self):
        self.running = False
        self.sock.close()

    def send(self, data: str):
        try:
            if self.sock is not None and self.running:
                self.sock.sendall((data + ";").encode())
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            self.sock.close()

    def set_posy(self, posy):
        self.player.y = posy

    def run(self):
        try:
            while self.running:
                datas = self.sock.recv(1024).decode('utf-8')
                if not datas:
                    break
                if datas == '':
                    continue
                datas = datas.split(";")
                for data in datas:
                    if data == "bye":
                        self.running = False
                    if data.startswith("posy"):
                        try:
                            posy = int(data[5:])
                            self.set_posy(posy)
                            if self.opponent is not None:
                                self.opponent.send("posy " + str(posy))
                            else:
                                print("opponent is None")
                        except ValueError:
                            pass
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            self.sock.close()
            self.running = False
