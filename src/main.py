import secrets

from fastapi import FastAPI
from pydantic import BaseModel

from src.calculation import Calculation
from src.config import Config

Config.init()
if Config.get_env("WEBHOOK") is None:
    token = secrets.token_urlsafe(32)
    print(token)
    Config.update_env("WEBHOOK", token)

TV_USERNAME = Config.get_env("TV_USERNAME")
TV_PASSWORD = Config.get_env("TV_PASSWORD")
DISCORD_WEBHOOK = Config.get_env("DISCORD_WEBHOOK")
WEBHOOK = Config.get_env("WEBHOOK")

calculation = Calculation()
app = FastAPI()


class TvMessage(BaseModel):
    ticker: str
    exchange: str
    interval: str


@app.post("/trade/webhook/" + WEBHOOK)
async def webhook_receive(payload: TvMessage) -> dict:
    print(
        calculation.calculate_parameter(
            ticker=payload.ticker,
            exchange=payload.exchange,
            interval=payload.interval,
        ),
    )
    return {"Status": "Ok"}
