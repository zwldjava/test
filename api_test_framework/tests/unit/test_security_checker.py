import pytest

from config.settings import config
from core.security_checker import SecurityChecker


class TestSecurityChecker:

    @pytest.fixture
    def checker(self):
        return SecurityChecker(config.config)

    def test_check_sql_injection(self, checker):
        malicious_data = {"username": "admin' OR '1'='1", "password": "anything"}

        vulnerabilities = checker.check_sql_injection(malicious_data)
        assert len(vulnerabilities) > 0
        assert vulnerabilities[0]["type"] == "SQL注入"

    def test_check_xss(self, checker):
        malicious_data = {"comment": "<script>alert('XSS')</script>"}

        vulnerabilities = checker.check_xss(malicious_data)
        assert len(vulnerabilities) > 0
        assert vulnerabilities[0]["type"] == "XSS攻击"

    def test_check_path_traversal(self, checker):
        malicious_data = {"file": "../../../etc/passwd"}

        vulnerabilities = checker.check_path_traversal(malicious_data)
        assert len(vulnerabilities) > 0
        assert vulnerabilities[0]["type"] == "路径遍历"

    def test_check_command_injection(self, checker):
        malicious_data = {"command": "ls; cat /etc/passwd"}

        vulnerabilities = checker.check_command_injection(malicious_data)
        assert len(vulnerabilities) > 0
        assert vulnerabilities[0]["type"] == "命令注入"

    def test_check_sensitive_data(self, checker):
        sensitive_data = {"user_password": "secret123", "api_token": "abc123xyz"}

        vulnerabilities = checker.check_sensitive_data(sensitive_data)
        assert len(vulnerabilities) > 0
        assert vulnerabilities[0]["type"] == "敏感数据泄露"

    def test_check_all(self, checker):
        malicious_data = {
            "username": "admin' OR '1'='1",
            "comment": "<script>alert('XSS')</script>",
            "file": "../../../etc/passwd",
            "password": "secret123",
        }

        results = checker.check_all(malicious_data)
        assert "sql_injection" in results
        assert "xss" in results
        assert "path_traversal" in results
        assert "sensitive_data" in results

    def test_safe_data(self, checker):
        safe_data = {
            "username": "normaluser",
            "email": "user@example.com",
            "name": "John Doe",
        }

        results = checker.check_all(safe_data)
        total_vulnerabilities = sum(len(vulns) for vulns in results.values())
        assert total_vulnerabilities == 0
