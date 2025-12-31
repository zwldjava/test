from typing import Dict, Optional, Any
import requests
from core.http_client import HTTPClient
from core.api.api_context import APIContext


class BaseAPI:
    def __init__(self, client: Optional[HTTPClient] = None, context: Optional[APIContext] = None):
        self.client = client or HTTPClient()
        self.context = context or APIContext()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        merged_headers = self._get_headers(headers)
        
        if method.upper() == "GET":
            return self.client.get(endpoint, params=params, headers=merged_headers, **kwargs)
        elif method.upper() == "POST":
            return self.client.post(endpoint, data=data, json=json, headers=merged_headers, **kwargs)
        elif method.upper() == "PUT":
            return self.client.put(endpoint, data=data, json=json, headers=merged_headers, **kwargs)
        elif method.upper() == "DELETE":
            return self.client.delete(endpoint, headers=merged_headers, **kwargs)
        elif method.upper() == "PATCH":
            return self.client.patch(endpoint, data=data, json=json, headers=merged_headers, **kwargs)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {}
        
        token = self.context.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _validate_status_code(self, response: requests.Response, expected: int):
        assert response.status_code == expected, f"状态码应该为{expected}，实际为{response.status_code}"
    
    def _validate_response_code(self, response: requests.Response, expected: int):
        response_data = response.json()
        actual = response_data.get("code")
        assert actual == expected, f"响应码应该为{expected}，实际为{actual}"
    
    def _validate_message_contains(self, response: requests.Response, expected: str):
        response_data = response.json()
        message = response_data.get("message", "")
        assert expected in message, f"响应消息应该包含'{expected}'，实际为'{message}'"
    
    def _validate_has_data(self, response: requests.Response):
        response_data = response.json()
        assert "data" in response_data and response_data["data"] is not None, "响应应该包含data字段"
    
    def _validate_field_equals(self, response: requests.Response, field: str, expected: Any):
        response_data = response.json()
        actual = self._get_nested_value(response_data, field)
        assert actual == expected, f"字段{field}应该为{expected}，实际为{actual}"
    
    def _get_nested_value(self, data: Dict, field_path: str):
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _extract_token(self, response: requests.Response, token_field: str = "access_token"):
        response_data = response.json()
        data = response_data.get("data", {})
        
        if isinstance(data, dict):
            token = data.get(token_field) or data.get("token")
        else:
            token = None
        
        if token:
            self.context.set("token", token)
        
        return token
    
    def _extract_data(self, response: requests.Response, field: str = None):
        response_data = response.json()
        data = response_data.get("data", {})
        
        if field:
            return self._get_nested_value(data, field)
        
        return data
    
    def _store_context(self, key: str, value: Any):
        self.context.set(key, value)
    
    def _get_context(self, key: str, default: Any = None):
        return self.context.get(key, default)
