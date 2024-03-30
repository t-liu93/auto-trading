from enum import Enum

import pandas as pd


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

    @staticmethod
    def determine_crossing(fast_old: float, fast_new: float, slow_old: float, slow_new: float) -> CrossingType:
        if fast_old <= slow_old and fast_new > slow_new:
            return CrossingType.UP
        if fast_old >= slow_old and fast_new < slow_old:
            return CrossingType.DOWN

        return CrossingType.NO

    @staticmethod
    def determine_trend(old: float, new: float) -> Trend:
        if old < new:
            return Trend.RISING
        if new < old:
            return Trend.FALLING

        return Trend.NO

    def make_decision(self, prices: pd.DataFrame) -> int:
        pass

    def prepare_indicators(self, prices: pd.DataFrame) -> None:
        pass
