from typing import Dict, Type, Optional
from core.http_client import HTTPClient
from core.api.api_context import APIContext
from core.api.base_api import BaseAPI


class APIManager:
    def __init__(self, client: Optional[HTTPClient] = None, context: Optional[APIContext] = None):
        self.client = client or HTTPClient()
        self.context = context or APIContext()
        self._apis: Dict[str, BaseAPI] = {}
    
    def register_api(self, name: str, api_class: Type[BaseAPI]) -> BaseAPI:
        if name in self._apis:
            return self._apis[name]
        
        api_instance = api_class(client=self.client, context=self.context)
        self._apis[name] = api_instance
        return api_instance
    
    def get_api(self, name: str) -> Optional[BaseAPI]:
        return self._apis.get(name)
    
    def get_context(self) -> APIContext:
        return self.context
    
    def clear_context(self):
        self.context.clear()
    
    def set_context(self, key: str, value):
        self.context.set(key, value)
    
    def get_context_value(self, key: str, default=None):
        return self.context.get(key, default)
