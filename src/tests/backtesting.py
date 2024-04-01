import sys

from tvDatafeed import Interval, TvDatafeedLive

sys.path.append("../src")
import config
import pandas as pd
from algo.ma import Ma
from algo.macd import Macd
from algo.mfi import Mfi
from algo.rsi import Rsi
from helper.benchmark import Benchmark, Type
from seis_data import SeisData

SYMBOL = "BTCUSD"
EXCHANGE = "COINBASE"
INTERVAL = "1"
NR_CANDLE = 1000

INIT_NR_CANDLE = 50

SUGGESTION_THRESHOLD = 4
EVA_DIFF_RATE = 1.0005

tvl = TvDatafeedLive(config.USERNAME, config.PASSWORD)

hist_prices = tvl.get_hist(SYMBOL, EXCHANGE, Interval(INTERVAL), n_bars=NR_CANDLE)

seis_data = SeisData(hist_prices.iloc[0].symbol, None, hist_prices)
ma = Ma()
ma.prepare_mas(hist_prices.iloc[0:INIT_NR_CANDLE])
rsi = Rsi()
rsi.prepare_rsis(hist_prices.iloc[0:INIT_NR_CANDLE])
mfi = Mfi()
mfi.prepare_mfis(hist_prices.iloc[0:INIT_NR_CANDLE])
macd = Macd()
macd.prepare_macds(hist_prices.iloc[0:INIT_NR_CANDLE])
seis_data.update_indicators({"ma": ma, "rsi": rsi, "macd": macd, "mfi": mfi})
benchmark = Benchmark(EVA_DIFF_RATE)


def seis_new_price(data: pd.DataFrame) -> None:
    seis_stored = seis_data
    if seis_stored.update_price(data):
        suggestion = seis_stored.indicators["ma"].make_decision(seis_stored.prices)
        suggestion += seis_stored.indicators["rsi"].make_decision(seis_stored.prices)
        suggestion += seis_stored.indicators["macd"].make_decision(seis_stored.prices)
        suggestion += seis_stored.indicators["mfi"].make_decision(seis_stored.prices)
        benchmark.update(data.iloc[-1]["close"])
        if abs(suggestion) >= SUGGESTION_THRESHOLD:
            suggestion_type = Type.BULL if suggestion > 0 else Type.BEAR
            benchmark.create(data.index[0].to_pydatetime(), suggestion_type, data.iloc[-1]["close"])


print("start running data")

for i, v in hist_prices[INIT_NR_CANDLE:].iterrows():  # noqa: B007
    seis_new_price(v.to_frame().T)
