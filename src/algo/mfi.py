import pandas as pd
from algo.algo import Algo, Trend
from talib import abstract

MFI = abstract.MFI

MFI_TIME_PERIOD = 20

MFI_THRESHOLD = 60
MFI_TREND_BACK_LENGTH = 1


class Mfi(Algo):
    def __init__(self) -> None:
        super().__init__()
        self._mfi: pd.Series = {}

    def prepare_mfis(self, prices: pd.DataFrame) -> None:
        self._mfi = MFI(prices, timeperiod=MFI_TIME_PERIOD).iloc[-25:]

    def _calculate_mfi(self, prices: pd.DataFrame) -> None:
        new_mfi = MFI(prices, timeperiod=MFI_TIME_PERIOD)
        self._mfi = self._mfi.iloc[1:]
        self._mfi[new_mfi.index[-1]] = new_mfi.iloc[-1]

    def make_decision(self, prices: pd.DataFrame) -> int:
        self._calculate_mfi(prices)
        latest_mfi = self._mfi.iloc[-1]
        old_mfi = self._mfi.iloc[-1 - MFI_TREND_BACK_LENGTH]
        threshold_downtrend = MFI_THRESHOLD
        threshold_uptrend = 100 - MFI_THRESHOLD
        if latest_mfi > threshold_downtrend and Algo.determine_trend(old_mfi, latest_mfi) == Trend.FALLING:
            return -1
        if latest_mfi < threshold_uptrend and Algo.determine_trend(old_mfi, latest_mfi) == Trend.RISING:
            return 1
        return 0
