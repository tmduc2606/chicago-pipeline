from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CONF_DIR = _REPO_ROOT / "pipeline" / "conf"


class Settings:
    def __init__(self, env: str | None = None) -> None:
        self._env = env or os.getenv("ENV", "local")
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        base_path = _CONF_DIR / "base.yaml"
        if base_path.exists():
            with open(base_path) as f:
                self._data = yaml.safe_load(f) or {}

        env_path = _CONF_DIR / f"{self._env}.yaml"
        if env_path.exists():
            with open(env_path) as f:
                overrides = yaml.safe_load(f) or {}
            self._deep_merge(self._data, overrides)

        self._resolve_env()

    @staticmethod
    def _deep_merge(base: dict, overrides: dict) -> None:
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                Settings._deep_merge(base[key], value)
            else:
                base[key] = value

    def _resolve_env(self) -> None:
        raw = yaml.dump(self._data)
        raw = os.path.expandvars(raw)
        self._data = yaml.safe_load(raw) or {}

    @property
    def storage(self) -> dict[str, Any]:
        return self._data.get("storage", {})

    @property
    def bronze(self) -> dict[str, Any]:
        return self._data.get("bronze", {})

    @property
    def silver(self) -> dict[str, Any]:
        return self._data.get("silver", {})

    @property
    def raw_data(self) -> dict[str, Any]:
        return self._data.get("raw_data", {})

    @property
    def logging(self) -> Any:
        return type("LogConfig", (), {
            "level": self._data.get("logging", {}).get("level", "INFO"),
            "json_format": self._data.get("logging", {}).get("json_format", True),
        })()

    @property
    def validation(self) -> dict[str, Any]:
        return self._data.get("validation", {})


settings = Settings()
