import allure
import pytest

from config.settings import config
from core.api_spec_validator import APISpecValidator
from core.base_test import BaseAPITest
from core.security_checker import SecurityChecker


@allure.feature("安全测试")
@allure.story("SQL注入检测")
class TestSQLInjection(BaseAPITest):

    @allure.title("检测登录接口SQL注入")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_sql_injection_login(self):
        checker = SecurityChecker(config.config)

        sql_payloads = [
            {"username": "admin' OR '1'='1", "password": "anything"},
            {"username": "admin'--", "password": "anything"},
            {"username": "admin'#", "password": "anything"},
            {"username": "admin'; DROP TABLE users--", "password": "anything"},
            {"username": "1' UNION SELECT NULL, NULL--", "password": "anything"},
        ]

        for payload in sql_payloads:
            with allure.step(f"测试SQL注入载荷: {payload['username']}"):
                response = self.post("/users/login", json=payload)

                vulnerabilities = checker.check_sql_injection(payload)

                if vulnerabilities:
                    allure.attach(
                        checker.generate_report({"sql_injection": vulnerabilities}),
                        name="SQL注入检测结果",
                    )

                assert response.status_code in [
                    401,
                    400,
                ], f"SQL注入防护失败，状态码: {response.status_code}"

    @allure.title("检测搜索接口SQL注入")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_sql_injection_search(self):
        checker = SecurityChecker(config.config)

        sql_payloads = [
            "1' OR '1'='1",
            "1'--",
            "1' UNION SELECT NULL--",
            "'; DROP TABLE products--",
        ]

        for payload in sql_payloads:
            with allure.step(f"测试SQL注入载荷: {payload}"):
                response = self.get(f"/products?name={payload}")

                vulnerabilities = checker.check_sql_injection({"name": payload})

                if vulnerabilities:
                    allure.attach(
                        checker.generate_report({"sql_injection": vulnerabilities}),
                        name="SQL注入检测结果",
                    )

                assert response.status_code in [
                    400,
                    403,
                    404,
                ], f"SQL注入防护失败，状态码: {response.status_code}"


@allure.feature("安全测试")
@allure.story("XSS攻击检测")
class TestXSS(BaseAPITest):

    @allure.title("检测XSS攻击")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_xss_attack(self):
        checker = SecurityChecker(config.config)

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'>",
            "<div onmouseover=alert('XSS')>Hover me</div>",
        ]

        for payload in xss_payloads:
            with allure.step(f"测试XSS载荷: {payload[:50]}..."):
                user_data = {
                    "username": f"testuser_{hash(payload)}",
                    "email": f"test_{hash(payload)}@example.com",
                    "password": "password123",
                    "name": payload,
                }

                response = self.post("/users/register", json=user_data)

                vulnerabilities = checker.check_xss(user_data)

                if vulnerabilities:
                    allure.attach(
                        checker.generate_report({"xss": vulnerabilities}),
                        name="XSS检测结果",
                    )

                if response.status_code == 201:
                    response_data = response.json()
                    response_vulnerabilities = checker.check_xss(response_data)

                    if response_vulnerabilities:
                        allure.attach(
                            checker.generate_report({"xss": response_vulnerabilities}),
                            name="响应XSS检测结果",
                        )
                        pytest.fail("响应中包含未转义的XSS载荷")


@allure.feature("安全测试")
@allure.story("路径遍历检测")
class TestPathTraversal(BaseAPITest):

    @allure.title("检测路径遍历攻击")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_path_traversal(self):
        checker = SecurityChecker(config.config)

        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f",
            "..%2f..%2f..%2f",
            "....//....//....//etc/passwd",
        ]

        for payload in path_payloads:
            with allure.step(f"测试路径遍历载荷: {payload}"):
                response = self.get(f"/files/{payload}")

                vulnerabilities = checker.check_path_traversal({"file": payload})

                if vulnerabilities:
                    allure.attach(
                        checker.generate_report({"path_traversal": vulnerabilities}),
                        name="路径遍历检测结果",
                    )

                assert response.status_code in [
                    400,
                    403,
                    404,
                ], f"路径遍历防护失败，状态码: {response.status_code}"


@allure.feature("安全测试")
@allure.story("认证绕过检测")
class TestAuthBypass(BaseAPITest):

    @allure.title("检测未授权访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_unauthorized_access(self):
        protected_endpoints = ["/api/users/me", "/api/products", "/api/orders"]

        for endpoint in protected_endpoints:
            with allure.step(f"测试未授权访问: {endpoint}"):
                response = self.get(endpoint)

                assert (
                    response.status_code == 401
                ), f"未授权访问防护失败: {endpoint}, 状态码: {response.status_code}"

    @allure.title("检测无效Token访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_invalid_token(self):
        invalid_tokens = [
            "",
            "invalid",
            "Bearer invalid",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        ]

        for token in invalid_tokens:
            with allure.step(f"测试无效Token: {token[:20]}..."):
                self.client.headers["Authorization"] = token
                response = self.get("/api/users/me")

                assert (
                    response.status_code == 401
                ), f"无效Token防护失败, 状态码: {response.status_code}"


@allure.feature("安全测试")
@allure.story("敏感数据泄露检测")
class TestSensitiveDataLeakage(BaseAPITest):

    @allure.title("检测敏感数据泄露")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_sensitive_data_leakage(self):
        checker = SecurityChecker(config.config)

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecretPassword123!",
            "credit_card": "4111111111111111",
            "secret": "mysecretkey",
        }

        response = self.post("/api/users/register", json=user_data)

        if response.status_code == 201:
            response_data = response.json()
            vulnerabilities = checker.check_sensitive_data(response_data)

            if vulnerabilities:
                allure.attach(
                    checker.generate_report({"sensitive_data": vulnerabilities}),
                    name="敏感数据泄露检测结果",
                )
                pytest.fail("响应中包含敏感数据")


@allure.feature("安全测试")
@allure.story("接口规范验证")
class TestAPISpecValidation(BaseAPITest):

    @allure.title("验证接口响应规范")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_api_response_spec(self):
        validator = APISpecValidator()

        test_cases = [
            ("GET", "/products", 200),
            ("POST", "/users/register", 201),
            ("GET", "/users/me", 200),
            ("DELETE", "/users/me", 204),
        ]

        for method, endpoint, expected_status in test_cases:
            with allure.step(f"验证 {method} {endpoint}"):
                response = self.request(
                    method, endpoint, expected_status=expected_status
                )

                spec_result = validator.validate_endpoint(method, endpoint, response)

                allure.attach(
                    validator.generate_report(spec_result),
                    name=f"接口规范验证: {method} {endpoint}",
                )

                assert spec_result["valid"], f"接口规范验证失败: {method} {endpoint}"
