from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config.settings import config


class HTTPClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url or config.base_url
        self.timeout = timeout or config.timeout
        self.headers = headers or config.headers.copy()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=10, pool_maxsize=10
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    def _update_headers(
        self, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)
        return merged_headers

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = self._build_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("headers", {})
        kwargs["headers"] = self._update_headers(kwargs["headers"])

        response = self.session.request(method.upper(), url, **kwargs)
        return response

    def get(
        self, endpoint: str, params: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.request("POST", endpoint, data=data, json=json, **kwargs)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
