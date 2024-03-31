import config
import pandas as pd
from algo.ma import Ma
from algo.macd import Macd
from algo.rsi import Rsi
from helper import messaging
from helper.benchmark import Benchmark, Type
from seis_data import SeisData
from tvDatafeed import Interval, Seis, TvDatafeedLive

tvl = TvDatafeedLive(config.USERNAME, config.PASSWORD)

SUGGESTION_THRESHOLD = 3


def seis_cb(seis: Seis, data: pd.DataFrame) -> None:
    name = data.iloc[0].symbol
    seis_stored = seises[name]
    if seis_stored.update_price(data):
        suggestion = seis_stored.indicators["ma"].make_decision(seis_stored.prices)
        suggestion += seis_stored.indicators["rsi"].make_decision(seis_stored.prices)
        suggestion += seis_stored.indicators["macd"].make_decision(seis_stored.prices)
        seis_stored.benchmark.update(seis_stored.indicators["ma"])
        if abs(suggestion) >= SUGGESTION_THRESHOLD:
            suggestion_type = Type.BULL if suggestion > 0 else Type.BEAR
            seis_stored.benchmark.create(data.index[0].to_pydatetime(), suggestion_type)
            messaging.send_symbol_suggestion(seis.symbol, suggestion)


def prepare_initial_data() -> dict[str, SeisData]:
    seises: dict[str, SeisData] = {}
    for symbol in config.LIST_OF_SYMBOLS:
        # needs to discard the last one, because the last candle is not finished yet.
        prices = tvl.get_hist(
            symbol["symbol"],
            symbol["exchange"],
            Interval(symbol["interval"]),
            n_bars=51,
        )[0:50]
        seis = tvl.new_seis(symbol["symbol"], symbol["exchange"], Interval(symbol["interval"]))
        consumer = seis.new_consumer(seis_cb)
        name = prices.iloc[0].symbol
        seis_data = SeisData(name, seis, prices, Benchmark())
        ma = Ma()
        ma.prepare_mas(prices)
        rsi = Rsi()
        rsi.prepare_rsis(prices)
        macd = Macd()
        macd.prepare_macds(prices)
        seis_data.update_indicators({"ma": ma, "rsi": rsi, "macd": macd})
        seis_data.add_consumer(consumer)
        seises[name] = seis_data

    return seises


messaging.send_general_notification("Start application.")

seises: dict[str, SeisData] = prepare_initial_data()
