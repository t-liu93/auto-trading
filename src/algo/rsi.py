import pandas as pd
from algo.algo import Algo, Trend
from talib import abstract

RSI = abstract.RSI

RSI_TIME_PERIOD = 16

RSI_THRESHOLD = 40
RSI_TREND_BACK_LENGTH = 1


class Rsi(Algo):
    def __init__(self) -> None:
        super().__init__()
        self._rsi: pd.Series = {}

    def prepare_rsis(self, prices: pd.DataFrame) -> None:
        self._rsi = RSI(prices, timeperiod=RSI_TIME_PERIOD).iloc[-25:]

    def _calculate_rsi(self, prices: pd.DataFrame) -> None:
        new_rsi = RSI(prices, timeperiod=RSI_TIME_PERIOD)
        self._rsi = self._rsi.iloc[1:]
        self._rsi[new_rsi.index[-1]] = new_rsi.iloc[-1]

    def make_decision(self, prices: pd.DataFrame) -> int:
        self._calculate_rsi(prices)
        latest_rsi = self._rsi.iloc[-1]
        old_rsi = self._rsi.iloc[-1 - RSI_TREND_BACK_LENGTH]
        threshold_downtrend = RSI_THRESHOLD
        threshold_uptrend = 100 - RSI_THRESHOLD
        if latest_rsi > threshold_downtrend and Algo.determine_trend(old_rsi, latest_rsi) == Trend.FALLING:
            return -1
        if latest_rsi < threshold_uptrend and Algo.determine_trend(old_rsi, latest_rsi) == Trend.RISING:
            return 1
        return 0
