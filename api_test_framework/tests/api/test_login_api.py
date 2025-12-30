import pytest
import allure
import concurrent.futures
from core.http_client import HTTPClient
from core.security_checker import SecurityChecker
from utils.data_reader import data_reader


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.auth
class TestLoginAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.security_checker = SecurityChecker()
    
    @classmethod
    def setup_class(cls):
        cls.test_cases = data_reader.read_yaml("login_data.yaml")["test_cases"]
    
    def _execute_request(self, request_data):
        if request_data["method"] == "POST":
            return self.client.post(request_data["endpoint"], json=request_data["body"])
        elif request_data["method"] == "GET":
            return self.client.get(request_data["endpoint"], params=request_data["body"])
        elif request_data["method"] == "PUT":
            return self.client.put(request_data["endpoint"], json=request_data["body"])
        elif request_data["method"] == "DELETE":
            return self.client.delete(request_data["endpoint"], json=request_data["body"])
    
    def _validate_status_code(self, response, expected):
        assert response.status_code == expected, f"状态码应该为{expected}，实际为{response.status_code}"
    
    def _validate_response_code(self, response, expected):
        response_data = response.json()
        assert response_data["code"] == expected, f"响应码应该为{expected}，实际为{response_data['code']}"
    
    def _validate_message_contains(self, response, expected):
        response_data = response.json()
        assert expected in response_data["message"], f"响应消息应该包含'{expected}'，实际为'{response_data['message']}'"
    
    def _validate_has_token(self, response, expected):
        response_data = response.json()
        has_token = "access_token" in response_data["data"] or "token" in response_data["data"]
        assert has_token == expected, f"token存在性应该为{expected}"
    
    def _validate_security_check(self, request_data, check_type, field):
        field_value = request_data["body"][field]
        if check_type == "sql_injection":
            vulnerabilities = self.security_checker.check_sql_injection(request_data["body"])
            assert len(vulnerabilities) > 0, "应该检测到SQL注入载荷"
        elif check_type == "xss":
            vulnerabilities = self.security_checker.check_xss(request_data["body"])
            assert len(vulnerabilities) > 0, "应该检测到XSS载荷"
    
    def _validate_response_time(self, request_data, max_avg_time, max_time, iterations=5):
        response_times = []
        for i in range(iterations):
            response = self._execute_request(request_data)
            response_time_ms = response.elapsed.total_seconds() * 1000
            response_times.append(response_time_ms)
            
            allure.attach(
                f"请求 {i+1}: {response_time_ms:.2f}ms",
                name="响应时间",
                attachment_type=allure.attachment_type.TEXT
            )
        
        avg_time = sum(response_times) / len(response_times)
        max_actual_time = max(response_times)
        
        allure.attach(
            f"平均: {avg_time:.2f}ms, 最大: {max_actual_time:.2f}ms",
            name="响应时间统计",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert avg_time < max_avg_time, f"平均响应时间过长: {avg_time:.2f}ms"
        assert max_actual_time < max_time, f"最大响应时间过长: {max_actual_time:.2f}ms"
    
    def _validate_concurrent_success(self, request_data, expected_success_count, concurrent_count=10):
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(self._execute_request, request_data) for _ in range(concurrent_count)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        
        allure.attach(
            f"成功: {success_count}/{concurrent_count}",
            name="并发请求结果",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert success_count == expected_success_count, f"部分请求失败: {success_count}/{concurrent_count}"
    
    def _run_validations(self, response, request_data, validations):
        for validation in validations:
            validation_type = validation["type"]
            
            if validation_type == "status_code":
                self._validate_status_code(response, validation["expected"])
            elif validation_type == "response_code":
                self._validate_response_code(response, validation["expected"])
            elif validation_type == "message_contains":
                self._validate_message_contains(response, validation["expected"])
            elif validation_type == "has_token":
                self._validate_has_token(response, validation["expected"])
            elif validation_type == "security_check":
                self._validate_security_check(request_data, validation["check_type"], validation["field"])
            elif validation_type == "response_time":
                self._validate_response_time(
                    request_data, 
                    validation["max_avg_time"], 
                    validation["max_time"], 
                    request_data.get("iterations", 5)
                )
            elif validation_type == "concurrent_success":
                self._validate_concurrent_success(
                    request_data, 
                    validation["expected_success_count"], 
                    request_data.get("concurrent_count", 10)
                )
    
    def _attach_data(self, response, request_data):
        allure.attach(
            response.text,
            name="响应内容",
            attachment_type=allure.attachment_type.TEXT
        )
        
        allure.attach(
            str(request_data),
            name="请求数据",
            attachment_type=allure.attachment_type.JSON
        )
    
    @pytest.mark.parametrize("test_case_index", range(10))
    def test_login_api(self, test_case_index):
        test_case = self.test_cases[test_case_index]
        
        allure.dynamic.feature(test_case["feature"])
        allure.dynamic.story(test_case["story"])
        allure.dynamic.severity(getattr(allure.severity_level, test_case["severity"].upper()))
        allure.dynamic.title(test_case["name"])
        
        for tag in test_case.get("tags", []):
            allure.dynamic.tag(tag)
        
        with allure.step(f"测试用例: {test_case['name']}"):
            with allure.step("发送请求"):
                response = self._execute_request(test_case["request"])
                self._attach_data(response, test_case["request"])
            
            with allure.step("验证响应"):
                self._run_validations(response, test_case["request"], test_case["validations"])
