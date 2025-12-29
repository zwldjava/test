import json
import re
from typing import Any, Dict, List, Optional, Type

from jmespath import search as jmespath_search
from jsonschema import ValidationError, validate
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError


class ResponseValidator:
    @staticmethod
    def validate_status_code(response, expected_status: int):
        actual_status = response.status_code
        assert (
            actual_status == expected_status
        ), f"状态码不匹配: 期望 {expected_status}, 实际 {actual_status}"

    @staticmethod
    def validate_json_schema(response, schema: Dict):
        try:
            data = response.json()
            validate(instance=data, schema=schema)
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        except ValidationError as e:
            raise AssertionError(f"JSON Schema验证失败: {e.message}")

    @staticmethod
    def validate_pydantic_model(response, model: Type[BaseModel]):
        try:
            data = response.json()
            model(**data)
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        except PydanticValidationError as e:
            raise AssertionError(f"Pydantic模型验证失败: {e}")

    @staticmethod
    def extract_value(response, expression: str) -> Any:
        try:
            data = response.json()
            return jmespath_search(expression, data)
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")

    @staticmethod
    def validate_field(response, field_path: str, expected_value: Any):
        actual_value = ResponseValidator.extract_value(response, field_path)
        assert (
            actual_value == expected_value
        ), f"字段值不匹配 [{field_path}]: 期望 {expected_value}, 实际 {actual_value}"

    @staticmethod
    def validate_field_exists(response, field_path: str):
        value = ResponseValidator.extract_value(response, field_path)
        assert value is not None, f"字段不存在: {field_path}"

    @staticmethod
    def validate_field_type(response, field_path: str, expected_type: type):
        value = ResponseValidator.extract_value(response, field_path)
        assert isinstance(
            value, expected_type
        ), f"字段类型不匹配 [{field_path}]: 期望 {expected_type}, 实际 {type(value)}"

    @staticmethod
    def validate_array_length(response, field_path: str, expected_length: int):
        value = ResponseValidator.extract_value(response, field_path)
        assert isinstance(value, list), f"字段不是数组: {field_path}"
        assert (
            len(value) == expected_length
        ), f"数组长度不匹配 [{field_path}]: 期望 {expected_length}, 实际 {len(value)}"

    @staticmethod
    def validate_response_time(response, max_time_ms: int):
        elapsed_ms = response.elapsed.total_seconds() * 1000
        assert (
            elapsed_ms <= max_time_ms
        ), f"响应时间超限: {elapsed_ms:.2f}ms > {max_time_ms}ms"

    @staticmethod
    def validate_headers(response, expected_headers: Dict[str, str]):
        for key, expected_value in expected_headers.items():
            actual_value = response.headers.get(key)
            assert actual_value is not None, f"响应头不存在: {key}"
            assert (
                actual_value == expected_value
            ), f"响应头值不匹配 [{key}]: 期望 {expected_value}, 实际 {actual_value}"
