#!/usr/bin/python
import os
import sys
config_dir = os.path.dirname(os.path.abspath(__file__)) + '/../config'
sys.path.append(config_dir)
import config
from tvDatafeed import TvDatafeedLive, Interval, Seis, Consumer
import requests
import json
from typing import List
from queue import Queue
from datetime import datetime
from dataclasses import dataclass

import pandas as pd

# import talib
from talib import abstract

SMA = abstract.SMA



tvl = TvDatafeedLive(config.USERNAME, config.PASSWORD)
# be = tvl.get_hist('NVDA', 'NASDAQ', Interval.in_5_minute, n_bars=100)

# output = SMA(be, timeperiod=4, price='close')
# print(be.iloc[0].symbol)
# print(output)
# print(be)
# row0 = be.iloc[0].name
# be_t = be.T
# # print(be_t)
# be_t.pop(row0)
# # print(be_t)
# be_new = be = tvl.get_hist('NVDA', 'NASDAQ', Interval.in_5_minute, n_bars=1000)
# be_new_T = be_new.T
# newRow = be_new.iloc[0].name
# be = be_t.T
# # be += be_new.iloc[0]
# print(type(be_new.iloc[0]))
# # print(be)
# be = pd.concat([be, be_new.iloc[0].to_frame().T], axis=0)
# # print(be_new.iloc[0])
# print(be)
# exit()

# besi_hist = tvl.get_hist('BESI', 'EURONEXT', Interval.in_5_minute, n_bars = 100)
# print(besi_hist)

# print(tvl.search_symbol('BESI', 'EURONEXT'))

@dataclass
class Price:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    ohlc4: float
    volume: float

class SeisData:
    def __init__(self, name: str, seis: Seis, prices: pd.DataFrame):
        self._symbol_name = name
        self._seis = seis
        self._consumers: List[Consumer] = []
        self._prices = prices

    def addConsumer(self, consumer: Consumer):
        self._consumers.append(consumer)

    def updatePrice(self, newPrice: pd.DataFrame):
        rowToPop = self._prices.iloc[0].name
        pricesT = self._prices.T
        pricesT.pop(rowToPop)
        oldTime = self._prices.iloc[-1].name.to_pydatetime()
        newTime = newPrice.iloc[0].name.to_pydatetime()
        if oldTime != newTime:
            self._prices = pricesT.T
            self._prices = pd.concat([self._prices, newPrice], axis=0)



    def printPrices(self):
        print(datetime.now())
        print(self._prices)

webhook = config.WEBHOOK

def calculate_sma(input: pd.DataFrame, length: int) -> pd.DataFrame:
    pass

def seis_cb(seis, data: pd.DataFrame):
    name = data.iloc[0].symbol
    seisStored = seises[name]
    seisStored.updatePrice(data)
    dataset = {
        'content':
        'Symbol: {}\n'.format(seis.symbol) +
        'New price: {}'.format(data.iloc[0].close)
    }
    requests.post(webhook, json=dataset, headers={'Content-type': 'application/json'})

def prepare_initial_data() -> dict[str, SeisData]:
    seises: dict[str, SeisData] = {}
    for symbol in config.LIST_OF_SYMBOLS:
        prices = tvl.get_hist(symbol['symbol'], symbol['exchange'], Interval(symbol['interval']), n_bars = 50)
        seis = tvl.new_seis(symbol['symbol'], symbol['exchange'], Interval(symbol['interval']))
        consumer = seis.new_consumer(seis_cb)
        name = prices.iloc[0].symbol
        seis_data = SeisData(name, seis, prices)
        seis_data.addConsumer(consumer)
        seises[name] = seis_data

    return seises

# data = prepare_initial_data()
# print(data)
seises: dict[str, SeisData] = prepare_initial_data()



# dataset = {
#     'content': 'test trigger',
#     'username': 'tradingbot'
# }

# req = requests.post(webhook, data=json.dumps(dataset), headers={'Content-type': 'application/json'})
# req = requests.post(webhook, json=dataset, headers={'Content-type': 'application/json'})


