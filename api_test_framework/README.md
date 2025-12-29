# API自动化测试框架

一个功能完整的API接口自动化测试框架，支持持续集成、安全检查、性能监控和详细报告生成。

## 功能特性

- **完整的测试框架**: 基于 pytest 构建，支持参数化测试、fixtures、标记等
- **HTTP客户端**: 支持重试机制、连接池、超时控制
- **响应验证**: 支持 JSON Schema、Pydantic 模型、自定义断言
- **安全检查**: 自动检测 SQL 注入、XSS、路径遍历、命令注入等漏洞
- **性能监控**: 记录响应时间、并发性能指标
- **测试报告**: 生成 JSON 和 HTML 格式的详细测试报告
- **通知机制**: 支持邮件和 Slack 通知
- **持续集成**: 集成 GitHub Actions，支持多版本 Python 测试
- **数据生成**: 使用 Faker 生成测试数据

## 项目结构

```
api_test_framework/
├── config/                 # 配置文件
│   ├── settings.py        # 配置管理
│   ├── dev.yaml           # 开发环境配置
│   ├── test.yaml          # 测试环境配置
│   └── prod.yaml          # 生产环境配置
├── core/                   # 核心模块
│   ├── http_client.py     # HTTP客户端
│   ├── validator.py       # 响应验证器
│   ├── security_checker.py # 安全检查器
│   ├── api_spec_validator.py # API规范验证
│   └── base_test.py       # 测试基类
├── utils/                  # 工具模块
│   ├── logger.py          # 日志工具
│   ├── data_generator.py  # 数据生成器
│   ├── report_generator.py # 报告生成器
│   └── notification.py    # 通知工具
├── tests/                  # 测试用例
│   ├── api/               # API测试
│   └── unit/              # 单元测试
├── .github/                # GitHub Actions配置
│   └── workflows/
│       ├── ci-cd.yml
│       ├── nightly-tests.yml
│       └── code-quality.yml
├── pytest.ini              # pytest配置
├── requirements.txt        # 依赖包
├── requirements-dev.txt    # 开发依赖
├── mypy.ini               # 类型检查配置
├── pyproject.toml         # 项目元数据
└── README.md              # 项目文档
```

## 安装

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd api_test_framework
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装开发依赖（可选）
```bash
pip install -r requirements-dev.txt
```

## 配置

### 环境配置

在项目根目录创建 `.env` 文件：

```env
TEST_ENV=dev
API_BASE_URL=http://localhost:8000
```

### 配置文件

编辑 `config/dev.yaml` 配置开发环境：

```yaml
api:
  base_url: http://localhost:8000
  timeout: 30
  headers:
    Content-Type: application/json
    User-Agent: API-Test-Framework

database:
  host: localhost
  port: 5432
  name: test_db

security:
  enabled: true
  check_sql_injection: true
  check_xss: true
  check_path_traversal: true
  check_command_injection: true

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/test.log

notification:
  email:
    enabled: false
    smtp_host: smtp.gmail.com
    smtp_port: 587
    smtp_username: your-email@gmail.com
    smtp_password: your-password
    to_emails:
      - recipient@example.com
  slack:
    enabled: false
    webhook_url: https://hooks.slack.com/services/...
```

## 使用方法

### 编写测试用例

创建测试文件 `tests/api/test_example.py`：

```python
import pytest
from core.http_client import HTTPClient
from core.validator import ResponseValidator
from utils.data_generator import DataGenerator


class TestExampleAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = HTTPClient()
        self.validator = ResponseValidator()

    def test_get_users(self):
        response = self.client.get("/api/users")
        
        self.validator.validate_status_code(response, 200)
        self.validator.validate_json_schema(response, {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"}
                }
            }
        })

    def test_create_user(self):
        user_data = DataGenerator.generate_user_data()
        response = self.client.post("/api/users", json=user_data)
        
        self.validator.validate_status_code(response, 201)
        self.validator.validate_field(response, "data.name", user_data["name"])
```

### 运行测试

运行所有测试：
```bash
pytest
```

运行特定测试文件：
```bash
pytest tests/api/test_example.py
```

运行特定测试用例：
```bash
pytest tests/api/test_example.py::TestExampleAPI::test_get_users
```

使用标记运行测试：
```bash
pytest -m smoke
pytest -m "not slow"
```

并行运行测试：
```bash
pytest -n auto
```

生成 Allure 报告：
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

### 安全检查

在测试中启用安全检查：

```python
from core.security_checker import SecurityChecker

def test_api_security():
    client = HTTPClient()
    security_checker = SecurityChecker()
    
    response = client.get("/api/users")
    security_results = security_checker.check_response(response)
    
    assert security_results["total"] == 0, "发现安全漏洞"
```

### 生成测试报告

```python
from utils.report_generator import TestReportGenerator

report_gen = TestReportGenerator()
report_gen.add_test_result("test_get_users", "passed", 0.5)
report_gen.add_test_result("test_create_user", "failed", 1.2, error="AssertionError")
report_gen.add_security_results(security_results)
report_gen.save_json_report()
report_gen.save_html_report()
```

### 发送通知

```python
from utils.notification import NotificationSender, SlackNotifier

sender = NotificationSender(config)
sender.send_test_report(summary)

slack = SlackNotifier(webhook_url)
slack.send_test_report(summary)
```

## 持续集成

### GitHub Actions

项目已配置 GitHub Actions 工作流：

- **CI/CD**: 在每次 push 和 pull request 时运行测试
- **Nightly Tests**: 每天凌晨运行完整测试套件
- **Code Quality**: 检查代码格式、类型和安全性

### 本地运行 CI 检查

```bash
# 代码格式检查
black --check .

# 代码排序检查
isort --check-only .

# 类型检查
mypy .

# 代码质量检查
pylint core utils config
```

## 最佳实践

1. **测试组织**: 按功能模块组织测试，使用清晰的命名
2. **数据管理**: 使用 DataGenerator 生成测试数据，避免硬编码
3. **断言清晰**: 使用 ResponseValidator 提供的验证方法
4. **错误处理**: 在测试中添加适当的错误处理和日志
5. **性能考虑**: 对关键接口添加性能测试
6. **安全优先**: 定期运行安全检查，修复发现的漏洞
7. **文档维护**: 保持测试用例和文档的同步更新

## 高级用法

### 参数化测试

使用 pytest.mark.parametrize 进行参数化测试：

```python
import pytest

@pytest.mark.parametrize("user_id,expected_status", [
    (1, 200),
    (2, 200),
    (999, 404),
])
def test_get_user_by_id(user_id, expected_status):
    client = HTTPClient()
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == expected_status
```

### 测试夹具 (Fixtures)

创建可复用的测试夹具：

```python
# tests/conftest.py
import pytest
from core.http_client import HTTPClient

@pytest.fixture(scope="session")
def api_client():
    """会话级别的HTTP客户端"""
    return HTTPClient()

@pytest.fixture
def authenticated_client(api_client):
    """已认证的客户端"""
    response = api_client.post("/api/auth/login", json={
        "username": "test_user",
        "password": "test_password"
    })
    token = response.json()["data"]["token"]
    api_client.set_auth_header(f"Bearer {token}")
    return api_client

@pytest.fixture
def test_user():
    """测试用户数据"""
    return DataGenerator.generate_user_data()
```

### 性能测试

使用 pytest-benchmark 进行性能测试：

```python
import pytest

def test_api_performance(benchmark):
    client = HTTPClient()
    
    def get_users():
        return client.get("/api/users")
    
    result = benchmark(get_users)
    assert result.status_code == 200
```

### 并发测试

使用 pytest-xdist 进行并发测试：

```bash
# 使用4个进程并发运行测试
pytest -n 4

# 自动检测CPU核心数
pytest -n auto
```

### 数据驱动测试

从 CSV 或 JSON 文件读取测试数据：

```python
import json

def load_test_data():
    with open("tests/data/test_cases.json") as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_data())
def test_data_driven(test_case):
    client = HTTPClient()
    response = client.post(
        test_case["endpoint"],
        json=test_case["payload"]
    )
    assert response.status_code == test_case["expected_status"]
```

### 自定义断言

创建自定义断言方法：

```python
from core.validator import ResponseValidator

class CustomValidator(ResponseValidator):
    def validate_pagination(self, response, expected_page=1, expected_size=10):
        data = response.json()
        assert "pagination" in data, "响应缺少分页信息"
        assert data["pagination"]["page"] == expected_page
        assert data["pagination"]["size"] == expected_size
    
    def validate_response_time(self, response, max_time_ms=1000):
        assert response.elapsed.total_seconds() * 1000 < max_time_ms
```

### 测试标记和分组

使用 pytest 标记组织测试：

```python
import pytest

@pytest.mark.smoke
def test_basic_functionality():
    pass

@pytest.mark.regression
def test_bug_fix():
    pass

@pytest.mark.security
def test_authentication():
    pass

@pytest.mark.slow
def test_large_dataset():
    pass

@pytest.mark.integration
def test_full_workflow():
    pass
```

运行特定标记的测试：
```bash
pytest -m smoke
pytest -m "regression and not slow"
pytest -m "security or smoke"
```

### 环境切换

在不同环境间切换：

```python
import os
from config.settings import Settings

def test_with_environment():
    env = os.getenv("TEST_ENV", "dev")
    settings = Settings(env=env)
    
    client = HTTPClient(base_url=settings.api_base_url)
    response = client.get("/api/users")
    assert response.status_code == 200
```

### Mock 和 Stub

使用 pytest-mock 进行模拟：

```python
from unittest.mock import Mock, patch

def test_with_mock(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    
    mocker.patch("core.http_client.HTTPClient.get", return_value=mock_response)
    
    client = HTTPClient()
    response = client.get("/api/users")
    assert response.status_code == 200
```

### 测试报告定制

自定义 Allure 报告：

```python
import allure

@allure.feature("用户管理")
@allure.story("创建用户")
@allure.title("创建新用户")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_user_with_allure():
    client = HTTPClient()
    
    with allure.step("准备测试数据"):
        user_data = DataGenerator.generate_user_data()
        allure.attach(
            str(user_data),
            name="用户数据",
            attachment_type=allure.attachment_type.JSON
        )
    
    with allure.step("发送创建请求"):
        response = client.post("/api/users", json=user_data)
    
    with allure.step("验证响应"):
        assert response.status_code == 201
        allure.attach(
            response.text,
            name="响应内容",
            attachment_type=allure.attachment_type.JSON
        )
```

## 实际场景示例

### 场景1: 用户注册流程测试

```python
class TestUserRegistration:
    def test_complete_registration_flow(self):
        client = HTTPClient()
        
        # 1. 发送验证码
        with allure.step("发送验证码"):
            response = client.post("/api/auth/send-code", json={
                "phone": "13800138000"
            })
            assert response.status_code == 200
        
        # 2. 验证手机号
        with allure.step("验证手机号"):
            response = client.post("/api/auth/verify-phone", json={
                "phone": "13800138000",
                "code": "123456"
            })
            assert response.status_code == 200
            verify_token = response.json()["data"]["token"]
        
        # 3. 完成注册
        with allure.step("完成注册"):
            user_data = {
                "phone": "13800138000",
                "password": "Test@123456",
                "verify_token": verify_token
            }
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201
            assert "access_token" in response.json()["data"]
```

### 场景2: 订单创建和支付流程

```python
@pytest.mark.integration
class TestOrderFlow:
    def test_order_creation_and_payment(self, authenticated_client):
        # 1. 创建订单
        order_data = {
            "product_id": 1,
            "quantity": 2,
            "shipping_address": DataGenerator.generate_address()
        }
        response = authenticated_client.post("/api/orders", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["data"]["order_id"]
        
        # 2. 获取支付信息
        response = authenticated_client.get(f"/api/orders/{order_id}/payment")
        assert response.status_code == 200
        payment_url = response.json()["data"]["payment_url"]
        
        # 3. 模拟支付回调
        callback_data = {
            "order_id": order_id,
            "status": "success",
            "transaction_id": "TXN123456"
        }
        response = authenticated_client.post(
            "/api/payment/callback",
            json=callback_data
        )
        assert response.status_code == 200
        
        # 4. 验证订单状态
        response = authenticated_client.get(f"/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "paid"
```

### 场景3: 批量数据导入测试

```python
@pytest.mark.slow
class TestBatchImport:
    def test_batch_import_users(self, authenticated_client):
        # 生成批量数据
        users = [DataGenerator.generate_user_data() for _ in range(100)]
        
        # 分批导入
        batch_size = 10
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            response = authenticated_client.post(
                "/api/users/batch",
                json={"users": batch}
            )
            assert response.status_code == 200
            assert response.json()["data"]["imported_count"] == len(batch)
        
        # 验证总数
        response = authenticated_client.get("/api/users")
        assert response.json()["data"]["total"] >= 100
```

### 场景4: API限流测试

```python
@pytest.mark.security
class TestRateLimiting:
    def test_rate_limiting(self):
        client = HTTPClient()
        
        # 快速发送多个请求
        responses = []
        for _ in range(100):
            response = client.get("/api/users")
            responses.append(response)
        
        # 检查是否有429状态码
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "API未实施限流保护"
        
        # 验证限流头
        for response in responses:
            if response.status_code == 429:
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "Retry-After" in response.headers
```

## API参考

### HTTPClient

```python
class HTTPClient:
    def __init__(self, base_url: str = None, timeout: int = 30)
    def get(self, endpoint: str, params: dict = None) -> Response
    def post(self, endpoint: str, json: dict = None, data: dict = None) -> Response
    def put(self, endpoint: str, json: dict = None) -> Response
    def delete(self, endpoint: str) -> Response
    def set_auth_header(self, token: str) -> None
    def set_default_headers(self, headers: dict) -> None
```

### ResponseValidator

```python
class ResponseValidator:
    def validate_status_code(self, response: Response, expected: int) -> None
    def validate_json_schema(self, response: Response, schema: dict) -> None
    def validate_field(self, response: Response, field_path: str, expected: Any) -> None
    def validate_response_time(self, response: Response, max_ms: int) -> None
```

### SecurityChecker

```python
class SecurityChecker:
    def check_response(self, response: Response) -> dict
    def check_sql_injection(self, data: str) -> list
    def check_xss(self, data: str) -> list
    def check_path_traversal(self, data: str) -> list
    def check_command_injection(self, data: str) -> list
```

### DataGenerator

```python
class DataGenerator:
    @staticmethod
    def generate_user_data() -> dict
    @staticmethod
    def generate_address() -> dict
    @staticmethod
    def generate_product_data() -> dict
    @staticmethod
    def generate_order_data() -> dict
```

## 故障排查

### 常见问题

1. **导入错误**: 确保在项目根目录运行测试
2. **配置问题**: 检查 .env 和 YAML 配置文件
3. **网络问题**: 检查 API_BASE_URL 和网络连接
4. **依赖冲突**: 使用虚拟环境隔离项目依赖

### 调试技巧

```bash
# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 在第一个失败时停止
pytest -x

# 进入调试器
pytest --pdb
```

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
