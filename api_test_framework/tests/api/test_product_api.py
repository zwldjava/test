import allure
import pytest

from core.api_spec_validator import APISpecValidator
from core.base_test import BaseAPITest
from core.security_checker import SecurityChecker
from utils.data_generator import DataGenerator


@allure.feature("产品管理")
@allure.story("产品CRUD操作")
class TestProductAPI(BaseAPITest):

    @pytest.fixture(autouse=True)
    def setup_product(self):
        login_data = {"phone": "18821371697", "password": "Ww12345678.."}
        login_response = self.post("/auth/login", json=login_data, expected_status=200)
        self.token = login_response.json()["data"].get("access_token") or login_response.json()["data"].get("token")
        self.client.headers["Authorization"] = f"Bearer {self.token}"
        yield
        self.client.headers.pop("Authorization", None)

    @allure.title("创建产品")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_create_product(self):
        product_data = DataGenerator.generate_product_data()

        response = self.post("/products", json=product_data, expected_status=201)

        self.assert_field_exists(response, "id")
        self.assert_field(response, "name", product_data["name"])
        self.assert_field(response, "price", product_data["price"])

        with allure.step("验证接口规范"):
            validator = APISpecValidator()
            spec_result = validator.validate_endpoint(
                "POST", "/api/products", response, product_data
            )
            allure.attach(
                validator.generate_report(spec_result), name="接口规范验证结果"
            )

    @allure.title("获取产品列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_products(self):
        for _ in range(3):
            product_data = DataGenerator.generate_product_data()
            self.post("/products", json=product_data, expected_status=201)

        response = self.get("/products", expected_status=200)

        self.assert_field_exists(response, "data")
        self.assert_field_type(response, "data", list)
        self.assert_array_length(response, "data", 3)

    @allure.title("获取单个产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_get_product(self):
        product_data = DataGenerator.generate_product_data()
        create_response = self.post(
            "/products", json=product_data, expected_status=201
        )
        product_id = create_response.json()["id"]

        response = self.get(f"/products/{product_id}", expected_status=200)

        self.assert_field(response, "id", product_id)
        self.assert_field(response, "name", product_data["name"])

    @allure.title("更新产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_update_product(self):
        product_data = DataGenerator.generate_product_data()
        create_response = self.post(
            "/products", json=product_data, expected_status=201
        )
        product_id = create_response.json()["id"]

        update_data = {"name": "Updated Product Name", "price": 99.99}
        response = self.put(
            f"/products/{product_id}", json=update_data, expected_status=200
        )

        self.assert_field(response, "name", update_data["name"])
        self.assert_field(response, "price", update_data["price"])

    @allure.title("删除产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_delete_product(self):
        product_data = DataGenerator.generate_product_data()
        create_response = self.post(
            "/products", json=product_data, expected_status=201
        )
        product_id = create_response.json()["id"]

        self.delete(f"/products/{product_id}", expected_status=204)

        response = self.get(f"/products/{product_id}", expected_status=404)


@allure.feature("产品管理")
@allure.story("产品搜索和过滤")
class TestProductSearch(BaseAPITest):

    @pytest.fixture(autouse=True)
    def setup_products(self):
        self.user_data = DataGenerator.generate_user_data()
        self.user_response = self.post(
            "/users/register", json=self.user_data, expected_status=201
        )
        self.token = self.user_response.json().get("token", "")
        self.client.headers["Authorization"] = f"Bearer {self.token}"

        self.products = []
        for i in range(5):
            product_data = DataGenerator.generate_product_data()
            product_data["name"] = f"Test Product {i}"
            product_data["category"] = "electronics" if i % 2 == 0 else "books"
            response = self.post(
                "/products", json=product_data, expected_status=201
            )
            self.products.append(response.json())
        yield
        self.client.headers.pop("Authorization", None)

    @allure.title("按名称搜索产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_search_by_name(self):
        response = self.get("/products?name=Test Product 1", expected_status=200)

        self.assert_field_exists(response, "data")
        products = response.json()["data"]
        assert len(products) > 0
        assert "Test Product 1" in products[0]["name"]

    @allure.title("按分类过滤产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_filter_by_category(self):
        response = self.get("/products?category=electronics", expected_status=200)

        self.assert_field_exists(response, "data")
        products = response.json()["data"]
        for product in products:
            assert product["category"] == "electronics"

    @allure.title("分页查询产品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    def test_pagination(self):
        response = self.get("/products?page=1&limit=2", expected_status=200)

        self.assert_field_exists(response, "data")
        self.assert_array_length(response, "data", 2)
        self.assert_field_exists(response, "meta")
        self.assert_field_exists(response, "meta.total")
        self.assert_field_exists(response, "meta.page")
        self.assert_field_exists(response, "meta.limit")
