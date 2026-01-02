from dataclasses import dataclass, field
from enum import Enum


class TablePosition(Enum):
    GAMEMASTER = 0  # Table end by game shelf
    WALL_1 = 1  # along the wall by the gamemaster
    WALL_2 = 2  # along the wall by the window
    WINDOW = 3  # table end by the windows
    ROOM_1 = 4  # back to the room by the gamemaster
    ROOM_2 = 5  # back to the room by the window
    NO_SEAT = 99
