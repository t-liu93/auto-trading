import argparse
import sys
from pathlib import Path

import numpy as np
from pandas import DataFrame
from tvDatafeed import Interval, TvDatafeedLive

file_path = Path(__file__).parent.resolve()
sys.path.append(str(file_path) + "/../..")
import src.config  # noqa: E402

tvl = TvDatafeedLive(src.config.USERNAME, src.config.PASSWORD)

# Create an argument parser
parser = argparse.ArgumentParser(description="Auto Trading Argument Parser")

# Add the required arguments
parser.add_argument("--symbol", type=str, required=True, help="Symbol of the stock")
parser.add_argument("--exchange", type=str, required=True, help="Exchange of the stock")
parser.add_argument("--interval", type=str, required=True, help="Interval for the stock data")
parser.add_argument("--pip-value", type=float, required=True, help="Pip value for the stock")

# Parse the command line arguments
args = parser.parse_args()

# Access the values of the arguments
symbol: str = args.symbol
exchange: str = args.exchange
interval: str = args.interval
n_bars: int = 5000
pip_value: float = args.pip_value

# Use the values in your code
# Example:
prices: DataFrame = tvl.get_hist(symbol, exchange, Interval(interval), n_bars)
prices = prices.T
size_arr: list[float] = []
for date in prices:
    size: float = prices[date]["high"] - prices[date]["low"]
    size_in_pips: int = int(round(size / pip_value))
    size_arr.append(size_in_pips)

size_arr.sort()
percentiles = [0, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 100]
result: list[int] = []
for percentile in percentiles:
    value: int = int(round(np.percentile(size_arr, percentile)))
    result.append(value)
print("Average: ", int(round(np.average(size_arr))))
print("Median: ", int(round(np.median(size_arr))))
for i, percentile in enumerate(percentiles):
    print(f"{percentile} percentile: {result[i]}")
