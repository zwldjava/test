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
- **数据管理**: 支持从 YAML/JSON 文件读取测试数据，实现数据与代码分离

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
│   ├── base_test.py       # 测试基类
│   └── api/               # API层（新增）
│       ├── __init__.py
│       ├── base_api.py    # 基础API类
│       ├── api_context.py # API上下文管理
│       ├── api_manager.py # API管理器
│       ├── auth_api.py    # 认证API
│       └── user_api.py    # 用户API
├── utils/                  # 工具模块
│   ├── logger.py          # 日志工具
│   ├── data_generator.py  # 数据生成器
│   ├── data_reader.py     # 数据读取器
│   ├── report_generator.py # 报告生成器
│   └── notification.py    # 通知工具
├── tests/                  # 测试用例
│   ├── data/              # 测试数据
│   │   ├── login_test_cases.yaml
│   │   └── user_test_cases.json
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

## API层架构

框架新增了完整的API层，解决了接口硬编码、接口关联数据管理等问题。

### 核心组件

#### 1. BaseAPI - 基础API类

提供通用的HTTP请求和验证功能，所有业务API类都继承自此类。

**主要功能：**
- 统一的HTTP请求方法
- 自动处理认证token
- 响应验证方法
- 数据提取和上下文存储

**示例：**
```python
from core.api.base_api import BaseAPI

class MyAPI(BaseAPI):
    def get_data(self, id: int):
        response = self._request("GET", f"/data/{id}")
        self._validate_status_code(response, 200)
        return self._extract_data(response)
```

#### 2. APIContext - API上下文

管理测试过程中的共享数据（如token、用户ID等），支持接口关联。

**主要功能：**
- 单例模式，全局共享
- 存储和获取上下文数据
- 支持嵌套字段访问

**示例：**
```python
from core.api.api_context import APIContext

context = APIContext()
context.set("token", "abc123")
context.set("user_id", 1001)

token = context.get("token")
user_id = context.get("user_id")
```

#### 3. APIManager - API管理器

统一管理所有API实例和上下文，简化测试代码。

**主要功能：**
- 注册和获取API实例
- 管理共享上下文
- 统一配置管理

**示例：**
```python
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from core.api.user_api import UserAPI

manager = APIManager()
auth_api = manager.register_api("auth", AuthAPI)
user_api = manager.register_api("user", UserAPI)

# 所有API实例共享同一个上下文
token = auth_api.login_and_extract_token("phone", "password")
profile = user_api.get_profile()  # 自动使用上面获取的token
```

#### 4. 业务API类

封装具体的业务接口，提供语义化的方法调用。

**AuthAPI - 认证相关接口：**
```python
from core.api.auth_api import AuthAPI

auth_api = AuthAPI()

# 登录
response = auth_api.login("18821371697", "password")

# 登录并自动提取token
token = auth_api.login_and_extract_token("18821371697", "password")

# 注册
response = auth_api.register("phone", "password", "password", "123456")

# 发送验证码
response = auth_api.send_verification_code("phone")

# 重置密码
response = auth_api.reset_password("phone", "new_password", "123456")

# 刷新token
response = auth_api.refresh_token()

# 退出登录
response = auth_api.logout()
```

**UserAPI - 用户相关接口：**
```python
from core.api.user_api import UserAPI

user_api = UserAPI()

# 获取用户信息
response = user_api.get_profile()
profile = user_api.get_profile_and_extract()

# 更新用户信息
response = user_api.update_profile({"nickname": "新昵称"})

# 修改密码
response = user_api.change_password("old_password", "new_password")

# 获取用户列表
response = user_api.get_user_list(page=1, page_size=10)

# 删除用户
response = user_api.delete_user(1001)

# 根据ID获取用户
response = user_api.get_user_by_id(1001)
```

### 使用API层编写测试

#### 基础用法

```python
import pytest
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI

class TestAuthWithAPILayer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = APIManager()
        self.auth_api = self.manager.register_api("auth", AuthAPI)
    
    def test_login_success(self):
        response = self.auth_api.login("18821371697", "Ww12345678..")
        self.auth_api._validate_status_code(response, 200)
        self.auth_api._validate_response_code(response, 200)
        self.auth_api._validate_message_contains(response, "登录成功")
```

#### 接口关联测试

```python
import pytest
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from core.api.user_api import UserAPI

class TestUserWorkflow:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = APIManager()
        self.auth_api = self.manager.register_api("auth", AuthAPI)
        self.user_api = self.manager.register_api("user", UserAPI)
    
    def test_login_and_get_profile(self):
        # 步骤1: 登录获取token
        token = self.auth_api.login_and_extract_token("18821371697", "Ww12345678..")
        assert token is not None
        
        # 步骤2: 使用token获取用户信息（自动从上下文获取）
        profile = self.user_api.get_profile_and_extract()
        assert profile is not None
        
        # 步骤3: 更新用户信息
        response = self.user_api.update_profile({"nickname": "测试用户"})
        self.user_api._validate_status_code(response, 200)
```

#### 参数化测试

```python
import pytest
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI

class TestAuthScenarios:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = APIManager()
        self.auth_api = self.manager.register_api("auth", AuthAPI)
    
    @pytest.mark.parametrize("phone,password,expected_code,expected_message", [
        ("18821371697", "Ww12345678..", 200, "登录成功"),
        ("", "", 400, "密码不能为空"),
        ("18821371697", "", 400, "密码不能为空"),
        ("18821371697", "wrongpassword", 401, "手机号或密码错误"),
    ])
    def test_login_scenarios(self, phone, password, expected_code, expected_message):
        response = self.auth_api.login(phone, password)
        self.auth_api._validate_response_code(response, expected_code)
        self.auth_api._validate_message_contains(response, expected_message)
```

### 创建自定义业务API类

```python
from core.api.base_api import BaseAPI
import requests

class ProductAPI(BaseAPI):
    def get_product_list(self, category_id: int = None, page: int = 1) -> requests.Response:
        params = {"page": page}
        if category_id:
            params["category_id"] = category_id
        return self._request("GET", "/products", params=params)
    
    def get_product_detail(self, product_id: int) -> requests.Response:
        return self._request("GET", f"/products/{product_id}")
    
    def create_product(self, product_data: dict) -> requests.Response:
        return self._request("POST", "/products", json=product_data)
    
    def update_product(self, product_id: int, product_data: dict) -> requests.Response:
        return self._request("PUT", f"/products/{product_id}", json=product_data)
    
    def delete_product(self, product_id: int) -> requests.Response:
        return self._request("DELETE", f"/products/{product_id}")
```

### API层的优势

1. **消除硬编码**：所有API端点封装在业务API类中，不再在测试用例中硬编码
2. **接口关联**：通过APIContext管理共享数据，轻松实现接口间的数据传递
3. **代码复用**：通用的请求和验证逻辑封装在BaseAPI中，减少重复代码
4. **易于维护**：API变更只需修改对应的业务API类，不影响测试用例
5. **语义清晰**：使用语义化的方法名（如login、get_profile），代码更易读
6. **扩展性强**：可以轻松添加新的业务API类和验证方法

## Data层 - 测试数据管理

框架提供了完整的Data层，支持从YAML和JSON文件读取测试数据，实现数据与代码分离。

### 核心组件

#### DataReader - 数据读取器

提供统一的数据读取接口，支持YAML和JSON格式。

**主要功能：**
- 读取YAML和JSON文件
- 自动识别文件格式
- 提供测试数据加载方法
- 支持数据文件列表查询

**示例：**
```python
from utils.data_reader import DataReader

reader = DataReader()

# 读取YAML文件
data = reader.read_yaml("login_test_cases")

# 读取JSON文件
data = reader.read_json("user_test_cases")

# 自动识别格式
data = reader.read("login_test_cases")

# 获取测试用例列表
test_cases = reader.get_test_cases("login_test_cases")

# 获取特定键的数据
config = reader.get_test_data("config", "api_url")
```

### 测试数据文件格式

#### YAML格式示例

```yaml
test_cases:
  - case_id: TC001
    case_name: 正常登录
    phone: "18821371697"
    password: "Ww12345678.."
    expected_status: 200
    expected_code: 200
    expected_message: "登录成功"
    description: 使用正确的手机号和密码登录

  - case_id: TC002
    case_name: 手机号为空
    phone: ""
    password: "test123"
    expected_status: 200
    expected_code: 400
    expected_message: "手机号或用户名不能为空"
    description: 手机号为空时应该返回错误
```

#### JSON格式示例

```json
{
  "test_cases": [
    {
      "case_id": "TC001",
      "case_name": "获取用户信息成功",
      "user_id": 1,
      "expected_status": 200,
      "expected_code": 200,
      "description": "使用有效的用户ID获取用户信息"
    },
    {
      "case_id": "TC002",
      "case_name": "用户不存在",
      "user_id": 99999,
      "expected_status": 200,
      "expected_code": 404,
      "expected_message": "用户不存在",
      "description": "使用不存在的用户ID应该返回404错误"
    }
  ]
}
```

### 使用Data层编写测试

#### 基础用法

```python
import pytest
from utils.data_reader import DataReader

class TestLoginWithData:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.reader = DataReader()
    
    def test_login_success(self):
        # 读取单个测试数据
        data = self.reader.get_test_data("login_test_cases", "test_cases")[0]
        
        response = self.auth_api.login(data["phone"], data["password"])
        self.auth_api._validate_status_code(response, data["expected_status"])
        self.auth_api._validate_response_code(response, data["expected_code"])
```

#### 使用Fixture

```python
import pytest
from utils.data_reader import DataReader

class TestLoginWithFixture:
    def test_login_success(self, test_cases):
        # 使用fixture加载测试用例
        cases = test_cases("login_test_cases")
        
        for case in cases:
            response = self.auth_api.login(case["phone"], case["password"])
            self.auth_api._validate_status_code(response, case["expected_status"])
            self.auth_api._validate_response_code(response, case["expected_code"])
```

#### 参数化测试

```python
import pytest
from utils.data_reader import DataReader

def load_login_test_cases():
    reader = DataReader()
    return reader.get_test_cases("login_test_cases")

class TestLoginDataDriven:
    @pytest.mark.parametrize("test_case", load_login_test_cases())
    def test_login_scenarios(self, test_case):
        response = self.auth_api.login(test_case["phone"], test_case["password"])
        self.auth_api._validate_status_code(response, test_case["expected_status"])
        self.auth_api._validate_response_code(response, test_case["expected_code"])
        self.auth_api._validate_message_contains(response, test_case["expected_message"])
```

#### 结合API层使用

```python
import pytest
from core.api.api_manager import APIManager
from core.api.auth_api import AuthAPI
from utils.data_reader import DataReader

class TestAuthWithDataLayer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = APIManager()
        self.auth_api = self.manager.register_api("auth", AuthAPI)
        self.reader = DataReader()
    
    def test_login_with_data(self):
        # 从数据文件读取测试用例
        test_cases = self.reader.get_test_cases("login_test_cases")
        
        for case in test_cases:
            with allure.step(f"测试用例: {case['case_name']}"):
                response = self.auth_api.login(case["phone"], case["password"])
                
                self.auth_api._validate_status_code(response, case["expected_status"])
                self.auth_api._validate_response_code(response, case["expected_code"])
                
                if "expected_message" in case:
                    self.auth_api._validate_message_contains(response, case["expected_message"])
```

### Data层的优势

1. **数据与代码分离**：测试数据存储在独立的YAML/JSON文件中，便于维护
2. **易于修改**：修改测试数据无需改动测试代码
3. **支持大量用例**：可以轻松管理成百上千个测试用例
4. **格式灵活**：支持YAML和JSON两种格式，满足不同需求
5. **非技术人员友好**：YAML格式简单易读，非技术人员也能维护数据
6. **参数化测试**：与pytest的参数化功能完美结合

### 数据文件组织建议

```
tests/data/
├── auth/                    # 认证相关数据
│   ├── login_test_cases.yaml
│   ├── register_test_cases.yaml
│   └── reset_password_test_cases.yaml
├── user/                    # 用户相关数据
│   ├── profile_test_cases.yaml
│   └── user_list_test_cases.json
├── product/                 # 产品相关数据
│   └── product_test_cases.yaml
└── common/                  # 通用数据
    └── config.yaml
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
pytest
python generate_allure_report.py
```

或者使用 Allure 命令行工具：
```bash
pytest
allure serve reports/allure-results
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
