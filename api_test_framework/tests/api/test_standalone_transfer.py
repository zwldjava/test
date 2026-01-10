import pytest
import allure
import yaml
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from core.api.standalone_transfer_api import StandaloneTransferAPI


VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDEzLCJjb21wYW55X2lkIjoxLCJjb21wYW55X3JvbGVfaWQiOjIsInNlbGVjdGVkX3R5cGUiOiJ0ZWFtIiwic2VsZWN0ZWRfaWQiOjE3OSwiaWF0IjoxNzY3ODM5MTY0LCJleHAiOjE3Njc5MjU1NjR9.sp99Iw0CNiKYdN0_n7u8vsbDWj8gDEg1l3pynHOQOAE"


@pytest.fixture(scope="class")
def transfer_test_data():
    with open("tests/data/standalone_transfer_test_cases.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.wo
class TestStandaloneTransferAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_manager = APIManager()
        self.auth_api = self.api_manager.register_api("auth", AuthAPI)
        self.transfer_api = self.api_manager.register_api("transfer", StandaloneTransferAPI)
    
    def test_get_transfer_list_without_auth(self):
        with allure.step("未认证访问独立打款列表接口"):
            response = self.transfer_api.get_transfer_list(
                page=1,
                page_size=10,
                start_time=1765123200,
                end_time=1765209599
            )
            
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
        
        with allure.step("验证返回401状态码"):
            self.transfer_api._validate_status_code(response, 401)
        
        with allure.step("验证返回缺少认证信息"):
            self.transfer_api._validate_response_code(response, 401)
            self.transfer_api._validate_message_contains(response, "缺少认证信息")
    
    @pytest.mark.parametrize("test_case", [
        {"case_id": "TC001", "case_name": "正常查询转账列表", "method": "GET", "params": {"page": 1, "page_size": 10}, "expected_status": 200, "expected_code": 200, "description": "使用正确的分页参数查询转账列表"},
        {"case_id": "TC002", "case_name": "分页查询第二页", "method": "GET", "params": {"page": 2, "page_size": 10}, "expected_status": 200, "expected_code": 200, "description": "查询第二页的转账列表"},
        {"case_id": "TC003", "case_name": "使用时间范围查询", "method": "GET", "params": {"page": 1, "page_size": 10, "start_time": 1767839164, "end_time": 1767925564}, "expected_status": 200, "expected_code": 200, "description": "使用时间范围参数查询转账列表"},
        {"case_id": "TC004", "case_name": "无效的分页参数", "method": "GET", "params": {"page": -1, "page_size": 10}, "expected_status": 200, "expected_code": 500, "description": "使用负数的页码应该返回错误"},
    ])
    def test_get_transfer_list(self, test_case):
        with allure.step("设置有效token"):
            self.transfer_api.context.set("token", VALID_TOKEN)
        
        with allure.step(f"{test_case['case_name']}: {test_case['description']}"):
            response = self.transfer_api.get_transfer_list(**test_case["params"])
            
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
            self.transfer_api._validate_status_code(response, test_case["expected_status"])
        
        with allure.step("验证返回数据结构"):
            self.transfer_api._validate_response_code(response, test_case["expected_code"])
