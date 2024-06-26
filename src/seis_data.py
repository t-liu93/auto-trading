from datetime import datetime, timezone

import pandas as pd
from algo.algo import Algo
from tvDatafeed import Consumer, Seis


class SeisData:
    def __init__(self, name: str, seis: Seis, prices: pd.DataFrame) -> None:
        self._symbol_name = name
        self._seis = seis
        self._consumers: list[Consumer] = []
        self._prices = prices
        self._indicators: dict[str, Algo] = {}

    def add_consumer(self, consumer: Consumer) -> None:
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

    def update_indicators(self, new_indicators: dict[str, Algo]) -> None:
        self._indicators = new_indicators  # needs improvement in the future

    @property
    def prices(self) -> pd.DataFrame:
        return self._prices

    @property
    def indicators(self) -> dict[str, Algo]:
        return self._indicators

    def print_prices(self) -> None:
        print(datetime.now(tz=timezone.utc))
        print(self._prices)
