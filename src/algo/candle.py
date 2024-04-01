from enum import Enum


class CandleType(Enum):
    GREEN = 0  # green is rising
    RED = 1


class Candle:
    def __init__(self) -> None:
        pass

    @staticmethod
    def determine_candle_trend(open_price: float, close_price: float) -> CandleType:
        if open_price >= close_price:
            return CandleType.GREEN

        return CandleType.RED
