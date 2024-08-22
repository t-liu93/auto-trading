import requests

from config import WEBHOOK


def send_general_notification(msg: str) -> None:
    dataset = {"content": "General Notification\n" + f"{msg}"}
    requests.post(WEBHOOK, json=dataset, headers={"Content-type": "application/json"})  # noqa: S113


def send_symbol_suggestion(symbol: str, suggestion: int) -> None:
    suggestion_str = "BULL" if suggestion > 0 else "BEAR"
    dataset = {"content": f"Symbol: {symbol}\n" + f"Suggestion: {suggestion_str}"}
    requests.post(WEBHOOK, json=dataset, headers={"Content-type": "application/json"})  # noqa: S113
