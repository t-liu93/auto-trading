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

MA_TYPE = MA_TYPE_SMA


class Macd(Algo):
    def __init__(self) -> None:
        super().__init__()
        self._macds: dict[str, pd.DataFrame] = {}

    def prepare_macds(self, prices: pd.DataFrame) -> None:
        self._macds["sma"] = MACD(
            prices,
            fastperiod=MACD_FAST,
            fastmatype=MA_TYPE_SMA,
            slowperiod=MACD_SLOW,
            slowmatype=MA_TYPE_SMA,
            signalperiod=MACD_SIGNAL,
            signalmatype=MA_TYPE_SMA,
        ).iloc[-25:]
        self._macds["ema"] = MACD(
            prices,
            fastperiod=MACD_FAST,
            fastmatype=MA_TYPE_EMA,
            slowperiod=MACD_SLOW,
            slowmatype=MA_TYPE_EMA,
            signalperiod=MACD_SIGNAL,
            signalmatype=MA_TYPE_EMA,
        ).iloc[-25:]

    def _calculate_macd(self, prices: pd.DataFrame) -> None:
        new_macds_sma = MACD(
            prices,
            fastperiod=MACD_FAST,
            fastmatype=MA_TYPE_SMA,
            slowperiod=MACD_SLOW,
            slowmatype=MA_TYPE_SMA,
            signalperiod=MACD_SIGNAL,
            signalmatype=MA_TYPE_SMA,
        ).iloc[-1:]
        new_macds_ema = MACD(
            prices,
            fastperiod=MACD_FAST,
            fastmatype=MA_TYPE_EMA,
            slowperiod=MACD_SLOW,
            slowmatype=MA_TYPE_EMA,
            signalperiod=MACD_SIGNAL,
            signalmatype=MA_TYPE_EMA,
        ).iloc[-1:]
        macd_sma_t = self._macds["sma"].T
        macd_sma_t.pop(self._macds["sma"].iloc[0].name)
        macd_ema_t = self._macds["ema"].T
        macd_ema_t.pop(self._macds["ema"].iloc[0].name)
        self._macds["sma"] = macd_sma_t.T
        self._macds["ema"] = macd_ema_t.T
        self._macds["sma"] = pd.concat([self._macds["sma"], new_macds_sma], axis=0)
        self._macds["ema"] = pd.concat([self._macds["ema"], new_macds_ema], axis=0)

    def make_decision(self, prices: pd.DataFrame) -> int:
        self._calculate_macd(prices)
        latest_macd_sma = self._macds["sma"].iloc[-1]["macd"]
        latest_macd_ema = self._macds["ema"].iloc[-1]["macd"]
        old_macd_sma = self._macds["sma"].iloc[-1 - MACD_TREND_BACK_LENGTH]["macd"]
        old_macd_ema = self._macds["ema"].iloc[-1 - MACD_TREND_BACK_LENGTH]["macd"]
        if (latest_macd_sma > MACD_THRESHOLD and Algo.determine_trend(old_macd_sma, latest_macd_sma) == Trend.FALLING) or (
            latest_macd_ema > MACD_THRESHOLD and Algo.determine_trend(old_macd_ema, latest_macd_ema == Trend.FALLING)
        ):
            return -1
        if (latest_macd_sma < MACD_THRESHOLD and Algo.determine_trend(old_macd_sma, latest_macd_sma) == Trend.RISING) or (
            latest_macd_ema < MACD_THRESHOLD and Algo.determine_trend(old_macd_ema, latest_macd_ema == Trend.RISING)
        ):
            return 1
        return 0
