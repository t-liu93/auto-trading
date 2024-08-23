import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pandas import DataFrame
from tvDatafeed import Interval, TvDatafeedLive

from src.config import Config

json_path = str(Path(__file__).parent.resolve()) + "/tickers.json"


class Calculation:
    @dataclass
    class TradingParameter:
        entry: float
        stop_loss: float
        tp_2_2: float
        tp_3_2: float
        tp_5: float
        tp_7: float
        tp_10: float

    @dataclass
    class TickerParameter:
        min_size: float
        threshold: float

    class BarType(Enum):
        BULL = 0
        BEAR = 1

    SL_REF_RATIO: float = 1.2

    def __init__(self) -> None:
        self._tickers: dict[str, Calculation.TickerParameter] = {}
        with Path.open(json_path) as json_file:
            tickers: dict = json.loads(json_file.read())
            for ticker, parameter in tickers.items():
                self._tickers[ticker] = Calculation.TickerParameter(min_size=parameter["min_size"], threshold=parameter["threshold"])

        self._tv = TvDatafeedLive(username=Config.get_env("TV_USERNAME"), password=Config.get_env("TV_PASSWORD"))

    def calculate_parameter(self, ticker: str, exchange: str, interval: str) -> TradingParameter:
        if ticker not in self._tickers:
            return None
        bar: DataFrame = self._tv.get_hist(symbol=ticker, exchange=exchange, interval=Interval(interval), n_bars=2)
        print(bar)
        open_price = float(bar.iloc[0]["open"])
        close_price = float(bar.iloc[0]["close"])
        high_price = float(bar.iloc[0]["high"])
        low_price = float(bar.iloc[0]["low"])
        parameter = self._tickers[ticker]
        if (
            Calculation._determine_bar_type(open_price=open_price, close_price=close_price, high_price=high_price, low_price=low_price)
            == Calculation.BarType.BULL
        ):
            sl_ref: float = (close_price - low_price) * Calculation.SL_REF_RATIO
            if sl_ref > parameter.threshold:
                pass
            risk = sl_ref
            return Calculation.TradingParameter(
                entry=round(close_price, 4),
                stop_loss=round(close_price - sl_ref, 4),
                tp_2_2=round(close_price + (risk * 2.2), 4),
                tp_3_2=round(close_price + (risk * 3.2), 4),
                tp_5=round(close_price + (risk * 5), 4),
                tp_7=round(close_price + (risk * 7), 4),
                tp_10=round(close_price + (risk * 10), 4),
            )

        sl_ref: float = (high_price - close_price) * Calculation.SL_REF_RATIO
        if sl_ref > parameter.threshold:
            pass
        risk = sl_ref
        return Calculation.TradingParameter(
            entry=round(close_price, 4),
            stop_loss=round(close_price + sl_ref, 4),
            tp_2_2=round(close_price - (risk * 2.2), 4),
            tp_3_2=round(close_price - (risk * 3.2), 4),
            tp_5=round(close_price - (risk * 5), 4),
            tp_7=round(close_price - (risk * 7), 4),
            tp_10=round(close_price - (risk * 10), 4),
        )

    @staticmethod
    def _determine_bar_type(open_price: float, close_price: float, high_price: float, low_price: float) -> BarType:
        upper_wick: float = high_price - max(open_price, close_price)
        lower_wick: float = min(open_price, close_price) - low_price
        if upper_wick > lower_wick:
            return Calculation.BarType.BULL
        return Calculation.BarType.BEAR


calculation = Calculation()
