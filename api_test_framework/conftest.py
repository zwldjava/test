import allure
import pytest
import requests_mock

from config.settings import config
from core.http_client import HTTPClient
from utils.data_generator import DataGenerator


@pytest.fixture(scope="session")
def api_client():
    client = HTTPClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def mock_api():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture(scope="function")
def sample_user():
    return DataGenerator.generate_user_data()


@pytest.fixture(scope="function")
def sample_product():
    return DataGenerator.generate_product_data()


@pytest.fixture(scope="function")
def sample_order():
    return DataGenerator.generate_order_data()


@pytest.fixture(scope="function", autouse=True)
def setup_allure_environment(request):
    pass


@pytest.fixture(scope="function")
def auth_token(api_client):
    login_data = {"phone": "18821371697", "password": "Ww12345678.."}
    response = api_client.post("/auth/login", json=login_data)
    if response.status_code == 200:
        response_data = response.json()
        token = response_data.get("data", {}).get("access_token") or response_data.get("data", {}).get("token")
        return token if token else ""
    return ""


@pytest.fixture(scope="function")
def authenticated_client(api_client, auth_token):
    api_client.headers["Authorization"] = f"Bearer {auth_token}"
    yield api_client
    api_client.headers.pop("Authorization", None)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if report.failed:
            allure.attach(
                str(report.longreprtext),
                name="失败信息",
                attachment_type=allure.attachment_type.TEXT,
            )

        if hasattr(item, "obj"):
            test_class = item.obj.__class__.__name__
            test_method = item.obj.__name__
            allure.label("testClass", test_class)
            allure.label("testMethod", test_method)


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "security: 安全测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "api: 接口测试")
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "integration: 集成测试")
