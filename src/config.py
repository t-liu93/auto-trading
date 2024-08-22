from pathlib import Path

from dotenv import dotenv_values

config_path = Path(__file__).parent.resolve()
config_values: dict = dotenv_values(str(config_path) + "/.env")

USERNAME = config_values["USERNAME"]
PASSWORD = config_values["PASSWORD"]
WEBHOOK = config_values["WEBHOOK"]

LIST_OF_SYMBOLS = [{"symbol": "SPY", "exchange": "", "interval": "1"}]
