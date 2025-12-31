import pytest
import allure
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from core.api.user_api import UserAPI


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.auth
class TestLoginAPIWithAPILayer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_manager = APIManager()
        self.auth_api = self.api_manager.register_api("auth", AuthAPI)
        self.user_api = self.api_manager.register_api("user", UserAPI)
    
    @pytest.mark.parametrize("phone,password,expected_status,expected_code,expected_message", [
        ("18821371697", "Ww12345678..", 200, 200, "登录成功"),
        ("", "", 200, 400, "密码不能为空"),
        ("18821371697", "", 200, 400, "密码不能为空"),
        ("", "test123", 200, 400, "手机号或用户名不能为空"),
        ("18821371697", "wrongpassword", 200, 401, "手机号或密码错误"),
    ])
    def test_login_scenarios(self, phone, password, expected_status, expected_code, expected_message):
        response = self.auth_api.login(phone, password)
        
        self.auth_api._validate_status_code(response, expected_status)
        self.auth_api._validate_response_code(response, expected_code)
        self.auth_api._validate_message_contains(response, expected_message)
    
    def test_login_with_token_extraction(self):
        response = self.auth_api.login("18821371697", "Ww12345678..")
        
        self.auth_api._validate_status_code(response, 200)
        self.auth_api._validate_response_code(response, 200)
        self.auth_api._validate_message_contains(response, "登录成功")
        
        token = self.auth_api._extract_token(response)
        assert token is not None, "应该成功提取token"
        assert self.api_manager.get_context_value("token") == token, "token应该存储在上下文中"
    
    def test_api_context_sharing(self):
        with allure.step("登录并获取token"):
            token = self.auth_api.login_and_extract_token("18821371697", "Ww12345678..")
            assert token is not None, "登录应该成功并获取token"
        
        with allure.step("验证token在上下文中"):
            context_token = self.api_manager.get_context_value("token")
            assert context_token == token, "token应该在上下文中正确存储"
        
        with allure.step("验证API实例间共享上下文"):
            assert self.user_api.context.get("token") == token, "不同API实例应该共享同一个上下文"
    
    def test_multiple_login_requests(self):
        with allure.step("第一次登录"):
            response1 = self.auth_api.login("18821371697", "Ww12345678..")
            self.auth_api._validate_status_code(response1, 200)
        
        with allure.step("第二次登录"):
            response2 = self.auth_api.login("18821371697", "Ww12345678..")
            self.auth_api._validate_status_code(response2, 200)
        
        with allure.step("验证两次登录都成功"):
            assert response1.status_code == response2.status_code == 200
