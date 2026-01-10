import pytest
import allure
import yaml
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from core.api.standalone_transfer_api import StandaloneTransferAPI


VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDEzLCJjb21wYW55X2lkIjoxLCJjb21wYW55X3JvbGVfaWQiOjIsInNlbGVjdGVkX3R5cGUiOiJ0ZWFtIiwic2VsZWN0ZWRfaWQiOjE3OSwiaWF0IjoxNzY3ODM5MTY0LCJleHAiOjE3Njc5MjU1NjR9.sp99Iw0CNiKYdN0_n7u8vsbDWj8gDEg1l3pynHOQOAE"


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.wo
class TestCreateTransfer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_manager = APIManager()
        self.auth_api = self.api_manager.register_api("auth", AuthAPI)
        self.transfer_api = self.api_manager.register_api("transfer", StandaloneTransferAPI)
    
    def test_create_transfer_without_auth(self):
        with allure.step("未认证访问创建独立转账接口"):
            response = self.transfer_api.create_transfer(
                actual_payment_amount=1200,
                final_payment_amount=1200,
                payment_account_id=123,
                payment_method=1,
                platform="taobao",
                platform_account="1234123421",
                platform_order_sn="341234123",
                receipt_account_name="1234",
                receipt_account_number="1234123",
                shop_id=51
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
        
        with allure.step("验证返回状态码"):
            self.transfer_api._validate_status_code(response, 200)
    
    @pytest.mark.parametrize("test_case", [
        {"case_id": "TC005", "case_name": "实际支付金额为0", "method": "POST", "params": {"actual_payment_amount": 0, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "1234123421", "platform_order_sn": "341234123", "receipt_account_name": "1234", "receipt_account_number": "1234123", "shop_id": 51}, "expected_status": 200, "expected_code": 500, "description": "实际支付金额为0应该返回错误"},
        {"case_id": "TC006", "case_name": "实际支付金额为负数", "method": "POST", "params": {"actual_payment_amount": -100, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "1234123421", "platform_order_sn": "341234123", "receipt_account_name": "1234", "receipt_account_number": "1234123", "shop_id": 51}, "expected_status": 200, "expected_code": 500, "description": "实际支付金额为负数应该返回错误"},
        {"case_id": "TC007", "case_name": "平台账号为空", "method": "POST", "params": {"actual_payment_amount": 1200, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "", "platform_order_sn": "341234123", "receipt_account_name": "1234", "receipt_account_number": "1234123", "shop_id": 51}, "expected_status": 200, "expected_code": 500, "description": "平台账号为空应该返回错误"},
        {"case_id": "TC008", "case_name": "平台订单号为空", "method": "POST", "params": {"actual_payment_amount": 1200, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "1234123421", "platform_order_sn": "", "receipt_account_name": "1234", "receipt_account_number": "1234123", "shop_id": 51}, "expected_status": 200, "expected_code": 500, "description": "平台订单号为空应该返回错误"},
        {"case_id": "TC009", "case_name": "收款账户名为空", "method": "POST", "params": {"actual_payment_amount": 1200, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "1234123421", "platform_order_sn": "341234123", "receipt_account_name": "", "receipt_account_number": "1234123", "shop_id": 51}, "expected_status": 200, "expected_code": 400, "description": "收款账户名为空应该返回错误"},
        {"case_id": "TC010", "case_name": "收款账号为空", "method": "POST", "params": {"actual_payment_amount": 1200, "final_payment_amount": 1200, "payment_account_id": 123, "payment_method": 1, "platform": "taobao", "platform_account": "1234123421", "platform_order_sn": "341234123", "receipt_account_name": "1234", "receipt_account_number": "", "shop_id": 51}, "expected_status": 200, "expected_code": 400, "description": "收款账号为空应该返回错误"},
    ])
    def test_create_transfer_invalid_params(self, test_case):
        with allure.step("设置有效token"):
            self.transfer_api.context.set("token", VALID_TOKEN)
        
        with allure.step(f"{test_case['case_name']}: {test_case['description']}"):
            response = self.transfer_api.create_transfer(**test_case["params"])
            
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
        
        with allure.step("验证返回错误"):
            self.transfer_api._validate_status_code(response, test_case["expected_status"])
            self.transfer_api._validate_response_code(response, test_case["expected_code"])
