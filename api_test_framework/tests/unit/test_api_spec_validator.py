from unittest.mock import Mock

import pytest

from core.api_spec_validator import APISpecValidator


class TestAPISpecValidator:

    @pytest.fixture
    def validator(self):
        return APISpecValidator()

    @pytest.fixture
    def mock_response(self):
        response = Mock()
        response.status_code = 200
        response.headers = {
            "content-type": "application/json; charset=utf-8",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff"
        }
        response.json.return_value = {
            "id": "123",
            "name": "Test Product",
            "price": 99.99,
        }
        return response

    def test_validate_http_method_valid(self, validator):
        result = validator._validate_http_method("GET")
        assert len(validator.issues) == 0

    def test_validate_http_method_invalid(self, validator):
        validator._validate_http_method("INVALID")
        assert len(validator.issues) > 0
        assert validator.issues[0]["type"] == "HTTP方法规范"

    def test_validate_endpoint_format_valid(self, validator):
        validator._validate_endpoint_format("/api/users")
        assert len(validator.issues) == 0

    def test_validate_endpoint_format_invalid(self, validator):
        validator._validate_endpoint_format("api/users")
        assert len(validator.issues) > 0

        validator.issues.clear()
        validator._validate_endpoint_format("/api users")
        assert len(validator.issues) > 0

    def test_validate_status_code_valid(self, validator):
        validator._validate_status_code(200, "GET")
        assert len(validator.issues) == 0

    def test_validate_status_code_invalid(self, validator):
        validator._validate_status_code(999, "GET")
        assert len(validator.issues) > 0

        validator.issues.clear()
        validator._validate_status_code("200", "GET")
        assert len(validator.issues) > 0

    def test_validate_response_headers_missing_content_type(self, validator):
        response = Mock()
        response.status_code = 200
        response.headers = {}

        validator._validate_response_headers(response)
        assert len(validator.issues) > 0

    def test_validate_endpoint_success(self, validator, mock_response):
        result = validator.validate_endpoint("GET", "/api/products", mock_response)
        assert result["valid"] == True
        assert result["method"] == "GET"
        assert result["endpoint"] == "/api/products"

    def test_validate_response_structure_valid(self, validator, mock_response):
        result = validator.validate_response_structure(mock_response, ["id", "name"])
        assert result["valid"] == True

    def test_validate_response_structure_missing_fields(self, validator, mock_response):
        result = validator.validate_response_structure(
            mock_response, ["id", "name", "missing"]
        )
        assert result["valid"] == False
        assert len(result["issues"]) > 0
