import pandas as pd
from algo.algo import Algo, CrossingType, Trend
from talib import abstract

SMA = abstract.SMA

SMA_FAST_MID_THRESHOLD = 5
SMA_FAST_SLOW_THRESHOLD = 2

SMA_FAST = 4
SMA_MID = 7
SMA_SLOW = 12


class Sma(Algo):
    def __init__(self) -> None:
        Algo.__init__(self)
        self._sma: pd.DataFrame
        self._sma_fast_mid_counter: int = 0
        self._sma_fast_mid_status: CrossingType = CrossingType.NO
        self._sma_fast_slow_counter: int = 0
        self._sma_fast_slow_status: CrossingType = CrossingType.NO

    @property
    def sma(self) -> pd.DataFrame:
        return self._sma

    def prepare_smas(self, prices: pd.DataFrame) -> str:
        sma_fast = SMA(prices, SMA_FAST)
        sma_mid = SMA(prices, SMA_MID)
        sma_slow = SMA(prices, SMA_SLOW)
        # get the latest 25 bars to store
        new_index = prices.index.to_numpy()[-25:]
        new_data = {"sma_fast": sma_fast.iloc[-25:], "sma_mid": sma_mid.iloc[-25:], "sma_slow": sma_slow.iloc[-25:]}
        self._sma = pd.DataFrame(data=new_data, index=new_index)

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

    def reset_counter(self) -> None:
        if self._sma_fast_mid_counter > SMA_FAST_MID_THRESHOLD or self._sma_fast_slow_counter > SMA_FAST_SLOW_THRESHOLD:
            self._sma_fast_mid_counter = 0
            self._sma_fast_slow_counter = 0

    def counter_within_range(self) -> bool:
        return self._sma_fast_mid_counter <= SMA_FAST_MID_THRESHOLD and self._sma_fast_slow_counter <= SMA_FAST_SLOW_THRESHOLD

    def calculate_sma(self, prices: pd.DataFrame) -> None:
        new_sma_fast = SMA(prices, SMA_FAST)
        new_sma_mid = SMA(prices, SMA_MID)
        new_sma_slow = SMA(prices, SMA_SLOW)
        new_df = pd.DataFrame(
            data={"sma_fast": new_sma_fast.iloc[-1], "sma_mid": new_sma_mid.iloc[-1], "sma_slow": new_sma_slow.iloc[-1]},
            index=[new_sma_fast.index[-1]],
        )
        sma_t = self._sma.T
        sma_t.pop(self._sma.iloc[0].name)
        self._sma = sma_t.T
        self._sma = pd.concat([self._sma, new_df], axis=0)

    def sma_decision(self, prices: pd.DataFrame) -> str:
        self.calculate_sma(prices)
        new_indicators = self._sma.iloc[-2:]
        # sma fast crossing mid
        fast_mid_status = Sma.determine_crossing(
            new_indicators["sma_fast"].iloc[0],
            new_indicators["sma_fast"].iloc[1],
            new_indicators["sma_mid"].iloc[0],
            new_indicators["sma_mid"].iloc[1],
        )
        if fast_mid_status == CrossingType.NO:
            self._sma_fast_mid_counter += 1
        elif fast_mid_status != self._sma_fast_mid_status:
            self._sma_fast_mid_status = fast_mid_status
            self._sma_fast_mid_counter = 1
        print(fast_mid_status, self._sma_fast_mid_status, self._sma_fast_mid_counter)

        # sma fast crossing slow
        fast_slow_status = Sma.determine_crossing(
            new_indicators["sma_fast"].iloc[0],
            new_indicators["sma_fast"].iloc[1],
            new_indicators["sma_slow"].iloc[0],
            new_indicators["sma_slow"].iloc[1],
        )
        if fast_slow_status == CrossingType.NO:
            self._sma_fast_slow_counter += 1
        elif fast_slow_status != self._sma_fast_slow_status:
            self._sma_fast_slow_status = fast_slow_status
            self._sma_fast_slow_counter = 1
        print(fast_slow_status, self._sma_fast_slow_status, self._sma_fast_slow_counter)

        # sma mid crossing slow
        mid_slow_status = Sma.determine_crossing(
            new_indicators["sma_mid"].iloc[0],
            new_indicators["sma_mid"].iloc[1],
            new_indicators["sma_slow"].iloc[0],
            new_indicators["sma_slow"].iloc[1],
        )
        print(mid_slow_status)
        if self.counter_within_range():
            if (
                mid_slow_status == CrossingType.UP
                and self._sma_fast_mid_status == CrossingType.UP
                and self._sma_fast_slow_status == CrossingType.UP
            ):
                return "BULL"
            elif (  # noqa: RET505
                mid_slow_status == CrossingType.DOWN
                and self._sma_fast_mid_status == CrossingType.DOWN
                and self._sma_fast_slow_status == CrossingType.DOWN
            ):
                return "BEAR"

        self.reset_counter()

        return "NA"
