from enum import Enum


class CrossingType(Enum):
    UP = 1
    DOWN = 2
    NO = 3


class Trend(Enum):
    RISING = 1
    FALLING = 2
    NO = 3


# Algo will be saved in each seis. this will holds all data to calculate a trigger.
class Algo:
    def __init__(self) -> None:
        pass
