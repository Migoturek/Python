from enum import Enum


class GameState(Enum):
    HOME = 1
    WAITING = 2
    RESIGN = 3
    RUNNING = 4
    SET = 5
    GAME_OVER = 6

