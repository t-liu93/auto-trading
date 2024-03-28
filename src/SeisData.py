from tvDatafeed import TvDatafeedLive, Interval, Seis, Consumer
import requests
from typing import List
from datetime import datetime
import pandas as pd

class SeisData:
    def __init__(self, name: str, seis: Seis, prices: pd.DataFrame):
        self._symbol_name = name
        self._seis = seis
        self._consumers: List[Consumer] = []
        self._prices = prices
        self._indicators: dict[str, pd.DataFrame] = {}

    def add_consumer(self, consumer: Consumer):
        self._consumers.append(consumer)

    def update_price(self, new_price: pd.DataFrame) -> bool:
        row_to_pop = self._prices.iloc[0].name
        prices_t = self._prices.T
        prices_t.pop(row_to_pop)
        old_time = self._prices.iloc[-1].name.to_pydatetime()
        new_time = new_price.iloc[0].name.to_pydatetime()
        if old_time != new_time:
            self._prices = prices_t.T
            self._prices = pd.concat([self._prices, new_price], axis=0)
            return True
        return False

    def update_indicators(self, new_indicators: dict[str, pd.DataFrame]):
        self._indicators = new_indicators # needs improvement in the future

    @property
    def prices(self) -> pd.DataFrame:
        return self._prices

    @property
    def indicators(self) -> dict[str, pd.DataFrame]:
        return self._indicators

    def print_prices(self):
        print(datetime.now())
        print(self._prices)