from algo.Algo import Algo, CrossingType
from talib import abstract
import pandas as pd

SMA = abstract.SMA

SMA_4_7_THRESHOLD = 6
SMA_4_20_THRESHOLD = 4

class Sma(Algo):
    def __init__(self):
        Algo.__init__(self)
        self._sma: pd.DataFrame
        self._sma_4_7_up_counter: int = 0
        self._sma_4_7_down_counter: int = 0
        self._sma_4_20_up_counter: int = 0
        self._sma_4_20_down_counter: int = 0
        self._sma_7_20_up_counter: int = 0
        self._sma_7_20_down_counter: int = 0

    @property
    def sma(self) -> pd.DataFrame:
        return self._sma

    def prepare_smas(self, prices: pd.DataFrame) -> str:
        sma_4 = SMA(prices, 4)
        sma_7 = SMA(prices, 7)
        sma_20 = SMA(prices, 20)
        indicators: dict[str: pd.DataFrame] = {}
        # get the latest 25 bars to store
        new_index = prices.index.values[-25:]
        new_data = {'sma_4': sma_4.iloc[-25:], 'sma_7': sma_7.iloc[-25:], 'sma_20': sma_20.iloc[-25:]}
        self._sma = pd.DataFrame(data=new_data, index=new_index)

    @staticmethod
    def compare_crossing(fast_old: float, fast_new: float, slow_old: float, slow_new: float) -> CrossingType:
        if fast_old <= slow_old and fast_new > slow_new:
            return CrossingType.UP
        if fast_old >= slow_old and fast_new < slow_old:
            return CrossingType.DOWN

    def calculate_sma(self, prices: pd.DataFrame):
        # calculate sma 4 7 and 20
        new_sma_4 = SMA(prices, 4)
        new_sma_7 = SMA(prices, 7)
        new_sma_20 = SMA(prices, 20)
        new_df = pd.DataFrame(data={'sma_4': new_sma_4.iloc[-1], 'sma_7': new_sma_7.iloc[-1], 'sma_20': new_sma_20.iloc[-1]}, index=[new_sma_4.index[-1]])
        sma_T = self._sma.T
        sma_T.pop(self._sma.iloc[0].name)
        self._sma = sma_T.T
        self._sma = pd.concat([self._sma, new_df], axis=0)

    def sma_decision(self, prices: pd.DataFrame) -> str:
        self.calculate_sma(prices)
        new_indicators = self._sma.iloc[-2:]
        print(new_indicators)
        # sma 4 crossing 7
        if Sma.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1]) == CrossingType.UP:
            # sma4 crossing up sma7
            print('sma 4 up crossing sma 7')
            self._sma_4_7_down_counter = 0
            self._sma_4_7_up_counter += 1
        elif Sma.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1]) == CrossingType.DOWN:
            # sma4 crossing down sma7
            print('sma 4 down crossing sma 7')
            self._sma_4_7_up_counter = 0
            self._sma_4_7_down_counter += 1

        # sma 4 crossing 20
        if Sma.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_20'].iloc[0], new_indicators['sma_20'].iloc[1]) == CrossingType.UP:
            # sma4 crossing up sma20
            print('sma 4 up crossing sma 20')
            self._sma_4_20_down_counter = 0
            self._sma_4_20_up_counter += 1
        elif Sma.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_20'].iloc[0], new_indicators['sma_20'].iloc[1]) == CrossingType.DOWN:
            # sma4 crossing down sma20
            print('sma 4 down crossing sma 20')
            self._sma_4_20_up_counter = 0
            self._sma_4_20_down_counter += 1

        # sma 7 crossing 20 do final check
        if Sma.compare_crossing(new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1], new_indicators['sma_20'].iloc[0], new_indicators['sma_20'].iloc[1]) == CrossingType.UP:
            # sma7 crossing up sma20
            print('sma 7 up crossing sma 20')
            if self._sma_4_7_up_counter <= SMA_4_7_THRESHOLD and self._sma_4_20_up_counter <= SMA_4_20_THRESHOLD:
                self._sma_4_7_up_counter = 0
                self._sma_4_20_up_counter = 0
                return 'BULL'
        elif Sma.compare_crossing(new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1], new_indicators['sma_20'].iloc[0], new_indicators['sma_20'].iloc[1]) == CrossingType.DOWN:
            # sma7 crossing down sma20
            print('sma 7 down crossing sma 20')
            if self._sma_4_7_down_counter <= SMA_4_7_THRESHOLD and self._sma_4_20_down_counter <= SMA_4_20_THRESHOLD:
                self._sma_4_7_down_counter = 0
                self._sma_4_20_down_counter = 0
                return 'BEAR'

        if self._sma_4_7_up_counter > SMA_4_7_THRESHOLD or self._sma_7_20_up_counter > SMA_4_20_THRESHOLD:
            self._sma_4_7_up_counter = 0
            self._sma_4_20_up_counter = 0

        if self._sma_4_7_down_counter > SMA_4_20_THRESHOLD or self._sma_4_20_down_counter > SMA_4_20_THRESHOLD:
            self._sma_4_7_down_counter = 0
            self._sma_4_20_down_counter = 0
        return 'NA'