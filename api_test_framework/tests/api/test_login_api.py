import pytest
import allure
from core.http_client import HTTPClient
from core.validator import ResponseValidator
from core.security_checker import SecurityChecker
from utils.data_reader import data_reader


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.auth
class TestLoginAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.validator = ResponseValidator()
        self.security_checker = SecurityChecker()

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self):
        login_data = data_reader.get_login_data("success")
        
        with allure.step("使用正确的手机号密码登录"):
            request_data = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=request_data)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"应该返回200状态码，实际返回{response.status_code}"

        with allure.step("验证登录成功"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回{login_data['expected_code']}成功码，实际返回{response_data['code']}"
            assert "access_token" in response_data["data"] or "token" in response_data["data"], "应该返回access_token或token"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试空请求体")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_body(self):
        login_data = data_reader.get_login_data("empty_body")
        
        with allure.step("发送空请求体"):
            response = self.client.post("/auth/login", json={})
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, "应该返回200状态码"

        with allure.step("验证错误提示"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回{login_data['expected_code']}错误码"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试只有手机号")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_only_phone(self):
        login_data = data_reader.get_login_data("only_phone")
        
        with allure.step("发送只有手机号的请求"):
            request_data = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=request_data)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, "应该返回200状态码"

        with allure.step("验证错误提示"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回{login_data['expected_code']}错误码"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试只有密码")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_only_password(self):
        login_data = data_reader.get_login_data("only_password")
        
        with allure.step("发送只有密码的请求"):
            request_data = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=request_data)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, "应该返回200状态码"

        with allure.step("验证错误提示"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回{login_data['expected_code']}错误码"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试错误的用户名密码")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_wrong_credentials(self):
        login_data = data_reader.get_login_data("wrong_credentials")
        
        with allure.step("发送错误的手机号密码"):
            request_data = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/api/auth/login", json=request_data)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            assert response.status_code == 200, "应该返回200状态码"

        with allure.step("验证错误提示"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回{login_data['expected_code']}错误码"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试SQL注入攻击")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_sql_injection(self):
        login_data = data_reader.get_login_data("sql_injection")
        
        with allure.step("发送SQL注入载荷"):
            sql_payload = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=sql_payload)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证SQL注入防护"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], "SQL注入应该被阻止"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

        with allure.step("安全检查"):
            vulnerabilities = self.security_checker.check_sql_injection(sql_payload)
            assert len(vulnerabilities) > 0, "应该检测到SQL注入载荷"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试XSS攻击")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_xss_attack(self):
        login_data = data_reader.get_login_data("xss_attack")
        
        with allure.step("发送XSS载荷"):
            xss_payload = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=xss_payload)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证XSS防护"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], "XSS应该被阻止"
            assert login_data["expected_message"] in response_data["message"], f"应该提示{login_data['expected_message']}"

        with allure.step("安全检查"):
            vulnerabilities = self.security_checker.check_xss(xss_payload)
            assert len(vulnerabilities) > 0, "应该检测到XSS载荷"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试超长用户名")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_long_username(self):
        login_data = data_reader.get_login_data("long_username")
        
        with allure.step("发送超长用户名"):
            long_payload = {"phone": login_data["phone"], "password": login_data["password"]}
            response = self.client.post("/auth/login", json=long_payload)
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证输入验证"):
            response_data = response.json()
            assert response_data["code"] == login_data["expected_code"], f"应该返回输入验证错误，实际返回{response_data['code']}"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_response_time(self):
        login_data = data_reader.get_login_data("response_time")
        
        with allure.step("多次请求测试响应时间"):
            response_times = []
            for i in range(login_data["iterations"]):
                response = self.client.post("/auth/login", json={"phone": login_data["phone"], "password": login_data["password"]})
                response_time_ms = response.elapsed.total_seconds() * 1000
                response_times.append(response_time_ms)
                
                allure.attach(
                    f"请求 {i+1}: {response_time_ms:.2f}ms",
                    name="响应时间",
                    attachment_type=allure.attachment_type.TEXT
                )

        with allure.step("验证平均响应时间"):
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            allure.attach(
                f"平均: {avg_time:.2f}ms, 最大: {max_time:.2f}ms",
                name="响应时间统计",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert avg_time < login_data["max_avg_time"], f"平均响应时间过长: {avg_time:.2f}ms"
            assert max_time < login_data["max_time"], f"最大响应时间过长: {max_time:.2f}ms"

    @allure.feature("认证")
    @allure.story("登录接口")
    @allure.title("测试并发登录请求")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_concurrent_requests(self):
        import concurrent.futures
        login_data = data_reader.get_login_data("concurrent_requests")
        
        with allure.step("发送并发请求"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=login_data["concurrent_count"]) as executor:
                futures = [executor.submit(self.client.post, "/auth/login", json={"phone": login_data["phone"], "password": login_data["password"]}) for _ in range(login_data["concurrent_count"])]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            allure.attach(
                f"成功: {success_count}/{login_data['concurrent_count']}",
                name="并发请求结果",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证所有请求都成功"):
            assert success_count == login_data["expected_success_count"], f"部分请求失败: {success_count}/{login_data['concurrent_count']}"
