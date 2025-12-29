import allure
import pytest

from config.settings import config
from core.api_spec_validator import APISpecValidator
from core.base_test import BaseAPITest
from core.security_checker import SecurityChecker
from utils.data_generator import DataGenerator


@allure.feature("用户管理")
@allure.story("用户注册")
class TestUserRegistration(BaseAPITest):

    @allure.title("正常用户注册")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_user_registration_success(self):
        user_data = DataGenerator.generate_user_data()

        with allure.step("准备注册数据"):
            allure.attach(
                str(user_data),
                name="注册数据",
                attachment_type=allure.attachment_type.JSON,
            )

        response = self.post("/users/register", json=user_data, expected_status=201)

        with allure.step("验证响应"):
            self.assert_field_exists(response, "id")
            self.assert_field_exists(response, "username")
            self.assert_field_type(response, "id", str)
            self.assert_field(response, "username", user_data["username"])
            self.assert_field(response, "email", user_data["email"])

        with allure.step("验证接口规范"):
            validator = APISpecValidator()
            spec_result = validator.validate_endpoint(
                "POST", "/api/users/register", response, user_data
            )
            allure.attach(
                validator.generate_report(spec_result), name="接口规范验证结果"
            )

    @allure.title("重复用户名注册")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_duplicate_username(self):
        user_data = DataGenerator.generate_user_data()

        self.post("/users/register", json=user_data, expected_status=201)
        response = self.post("/users/register", json=user_data, expected_status=409)

        self.assert_field_exists(response, "error")
        self.assert_field_exists(response, "error.code")

    @allure.title("无效邮箱格式")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_invalid_email(self):
        user_data = DataGenerator.generate_user_data()
        user_data["email"] = "invalid-email"

        response = self.post("/users/register", json=user_data, expected_status=400)

        self.assert_field_exists(response, "error")

    @allure.title("缺少必填字段")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.parametrize("missing_field", ["username", "email", "password"])
    def test_missing_required_field(self, missing_field):
        user_data = DataGenerator.generate_user_data()
        del user_data[missing_field]

        response = self.post("/users/register", json=user_data, expected_status=400)

        self.assert_field_exists(response, "error")


@allure.feature("用户管理")
@allure.story("用户登录")
class TestUserLogin(BaseAPITest):

    @allure.title("正常用户登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_user_login_success(self):
        user_data = DataGenerator.generate_user_data()
        self.post("/users/register", json=user_data, expected_status=201)

        login_data = {
            "username": user_data["username"],
            "password": user_data.get("password", "password123"),
        }

        response = self.post("/users/login", json=login_data, expected_status=200)

        self.assert_field_exists(response, "token")
        self.assert_field_exists(response, "user")
        self.assert_field_type(response, "token", str)

    @allure.title("错误密码登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_wrong_password(self):
        user_data = DataGenerator.generate_user_data()
        self.post("/users/register", json=user_data, expected_status=201)

        login_data = {"username": user_data["username"], "password": "wrongpassword"}

        response = self.post("/users/login", json=login_data, expected_status=401)

        self.assert_field_exists(response, "error")

    @allure.title("不存在的用户登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_nonexistent_user(self):
        login_data = {"username": "nonexistentuser", "password": "password123"}

        response = self.post("/users/login", json=login_data, expected_status=401)

        self.assert_field_exists(response, "error")
