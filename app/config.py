from pathlib import Path
from typing import Any
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class Config:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def get(self, *keys: str, default: Any = None) -> Any:
        node: Any = self._data
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    @property
    def db_url(self) -> str:
        return self.get("database", "url")

    @property
    def fallback(self) -> str:
        return self.get("app", "fallback_answer")


def load_config(path: Path = CONFIG_PATH) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        return Config(yaml.safe_load(f))