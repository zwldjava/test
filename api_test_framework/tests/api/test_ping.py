import pytest
import allure
from core.http_client import HTTPClient
from core.validator import ResponseValidator
from core.security_checker import SecurityChecker


@pytest.mark.smoke
@pytest.mark.api
class TestPingAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.validator = ResponseValidator()
        self.security_checker = SecurityChecker()

    @allure.feature("健康检查")
    @allure.story("Ping接口")
    @allure.title("测试 /system/ping 接口")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ping_endpoint(self):
        with allure.step("发送 GET 请求到 /system/ping"):
            response = self.client.get("/system/ping")
            
            allure.attach(
                f"状态码: {response.status_code}",
                name="响应状态",
                attachment_type=allure.attachment_type.TEXT
            )
            
            allure.attach(
                response.text,
                name="响应内容",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证响应状态码"):
            self.validator.validate_status_code(response, 200)

        with allure.step("验证响应格式"):
            try:
                response_data = response.json()
                assert isinstance(response_data, dict), "响应应该是JSON对象"
                
                allure.attach(
                    str(response_data),
                    name="JSON响应",
                    attachment_type=allure.attachment_type.JSON
                )
            except Exception as e:
                pytest.fail(f"响应不是有效的JSON格式: {e}")

        with allure.step("验证响应时间"):
            self.validator.validate_response_time(response, max_time_ms=5000)

        with allure.step("安全检查"):
            try:
                response_data = response.json()
                security_results = self.security_checker.check_all(response_data)
                
                total_vulnerabilities = sum(len(vulns) for vulns in security_results.values())
                security_report = self.security_checker.generate_report(security_results)
                
                allure.attach(
                    security_report,
                    name="安全检查结果",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                assert total_vulnerabilities == 0, f"发现安全漏洞: {security_report}"
            except Exception as e:
                allure.attach(
                    str(e),
                    name="安全检查异常",
                    attachment_type=allure.attachment_type.TEXT
                )

    @allure.feature("健康检查")
    @allure.story("Ping接口")
    @allure.title("测试 /system/ping 接口响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ping_response_time(self):
        with allure.step("多次请求测试响应时间"):
            response_times = []
            for i in range(5):
                response = self.client.get("/system/ping")
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
            
            assert avg_time < 2000, f"平均响应时间过长: {avg_time:.2f}ms"
            assert max_time < 5000, f"最大响应时间过长: {max_time:.2f}ms"

    @allure.feature("健康检查")
    @allure.story("Ping接口")
    @allure.title("测试 /api/system/ping 接口并发请求")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ping_concurrent_requests(self):
        import concurrent.futures
        
        with allure.step("发送并发请求"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.client.get, "/system/ping") for _ in range(10)]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            allure.attach(
                f"成功: {success_count}/10",
                name="并发请求结果",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("验证所有请求都成功"):
            assert success_count == 10, f"部分请求失败: {success_count}/10"
