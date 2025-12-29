import json
from typing import Any, Dict, Optional

import allure
import pytest

from core.http_client import HTTPClient
from core.validator import ResponseValidator
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAPITest:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.validator = ResponseValidator()
        logger.info(f"开始测试: {self.__class__.__name__}")
        yield
        self.client.close()
        logger.info(f"结束测试: {self.__class__.__name__}")

    def log_request(self, method: str, endpoint: str, **kwargs):
        logger.info(f"请求: {method.upper()} {endpoint}")
        if kwargs.get("params"):
            logger.info(f"参数: {kwargs['params']}")
        if kwargs.get("json"):
            logger.info(f"请求体: {json.dumps(kwargs['json'], ensure_ascii=False)}")

    def log_response(self, response):
        logger.info(f"响应状态: {response.status_code}")
        try:
            logger.info(f"响应体: {json.dumps(response.json(), ensure_ascii=False)}")
        except:
            logger.info(f"响应体: {response.text}")

    @allure.step("发送GET请求")
    def get(self, endpoint: str, expected_status: int = 200, **kwargs):
        self.log_request("GET", endpoint, **kwargs)
        response = self.client.get(endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response

    @allure.step("发送POST请求")
    def post(self, endpoint: str, expected_status: int = 201, **kwargs):
        self.log_request("POST", endpoint, **kwargs)
        response = self.client.post(endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response

    @allure.step("发送PUT请求")
    def put(self, endpoint: str, expected_status: int = 200, **kwargs):
        self.log_request("PUT", endpoint, **kwargs)
        response = self.client.put(endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response

    @allure.step("发送DELETE请求")
    def delete(self, endpoint: str, expected_status: int = 204, **kwargs):
        self.log_request("DELETE", endpoint, **kwargs)
        response = self.client.delete(endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response

    @allure.step("发送PATCH请求")
    def patch(self, endpoint: str, expected_status: int = 200, **kwargs):
        self.log_request("PATCH", endpoint, **kwargs)
        response = self.client.patch(endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response

    @allure.step("验证响应字段")
    def assert_field(self, response, field_path: str, expected_value: Any):
        self.validator.validate_field(response, field_path, expected_value)

    @allure.step("验证字段存在")
    def assert_field_exists(self, response, field_path: str):
        self.validator.validate_field_exists(response, field_path)

    @allure.step("验证字段类型")
    def assert_field_type(self, response, field_path: str, expected_type: type):
        self.validator.validate_field_type(response, field_path, expected_type)

    @allure.step("验证数组长度")
    def assert_array_length(self, response, field_path: str, expected_length: int):
        self.validator.validate_array_length(response, field_path, expected_length)

    @allure.step("验证响应时间")
    def assert_response_time(self, response, max_time_ms: int):
        self.validator.validate_response_time(response, max_time_ms)

    @allure.step("验证JSON Schema")
    def assert_schema(self, response, schema: Dict[str, Any]):
        self.validator.validate_json_schema(response, schema)

    def request(self, method: str, endpoint: str, expected_status: int = 200, **kwargs):
        self.log_request(method, endpoint, **kwargs)
        response = self.client.request(method.upper(), endpoint, **kwargs)
        self.log_response(response)
        self.validator.validate_status_code(response, expected_status)
        return response
