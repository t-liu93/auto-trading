from datetime import datetime, timezone

import pandas as pd
from algo.algo import Algo, CrossingType, Trend
from talib import abstract

MA = abstract.EMA

MA_FAST_MID_THRESHOLD = 2
MA_FAST_SLOW_THRESHOLD = 2

MA_FAST = 4
MA_MID = 7
MA_SLOW = 14


class Ma(Algo):
    def __init__(self) -> None:
        Algo.__init__(self)
        self._ma: pd.DataFrame
        self._ma_fast_mid_counter: int = 0
        self._ma_fast_mid_status: CrossingType = CrossingType.NO
        self._ma_fast_slow_counter: int = 0
        self._ma_fast_slow_status: CrossingType = CrossingType.NO

    @property
    def ma(self) -> pd.DataFrame:
        return self._ma

    def prepare_mas(self, prices: pd.DataFrame) -> str:
        ma_fast = MA(prices, MA_FAST)
        ma_mid = MA(prices, MA_MID)
        ma_slow = MA(prices, MA_SLOW)
        # get the latest 25 bars to store
        new_index = prices.index.to_numpy()[-25:]
        new_data = {"ma_fast": ma_fast.iloc[-25:], "ma_mid": ma_mid.iloc[-25:], "ma_slow": ma_slow.iloc[-25:]}
        self._ma = pd.DataFrame(data=new_data, index=new_index)

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
        if self._ma_fast_mid_counter > MA_FAST_MID_THRESHOLD or self._ma_fast_slow_counter > MA_FAST_SLOW_THRESHOLD:
            self._ma_fast_mid_counter = 0
            self._ma_fast_slow_counter = 0

    def counter_within_range(self) -> bool:
        return self._ma_fast_mid_counter <= MA_FAST_MID_THRESHOLD and self._ma_fast_slow_counter <= MA_FAST_SLOW_THRESHOLD

    def calculate_ma(self, prices: pd.DataFrame) -> None:
        new_ma_fast = MA(prices, MA_FAST)
        new_ma_mid = MA(prices, MA_MID)
        new_ma_slow = MA(prices, MA_SLOW)
        new_df = pd.DataFrame(
            data={"ma_fast": new_ma_fast.iloc[-1], "ma_mid": new_ma_mid.iloc[-1], "ma_slow": new_ma_slow.iloc[-1]},
            index=[new_ma_fast.index[-1]],
        )
        ma_t = self._ma.T
        ma_t.pop(self._ma.iloc[0].name)
        self._ma = ma_t.T
        self._ma = pd.concat([self._ma, new_df], axis=0)

    def ma_decision(self, prices: pd.DataFrame) -> str:
        self.calculate_ma(prices)
        new_indicators = self._ma.iloc[-2:]
        print(datetime.now(tz=timezone.utc))
        # ma fast crossing mid
        fast_mid_status = Ma.determine_crossing(
            new_indicators["ma_fast"].iloc[0],
            new_indicators["ma_fast"].iloc[1],
            new_indicators["ma_mid"].iloc[0],
            new_indicators["ma_mid"].iloc[1],
        )
        if fast_mid_status == CrossingType.NO:
            self._ma_fast_mid_counter += 1
        elif fast_mid_status != self._ma_fast_mid_status:
            self._ma_fast_mid_status = fast_mid_status
            self._ma_fast_mid_counter = 1
        print("fast-mid", fast_mid_status, self._ma_fast_mid_status, self._ma_fast_mid_counter)

        # ma fast crossing slow
        fast_slow_status = Ma.determine_crossing(
            new_indicators["ma_fast"].iloc[0],
            new_indicators["ma_fast"].iloc[1],
            new_indicators["ma_slow"].iloc[0],
            new_indicators["ma_slow"].iloc[1],
        )
        if fast_slow_status == CrossingType.NO:
            self._ma_fast_slow_counter += 1
        elif fast_slow_status != self._ma_fast_slow_status:
            self._ma_fast_slow_status = fast_slow_status
            self._ma_fast_slow_counter = 1
        print("fast-slow", fast_slow_status, self._ma_fast_slow_status, self._ma_fast_slow_counter)

        # ma mid crossing slow
        mid_slow_status = Ma.determine_crossing(
            new_indicators["ma_mid"].iloc[0],
            new_indicators["ma_mid"].iloc[1],
            new_indicators["ma_slow"].iloc[0],
            new_indicators["ma_slow"].iloc[1],
        )
        print("mid-slow", mid_slow_status)
        if self.counter_within_range():
            if (
                mid_slow_status == CrossingType.UP
                and self._ma_fast_mid_status == CrossingType.UP
                and self._ma_fast_slow_status == CrossingType.UP
            ):
                return "BULL"
            elif (  # noqa: RET505
                mid_slow_status == CrossingType.DOWN
                and self._ma_fast_mid_status == CrossingType.DOWN
                and self._ma_fast_slow_status == CrossingType.DOWN
            ):
                return "BEAR"

        self.reset_counter()

        return "NA"
