import os

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
WEBHOOK = os.getenv("WEBHOOK")

LIST_OF_SYMBOLS = [{"symbol": "SPY", "exchange": "", "interval": "1"}]
