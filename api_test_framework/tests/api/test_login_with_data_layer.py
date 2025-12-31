import pytest
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from utils.data_reader import DataReader


class TestLoginWithDataLayer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = APIManager()
        self.auth_api = self.manager.register_api("auth", AuthAPI)
        self.reader = DataReader()
    
    def test_read_yaml_data(self):
        test_cases = self.reader.get_test_cases("login_test_cases")
        assert len(test_cases) > 0
        assert "phone" in test_cases[0]
        assert "password" in test_cases[0]
    
    def test_read_json_data(self):
        test_cases = self.reader.get_test_cases("user_test_cases")
        assert len(test_cases) > 0
        assert "user_id" in test_cases[0]
    
    def test_login_with_data(self):
        test_cases = self.reader.get_test_cases("login_test_cases")
        
        assert len(test_cases) == 6, "应该有6个测试用例"
        
        for case in test_cases:
            assert "case_id" in case, "测试用例应该包含case_id"
            assert "case_name" in case, "测试用例应该包含case_name"
            assert "phone" in case, "测试用例应该包含phone"
            assert "password" in case, "测试用例应该包含password"
            assert "expected_status" in case, "测试用例应该包含expected_status"
            assert "expected_code" in case, "测试用例应该包含expected_code"
            assert "expected_message" in case, "测试用例应该包含expected_message"
            assert "description" in case, "测试用例应该包含description"
