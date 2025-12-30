import pytest
import allure
import concurrent.futures
import json
from core.http_client import HTTPClient
from core.security_checker import SecurityChecker
from utils.data_reader import data_reader
from utils.logger import get_logger


test_cases_data = data_reader.read_yaml("wo_data.yaml")["test_cases"]


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.wo
class TestWoAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.security_checker = SecurityChecker()
        self.logger = get_logger(__name__)
    
    @classmethod
    def setup_class(cls):
        cls.test_cases = test_cases_data
        cls.token = cls._get_token()
    
    @classmethod
    def _get_token(cls):
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDEzLCJjb21wYW55X2lkIjoxLCJjb21wYW55X3JvbGVfaWQiOjIsInNlbGVjdGVkX3R5cGUiOiJvcmciLCJzZWxlY3RlZF9pZCI6MjE0LCJpYXQiOjE3NjY5OTk5MjgsImV4cCI6MTc2NzA4NjMyOH0.9QA_Z1_7XQ2xvz5J5uoCa0HSA-0zLwUvEuIN8YHhsP8"
    
    def _execute_request(self, request_data):
        headers = request_data.get("headers", {}).copy()
        
        if "Authorization" in headers and "{token}" in headers["Authorization"]:
            headers["Authorization"] = headers["Authorization"].replace("{token}", self.token)
        
        self.logger.info("=" * 80)
        self.logger.info(f"开始执行请求 - 方法: {request_data['method']}")
        self.logger.info(f"请求端点: {request_data['endpoint']}")
        self.logger.info(f"请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        self.logger.info(f"请求体: {json.dumps(request_data['body'], ensure_ascii=False, indent=2)}")
        
        if request_data["method"] == "POST":
            response = self.client.post(request_data["endpoint"], json=request_data["body"], headers=headers)
        elif request_data["method"] == "GET":
            response = self.client.get(request_data["endpoint"], params=request_data["body"], headers=headers)
        elif request_data["method"] == "PUT":
            response = self.client.put(request_data["endpoint"], json=request_data["body"], headers=headers)
        elif request_data["method"] == "DELETE":
            response = self.client.delete(request_data["endpoint"], json=request_data["body"], headers=headers)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.info(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")
        self.logger.info(f"响应体: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        self.logger.info(f"响应时间: {response.elapsed.total_seconds() * 1000:.2f}ms")
        self.logger.info("=" * 80)
        
        return response
    
    def _validate_status_code(self, response, expected):
        self.logger.info(f"验证状态码 - 预期: {expected}, 实际: {response.status_code}")
        assert response.status_code == expected, f"状态码应该为{expected}，实际为{response.status_code}"
        self.logger.info("状态码验证通过")
    
    def _validate_response_code(self, response, expected):
        response_data = response.json()
        actual_code = response_data.get('code', 'N/A')
        self.logger.info(f"验证响应码 - 预期: {expected}, 实际: {actual_code}")
        assert response_data["code"] == expected, f"响应码应该为{expected}，实际为{response_data['code']}"
        self.logger.info("响应码验证通过")
    
    def _validate_message_contains(self, response, expected):
        response_data = response.json()
        actual_message = response_data.get('message', 'N/A')
        self.logger.info(f"验证响应消息 - 预期包含: '{expected}', 实际: '{actual_message}'")
        assert expected in response_data["message"], f"响应消息应该包含'{expected}'，实际为'{response_data['message']}'"
        self.logger.info("响应消息验证通过")
    
    def _validate_has_field(self, response, field):
        response_data = response.json()
        self.logger.info(f"验证字段存在 - 字段路径: {field}")
        field_parts = field.split(".")
        current = response_data
        for part in field_parts:
            if isinstance(current, dict):
                if part not in current:
                    assert False, f"响应中缺少字段: {field}"
                current = current[part]
            else:
                assert False, f"字段路径无效: {field}"
        assert True, f"字段 {field} 存在"
        self.logger.info(f"字段 {field} 验证通过")
    
    def _validate_security_check(self, request_data, check_type, field):
        field_value = request_data["body"][field]
        self.logger.info(f"执行安全检查 - 类型: {check_type}, 字段: {field}")
        if check_type == "sql_injection":
            vulnerabilities = self.security_checker.check_sql_injection(request_data["body"])
            assert len(vulnerabilities) > 0, "应该检测到SQL注入载荷"
            self.logger.info(f"检测到 {len(vulnerabilities)} 个SQL注入载荷")
        elif check_type == "xss":
            vulnerabilities = self.security_checker.check_xss(request_data["body"])
            assert len(vulnerabilities) > 0, "应该检测到XSS载荷"
            self.logger.info(f"检测到 {len(vulnerabilities)} 个XSS载荷")
    
    def _validate_response_time(self, request_data, max_avg_time, max_time, iterations=5):
        self.logger.info(f"执行响应时间测试 - 迭代次数: {iterations}, 最大平均时间: {max_avg_time}ms, 最大时间: {max_time}ms")
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
        
        self.logger.info(f"响应时间统计 - 平均: {avg_time:.2f}ms, 最大: {max_actual_time:.2f}ms, 最小: {min(response_times):.2f}ms")
        
        allure.attach(
            f"平均: {avg_time:.2f}ms, 最大: {max_actual_time:.2f}ms",
            name="响应时间统计",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert avg_time < max_avg_time, f"平均响应时间过长: {avg_time:.2f}ms"
        assert max_actual_time < max_time, f"最大响应时间过长: {max_actual_time:.2f}ms"
        self.logger.info("响应时间验证通过")
    
    def _validate_concurrent_success(self, request_data, expected_success_count, concurrent_count=10):
        self.logger.info(f"执行并发测试 - 并发数: {concurrent_count}, 预期成功数: {expected_success_count}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(self._execute_request, request_data) for _ in range(concurrent_count)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        
        self.logger.info(f"并发测试结果 - 成功: {success_count}/{concurrent_count}")
        
        allure.attach(
            f"成功: {success_count}/{concurrent_count}",
            name="并发请求结果",
            attachment_type=allure.attachment_type.TEXT
        )
        
        assert success_count == expected_success_count, f"部分请求失败: {success_count}/{concurrent_count}"
        self.logger.info("并发测试验证通过")
    
    def _run_validations(self, response, request_data, validations):
        for validation in validations:
            validation_type = validation["type"]
            
            if validation_type == "status_code":
                self._validate_status_code(response, validation["expected"])
            elif validation_type == "response_code":
                self._validate_response_code(response, validation["expected"])
            elif validation_type == "message_contains":
                self._validate_message_contains(response, validation["expected"])
            elif validation_type == "has_field":
                self._validate_has_field(response, validation["field"])
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
    
    @pytest.mark.parametrize("test_case_index", range(len(test_cases_data)))
    def test_wo_api(self, test_case_index):
        test_case = self.test_cases[test_case_index]
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"开始执行测试用例 [{test_case_index}]: {test_case['name']}")
        self.logger.info(f"功能: {test_case['feature']}")
        self.logger.info(f"场景: {test_case['story']}")
        self.logger.info(f"严重级别: {test_case['severity']}")
        self.logger.info(f"标签: {', '.join(test_case.get('tags', []))}")
        self.logger.info(f"{'='*80}\n")
        
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
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"测试用例 [{test_case_index}]: {test_case['name']} 执行完成")
        self.logger.info(f"{'='*80}\n")
