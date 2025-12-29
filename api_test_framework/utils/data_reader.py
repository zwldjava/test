import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class DataReader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent.parent / "data"
        
        self._cache: Dict[str, Any] = {}

    def read_yaml(self, filename: str) -> Dict[str, Any]:
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        if filename in self._cache:
            return self._cache[filename]
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self._cache[filename] = data
            return data

    def get(self, filename: str, key: str, default: Any = None) -> Any:
        data = self.read_yaml(filename)
        keys = key.split(".")
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value if value is not None else default

    def get_login_data(self, test_case: str) -> Dict[str, Any]:
        return self.get("login_data.yaml", f"login.{test_case}", {})

    def get_user_data(self, test_case: str) -> Dict[str, Any]:
        return self.get("user_data.yaml", f"users.{test_case}", {})

    def get_product_data(self, test_case: str) -> Dict[str, Any]:
        return self.get("product_data.yaml", f"products.{test_case}", {})

    def get_security_data(self, test_case: str) -> Any:
        return self.get("login_data.yaml", f"security.{test_case}", [])

    def clear_cache(self):
        self._cache.clear()


data_reader = DataReader()
