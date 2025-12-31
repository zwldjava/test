from typing import Dict, Any, Optional
from threading import Lock


class APIContext:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = {}
        return cls._instance
    
    def set(self, key: str, value: Any):
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def remove(self, key: str):
        if key in self._data:
            del self._data[key]
    
    def clear(self):
        self._data.clear()
    
    def get_all(self) -> Dict[str, Any]:
        return self._data.copy()
    
    def update(self, data: Dict[str, Any]):
        self._data.update(data)
    
    def has(self, key: str) -> bool:
        return key in self._data
