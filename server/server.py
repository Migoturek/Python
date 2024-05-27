import socket
import sys

import time
from threading import Thread

from ball import Ball
from game_state import GameState
from player import Player

game_state = GameState.WAITING
ready_timer = 3

core_thread: Thread = None
left_player: Player = None
right_player: Player = None
ball: Ball = None


def core_work():

    global game_state, left_player, right_player, ball, ready_timer

    while True:

        if left_player is not None and not left_player.running:
            if right_player is not None:
                right_player.send("resign")
            left_player = None
        if right_player is not None and not right_player.running:
            if left_player is not None:
                left_player.send("resign")
            right_player = None

        if left_player is None or right_player is None:
            game_state = GameState.WAITING

        if game_state is GameState.WAITING:
            time.sleep(0.1)
            continue

        if game_state is GameState.READY:
            if ready_timer > 0:
                left_player.send("ready " + str(ready_timer))
                right_player.send("ready " + str(ready_timer))
                time.sleep(1)
                ready_timer = ready_timer - 1
                continue
            if ready_timer <= 0:
                game_state = GameState.RUNNING
                right_player.set_opponent(left_player)
                left_player.set_opponent(right_player)
                left_player.send("go")
                right_player.send("go")
                ball = Ball(left_player, right_player)
                ball.start_position()
                continue

        if game_state is GameState.RUNNING:
            ball.move_ball()
            # check win
            if ball.ball.right >= 700:
                left_player.add_point()
                ball.start_position()
                if left_player.points == 5:
                    game_state = GameState.WAITING
                    left_player.send("gameover 1 " + str(left_player.points) + " " + str(right_player.points))
                    right_player.send("gameover 0 " + str(right_player.points) + " " + str(left_player.points))
                    time.sleep(0.1)
                    left_player.stop()
                    right_player.stop()
                else:
                    game_state = GameState.SET
                    ready_timer = 3
                continue
            if ball.ball.left <= 0:
                right_player.add_point()
                ball.start_position()
                if right_player.points == 5:
                    game_state = GameState.WAITING
                    left_player.send("gameover 0 " + str(left_player.points) + " " + str(right_player.points))
                    right_player.send("gameover 1 " + str(right_player.points) + " " + str(left_player.points))
                    time.sleep(0.1)
                    left_player.stop()
                    right_player.stop()
                else:
                    game_state = GameState.SET
                    ready_timer = 3
                continue
            #
            time.sleep(20 / 1000)
            continue

        if game_state is GameState.SET:
            if ready_timer > 0:
                left_player.send("set " + str(left_player.points) + " " + str(right_player.points) + " " + str(ready_timer))
                right_player.send("set " + str(right_player.points) + " " + str(left_player.points) + " " + str(ready_timer))
                left_player.start_position()
                right_player.start_position()
                time.sleep(1)
                ready_timer = ready_timer - 1
                continue
            if ready_timer <= 0:
                game_state = GameState.RUNNING
                right_player.set_opponent(left_player)
                left_player.set_opponent(right_player)
                left_player.send("go")
                right_player.send("go")
                ball = Ball(left_player, right_player)
                ball.start_position()
                continue

        time.sleep(50 / 1000)


def main():
    global game_state, ready_timer, core_thread, left_player, right_player

    core_thread = Thread(target=core_work, args=())
    core_thread.start()

    host = '0.0.0.0'  # allow any incoming connections
    port = 8888
    s = socket.socket()
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.bind((host, port))  # bind the socket to the port and ip address

    s.listen(5)  # wait for new connections

    while True:
        try:
            sock, addr = s.accept()  # Establish connection with client.
            print(f"New connection from: {addr}")
            if left_player is None:
                left_player = Player(sock, addr, True)
                left_player.play()
            elif right_player is None:
                right_player = Player(sock, addr, False)
                right_player.play()
            else:
                sock.sendall(b"busy;")
                sock.close()
            if left_player is not None and right_player is not None:
                game_state = GameState.READY
                ready_timer = 3
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            sys.exit()
            pass


if __name__ == '__main__':
    main()
