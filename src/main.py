#!/usr/bin/python
import os
import sys
config_dir = os.path.dirname(os.path.abspath(__file__)) + '/../config'
sys.path.append(config_dir)
import config

from tvDatafeed import TvDatafeedLive, Interval, Seis, Consumer
import requests
from typing import List
from datetime import datetime
from dataclasses import dataclass

from SeisData import SeisData
from algo.Algo import *



tvl = TvDatafeedLive(config.USERNAME, config.PASSWORD)
# symbol = config.LIST_OF_SYMBOLS[0]
# prices = tvl.get_hist(symbol['symbol'], symbol['exchange'], Interval(symbol['interval']), n_bars = 50)
# name = prices.iloc[0].symbol
# seis_data = SeisData(name, None, prices)
# prepare_smas(seis_data)
# exit()

webhook = config.WEBHOOK

def seis_cb(seis, data: pd.DataFrame):
    name = data.iloc[0].symbol
    seis_stored = seises[name]
    if seis_stored.update_price(data):
        suggestion = Algo.calculate_indicator(seis_stored)
        if suggestion != 'NA':
            dataset = {
                'content':
                'Symbol: {}\n'.format(seis.symbol) +
                'Suggestion: {}'.format(suggestion)
            }
            requests.post(webhook, json=dataset, headers={'Content-type': 'application/json'})

def prepare_initial_data() -> dict[str, SeisData]:
    seises: dict[str, SeisData] = {}
    for symbol in config.LIST_OF_SYMBOLS:
        # needs to discard the last one, because the last candle is not finished yet.
        prices = tvl.get_hist(symbol['symbol'], symbol['exchange'], Interval(symbol['interval']), n_bars = 51)[0:50]
        seis = tvl.new_seis(symbol['symbol'], symbol['exchange'], Interval(symbol['interval']))
        consumer = seis.new_consumer(seis_cb)
        name = prices.iloc[0].symbol
        seis_data = SeisData(name, seis, prices)
        seis_data.add_consumer(consumer)
        Algo.prepare_smas(seis_data)
        seises[name] = seis_data

    return seises

seises: dict[str, SeisData] = prepare_initial_data()



