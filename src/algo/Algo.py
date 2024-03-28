# import talib
import pandas as pd
from talib import abstract
from SeisData import SeisData
from enum import Enum

SMA = abstract.SMA

class CrossingType(Enum):
    UP = 1
    DOWN = 2
    NO = 3

# Algo will be saved in each seis. this will holds all data to calculate a trigger.
class Algo:
    def __init__(self):
        pass

    def prepare_smas(self, seis: SeisData) -> str:
        sma_4 = SMA(seis.prices, 4)
        sma_7 = SMA(seis.prices, 7)
        sma_20 = SMA(seis.prices, 20)
        indicators: dict[str: pd.DataFrame] = {}
        # get the latest 25 bars to store
        new_index = seis.prices.index.values[-25:]
        new_data = {'sma_4': sma_4.iloc[-25:], 'sma_7': sma_7.iloc[-25:], 'sma_20': sma_20.iloc[-25:]}
        sma = pd.DataFrame(data=new_data, index=new_index)
        indicators['sma'] = sma
        seis.update_indicators(indicators)

    def calculate_indicator(self, seis: SeisData) -> str:
        sma = self.calculate_sma(seis)
        return sma

    @staticmethod
    def compare_crossing(fast_old: float, fast_new: float, slow_old: float, slow_new: float) -> CrossingType:
        if fast_old < slow_old and fast_new > slow_new:
            return CrossingType.UP
        if fast_old > slow_old and fast_new < slow_old:
            return CrossingType.DOWN

    def calculate_sma(self, seis: SeisData) -> str:
        # calculate sma 4 7 and 20
        new_sma_4 = SMA(seis.prices, 4)
        new_sma_7 = SMA(seis.prices, 7)
        new_sma_20 = SMA(seis.prices, 20)
        new_df = pd.DataFrame(data={'sma_4': new_sma_4.iloc[-1], 'sma_7': new_sma_7.iloc[-1], 'sma_20': new_sma_20.iloc[-1]}, index=[new_sma_4.index[-1]])
        indicators = seis.indicators
        sma_T = indicators['sma'].T
        sma_T.pop(indicators['sma'].iloc[0].name)
        indicators['sma'] = sma_T.T
        indicators['sma'] = pd.concat([indicators['sma'], new_df], axis=0)
        seis.update_indicators(indicators)
        new_indicators = indicators['sma'].iloc[-2:]
        if Algo.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1]) == CrossingType.UP:
            return 'slightly bull'
        elif Algo.compare_crossing(new_indicators['sma_4'].iloc[0], new_indicators['sma_4'].iloc[1], new_indicators['sma_7'].iloc[0], new_indicators['sma_7'].iloc[1]) == CrossingType.DOWN:
            return 'slightly bear'

        return 'NA'

