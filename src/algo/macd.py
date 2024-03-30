import pandas as pd
from algo.algo import Algo, Trend
from talib import abstract

MACD = abstract.MACDEXT

MACD_FAST = 7
MACD_SLOW = 12
MACD_SIGNAL = 9

MACD_THRESHOLD = 0
MACD_TREND_BACK_LENGTH = 1

MA_TYPE_SMA = 0
MA_TYPE_EMA = 1


class Macd(Algo):
    def __init__(self) -> None:
        super().__init__()
        self._macds: pd.DataFrame = {}

    def prepare_macds(self, prices: pd.DataFrame) -> None:
        self._macds = MACD(
            prices,
            fastperiod=MACD_FAST,
            fastmatype=MA_TYPE_SMA,
            slowperiod=MACD_SLOW,
            slowmatype=MA_TYPE_SMA,
            signalperiod=MACD_SIGNAL,
            signalmatype=MA_TYPE_EMA,
        ).iloc[-25:]
        print(self._macds)

    def _calculate_macd(self, prices: pd.DataFrame) -> None:
        new_macds = MACD(prices, fastperiod=MACD_FAST, slowperiod=MACD_SLOW, signalperiod=MACD_SIGNAL).iloc[-1:]
        macd_t = self._macds.T
        macd_t.pop(self._macds.iloc[0].name)
        self._macds = macd_t.T
        self._macds = pd.concat([self._macds, new_macds], axis=0)

    def make_decision(self, prices: pd.DataFrame) -> int:
        self._calculate_macd(prices)
        latest_macd = self._macds.iloc[-1]["macd"]
        old_macd = self._macds.iloc[-1 - MACD_TREND_BACK_LENGTH]["macd"]
        if latest_macd > MACD_THRESHOLD and Algo.determine_trend(old_macd, latest_macd) == Trend.FALLING:
            return -1
        if latest_macd < MACD_THRESHOLD and Algo.determine_trend(old_macd, latest_macd) == Trend.RISING:
            return 1
        return 0
