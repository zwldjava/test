import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    def __init__(self, env: Optional[str] = None):
        self.env = env or os.getenv("TEST_ENV", "dev")
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        self._load_config()

    def _load_config(self):
        load_dotenv(self.base_dir / ".env")
        config_file = self.config_dir / f"{self.env}.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    @property
    def base_url(self) -> str:
        return str(
            self.get(
                "api.base_url", os.getenv("API_BASE_URL", "http://localhost:8000")
            )
        )

    @property
    def timeout(self) -> int:
        return int(self.get("api.timeout", 30))

    @property
    def headers(self) -> Dict[str, str]:
        return dict(self.get("api.headers", {}))

    @property
    def auth(self) -> Dict[str, str]:
        return dict(self.get("api.auth", {}))

    @property
    def database(self) -> Dict[str, str]:
        return dict(self.get("database", {}))

    @property
    def security_rules(self) -> Dict[str, Any]:
        return dict(self.get("security", {}))


config = Config()
