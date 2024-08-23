from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from dotenv import dotenv_values, set_key, unset_key

if TYPE_CHECKING:
    from collections import OrderedDict

config_path = Path(__file__).parent.resolve()
DOT_ENV_PATH = Path(config_path, ".env")
DOT_ENV_PATH.touch(mode=0o600, exist_ok=True)


class Config:
    env_dict: ClassVar[OrderedDict[str, str]] = {}
    dot_env_path = DOT_ENV_PATH
    VERSION = "2.0"

    @staticmethod
    def init(dotenv_path: str = DOT_ENV_PATH) -> None:
        Config.dot_env_path = dotenv_path
        Config.env_dict = dotenv_values(dotenv_path=dotenv_path)

    @staticmethod
    def get_env(key: str) -> str | None:
        if key in Config.env_dict:
            return Config.env_dict[key]
        return None

    @staticmethod
    def update_env(key: str, value: str) -> None:
        set_key(Config.dot_env_path, key, value)
        Config.env_dict = dotenv_values(dotenv_path=Config.dot_env_path)

    @staticmethod
    def remove_env(key: str) -> None:
        unset_key(Config.dot_env_path, key)
        Config.env_dict = dotenv_values(dotenv_path=Config.dot_env_path)
