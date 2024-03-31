import pandas as pd
from algo.algo import Algo, CrossingType
from talib import abstract

MA = abstract.EMA

MA_FAST_MID_THRESHOLD = 1
MA_FAST_SLOW_THRESHOLD = 1

MA_FAST = 4
MA_MID = 7
MA_SLOW = 14


class Ma(Algo):
    def __init__(self) -> None:
        super().__init__()
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

    def reset_counter(self) -> None:
        self._ma_fast_mid_counter = 0
        self._ma_fast_slow_counter = 0

    def check_counter(self) -> None:
        if self._ma_fast_mid_counter > MA_FAST_MID_THRESHOLD or self._ma_fast_slow_counter > MA_FAST_SLOW_THRESHOLD:
            self._ma_fast_mid_counter = 0
            self._ma_fast_slow_counter = 0

    def counter_within_range(self) -> bool:
        return self._ma_fast_mid_counter <= MA_FAST_MID_THRESHOLD and self._ma_fast_slow_counter <= MA_FAST_SLOW_THRESHOLD

    def _calculate_ma(self, prices: pd.DataFrame) -> None:
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

    def _crossing_decision(self) -> int:
        new_indicators = self._ma.iloc[-2:]
        # ma fast crossing mid
        fast_mid_status = Algo.determine_crossing(
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

        # ma fast crossing slow
        fast_slow_status = Algo.determine_crossing(
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

        # ma mid crossing slow
        mid_slow_status = Algo.determine_crossing(
            new_indicators["ma_mid"].iloc[0],
            new_indicators["ma_mid"].iloc[1],
            new_indicators["ma_slow"].iloc[0],
            new_indicators["ma_slow"].iloc[1],
        )
        if self.counter_within_range():
            if (
                mid_slow_status == CrossingType.UP
                and self._ma_fast_mid_status == CrossingType.UP
                and self._ma_fast_slow_status == CrossingType.UP
            ):
                self.reset_counter()
                return 1
            elif (  # noqa: RET505
                mid_slow_status == CrossingType.DOWN
                and self._ma_fast_mid_status == CrossingType.DOWN
                and self._ma_fast_slow_status == CrossingType.DOWN
            ):
                self.reset_counter()
                return -1

        self.check_counter()

        return 0

    def _instant_crossing_decision(self) -> int:
        new_indicators = self._ma.iloc[-2:]
        fast_mid_status = Algo.determine_crossing(
            new_indicators["ma_fast"].iloc[0],
            new_indicators["ma_fast"].iloc[1],
            new_indicators["ma_mid"].iloc[0],
            new_indicators["ma_mid"].iloc[1],
        )
        fast_slow_status = Algo.determine_crossing(
            new_indicators["ma_fast"].iloc[0],
            new_indicators["ma_fast"].iloc[1],
            new_indicators["ma_slow"].iloc[0],
            new_indicators["ma_slow"].iloc[1],
        )
        mid_slow_status = Algo.determine_crossing(
            new_indicators["ma_mid"].iloc[0],
            new_indicators["ma_mid"].iloc[1],
            new_indicators["ma_slow"].iloc[0],
            new_indicators["ma_slow"].iloc[1],
        )
        if fast_mid_status == CrossingType.UP and fast_slow_status == CrossingType.UP and mid_slow_status == CrossingType.UP:
            return 1
        if fast_mid_status == CrossingType.DOWN and fast_slow_status == CrossingType.DOWN and mid_slow_status == CrossingType.DOWN:
            return -1
        return 0

    def _movement_decision(self, prices: pd.DataFrame) -> int:
        latest_ma = self._ma.iloc[-1]
        latest_price = prices.iloc[-1]
        if (
            latest_price["open"] <= latest_ma["ma_fast"]
            and latest_price["close"] >= latest_ma["ma_slow"]
            and latest_ma["ma_fast"] <= latest_ma["ma_slow"]
        ) or (
            latest_price["low"] <= latest_ma["ma_fast"]
            and latest_price["close"] >= latest_ma["ma_slow"]
            and latest_ma["ma_fast"] <= latest_ma["ma_slow"]
            and latest_price["open"] < latest_price["close"]
        ):
            return 1
        if (
            latest_price["open"] >= latest_ma["ma_fast"]
            and latest_price["close"] <= latest_ma["ma_slow"]
            and latest_ma["ma_fast"] >= latest_ma["ma_slow"]
        ) or (
            latest_price["high"] >= latest_ma["ma_fast"]
            and latest_price["close"] <= latest_ma["ma_slow"]
            and latest_ma["ma_fast"] >= latest_ma["ma_slow"]
            and latest_price["open"] > latest_price["close"]
        ):
            return -1
        return 0

    def make_decision(self, prices: pd.DataFrame) -> int:
        self._calculate_ma(prices)
        return self._movement_decision(prices)
