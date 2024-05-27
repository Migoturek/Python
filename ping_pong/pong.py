from socket import socket
from threading import Thread

import pygame
import sys
import socket
import time

from ball import Ball
from game_state import GameState
from player import Player

pygame.init()
pygame.mixer.init()
pygame.font.init()

Clock = pygame.time.Clock()
screen = pygame.display.set_mode((700, 500))

font1 = pygame.font.Font('font.ttf', 80)
font2 = pygame.font.Font('font.ttf', 80)
font3 = pygame.font.Font('font.ttf', 35)

working = True

#HOST = "127.0.0.1"  # The server's hostname or IP address
HOST = "192.168.0.xxxx"  # The server's hostname or IP address
PORT = 8888  # The port used by the server
sock: socket = None
message: str = None
result: str = None
ready_timer = 0

left_player = Player('Wojtek', screen, True)
right_player = Player('Marcin', screen, False)
ball = Ball(screen, left_player, right_player)

game_state: GameState = GameState.HOME


def core_work():
    global working, sock, game_state, message, result, ready_timer
    try:
        while working:
            if (
                    game_state is GameState.WAITING or game_state is GameState.RUNNING or game_state is GameState.SET) and sock is not None:
                datas = sock.recv(1024).decode('utf-8')
                print(datas)
                if not datas:
                    break
                datas = datas.split(";")
                for data in datas:
                    if data.startswith("ready"):
                        ready_timer = int(data[6:])
                        message = "Ready: " + str(ready_timer)
                    elif data == "resign":
                        ready_timer = int(100)
                        message = "The opponent has given up the game"
                        game_state = GameState.RESIGN
                    elif data == "go":
                        game_state = GameState.RUNNING
                        print("running")
                    elif data.startswith("posy"):
                        try:
                            posy = int(data[5:])
                            right_player.set_posy(posy)
                        except ValueError:
                            pass
                    elif data.startswith("ball"):
                        try:
                            pos = data.split()
                            posx = int(pos[1])
                            posy = int(pos[2])
                            ball.move_ball(posx, posy)
                        except ValueError:
                            pass
                    elif data.startswith("set"):
                        try:
                            left_player.start_position()
                            right_player.start_position()
                            pos = data.split()
                            left = int(pos[1])
                            right = int(pos[2])
                            ready_timer = int(pos[3])
                            result = "Result: " + str(left) + " - " + str(right)
                            message = "Next round ready: " + str(ready_timer)
                        except ValueError:
                            left = 0
                            right = 0
                            ready_timer = 0
                            result = "Result: " + str(left) + " - " + str(right)
                            message = "Next round ready: " + str(ready_timer)
                        game_state = GameState.SET
                        print("set")
                    elif data.startswith("gameover"):
                        try:
                            pos = data.split()
                            res = int(pos[1])
                            left = int(pos[2])
                            right = int(pos[3])
                            if res == 1:
                                result = "You won: " + str(left) + " - " + str(right)
                            else:
                                result = "You lost: " + str(left) + " - " + str(right)
                            message = "Press space to continue"
                        except ValueError:
                            res = 0
                            left = 0
                            right = 0
                            result = "Error: " + str(left) + " - " + str(right)
                            message = "Press space to continue"
                        game_state = GameState.GAME_OVER
                        print("gameover")
            else:
                time.sleep(10 / 1000)
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        sock.close()


core_thread = Thread(target=core_work)
core_thread.start()


def draw_net():
    net = []
    j = 0
    for i in range(0, 50):
        element = pygame.Rect(350, 2 + j, 7, 12)
        net.append(element)
        j += 22

    for element in net:
        pygame.draw.rect(screen, 'white', element)


def connect():
    global game_state, sock, message
    try:
        game_state = GameState.HOME
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(10)
        sock.connect((HOST, PORT))
        sock.sendall(b"hello;")
        data = sock.recv(1024).decode('utf-8')
        if data == "hello;":
            game_state = GameState.WAITING
            message = "Waiting for the opponent"
        elif data == "busy;":
            message = "Server is busy. Please try later."
        else:
            message = "Server return: " + data
    except ConnectionRefusedError:
        print("connection refused")
        message = "Connection refused"
        game_state = GameState.HOME
    except (ConnectionResetError, ConnectionAbortedError):
        print("connection reset")
        message = "Connection reset"
        game_state = GameState.HOME
    except TimeoutError:
        print("timeout")
        message = "Connection timeout. Try again."
        game_state = GameState.HOME
    except socket.error:
        print("timeout")
        message = "Connection timeout. Try again."
        game_state = GameState.HOME

def home_page():
    screen.fill('black')
    press_space = font3.render("Enter server IP address and press enter", False, (0, 255, 0))
    press_space_rect = press_space.get_rect()
    press_space_rect.center = (350, 150)
    screen.blit(press_space, press_space_rect)
    ip_field = font2.render(HOST, False, (0, 0, 255))
    ip_field_rect = ip_field.get_rect()
    ip_field_rect.center = (350, 230)
    screen.blit(ip_field, ip_field_rect)
    message_field = font3.render(message, False, (255, 0, 0))
    message_field_rect = message_field.get_rect()
    message_field_rect.center = (350, 300)
    screen.blit(message_field, message_field_rect)


def set_page():
    screen.fill('black')
    result_field = font1.render(result, False, (0, 255, 0))
    result_field_rect = result_field.get_rect()
    result_field_rect.center = (350, 150)
    screen.blit(result_field, result_field_rect)
    message_field = font3.render(message, False, (255, 0, 0))
    message_field_rect = message_field.get_rect()
    message_field_rect.center = (350, 300)
    screen.blit(message_field, message_field_rect)


def game_over_page():
    screen.fill('black')
    result_field = font1.render(result, False, (0, 255, 0))
    result_field_rect = result_field.get_rect()
    result_field_rect.center = (350, 150)
    screen.blit(result_field, result_field_rect)
    message_field = font3.render(message, False, (255, 0, 0))
    message_field_rect = message_field.get_rect()
    message_field_rect.center = (350, 300)
    screen.blit(message_field, message_field_rect)


while working:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            try:
                if sock is not None:
                    if game_state is not GameState.GAME_OVER:
                        sock.sendall(b"bye;")
                        sock.close()
                working = False
                Clock.tick(60)
                sys.exit()
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                working = False
                Clock.tick(60)
                sys.exit()

    if game_state is GameState.HOME:
        home_page()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    message = "Connection is in progress"
                    pygame.display.update()
                    connect()
                elif pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    HOST = HOST[:-1]
                elif pygame.key.get_pressed()[pygame.K_PERIOD]:
                    HOST = HOST + "."
                elif event.unicode.isdigit():
                    HOST = HOST + event.unicode
                elif pygame.K_a <= event.key <= pygame.K_z:
                    HOST = HOST + event.unicode
        pygame.display.update()
        Clock.tick(60)
    elif game_state is GameState.WAITING:
        home_page()
        pygame.display.update()
        Clock.tick(60)
    elif game_state is GameState.RESIGN:
        home_page()
        ready_timer -= 1
        if ready_timer <= 0:
            message = "Waiting for the opponent"
            game_state = GameState.WAITING
        pygame.display.update()
        Clock.tick(60)
    elif game_state is GameState.RUNNING:

        if pygame.key.get_pressed()[pygame.K_UP]:
            left_player.move_up(sock)
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            left_player.move_down(sock)

        screen.fill('black')
        draw_net()
        left_player.draw_player()
        right_player.draw_player()
        ball.draw_ball()
        pygame.display.update()
        Clock.tick(60)
    elif game_state is GameState.SET:
        set_page()
        pygame.display.update()
        Clock.tick(60)
    elif game_state is GameState.GAME_OVER:
        game_over_page()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    left_player.points = 0
                    right_player.points = 0
                    ball.ball.x = 350
                    ball.ball.y = 350
                    result = ""
                    message = ""
                    game_state = GameState.HOME
        pygame.display.update()
        Clock.tick(60)
        pygame.display.update()
        Clock.tick(60)
    else:
        Clock.tick(60)
