import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import logging
import allure
import pytest
import requests_mock
from utils.logger import get_logger
from utils.data_reader import DataReader

from config.settings import config
from core.http_client import HTTPClient
from utils.data_generator import DataGenerator

logging.basicConfig(format='%(message)s', level=logging.INFO, force=True)


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


@pytest.fixture(scope="session")
def data_reader():
    reader = DataReader()
    yield reader


@pytest.fixture(scope="function")
def test_data(data_reader):
    def _load_data(file_name: str, key: str = None):
        return data_reader.get_test_data(file_name, key)
    return _load_data


@pytest.fixture(scope="function")
def test_cases(data_reader):
    def _load_test_cases(file_name: str):
        return data_reader.get_test_cases(file_name)
    return _load_test_cases


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    logger = get_logger(__name__)

    if report.when == "call":
        nodeid = item.nodeid
        
        test_path = nodeid.split("::")[0]
        test_file = test_path.replace("tests/", "").replace(".py", "")
        test_name = nodeid.split("::")[-1]
        
        display_name = f"{test_file}::{test_name}"
        
        if report.failed:
            logger.error(f"✗ {display_name}")
            logger.error(f"失败原因: {report.longreprtext}")
            allure.attach(
                str(report.longreprtext),
                name="失败信息",
                attachment_type=allure.attachment_type.TEXT,
            )
        elif report.passed:
            logger.info(f"✓ {display_name}")

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


def pytest_sessionstart(session):
    logger = get_logger(__name__)
    logger.info(f"测试会话开始")


def pytest_sessionfinish(session, exitstatus):
    logger = get_logger(__name__)
    logger.info(f"测试会话结束 - 退出状态码: {exitstatus}")
