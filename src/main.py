import config
import pandas as pd
from algo.ma import Ma
from helper import messaging
from seis_data import SeisData
from tvDatafeed import Interval, Seis, TvDatafeedLive

tvl = TvDatafeedLive(config.USERNAME, config.PASSWORD)


def seis_cb(seis: Seis, data: pd.DataFrame) -> None:
    name = data.iloc[0].symbol
    seis_stored = seises[name]
    if seis_stored.update_price(data):
        suggestion = seis_stored.indicators["ma"].ma_decision(seis_stored.prices)

        if suggestion != "NA":
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
        seis_data = SeisData(name, seis, prices)
        ma = Ma()
        ma.prepare_mas(prices)
        seis_data.update_indicators({"ma": ma})
        seis_data.add_consumer(consumer)
        seises[name] = seis_data

    return seises


messaging.send_general_notification("Start application.")

seises: dict[str, SeisData] = prepare_initial_data()
