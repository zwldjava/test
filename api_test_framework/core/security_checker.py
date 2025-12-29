import json
import re
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


class SecurityChecker:
    SQL_INJECTION_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"union.*select",
        r"exec.*xp_cmdshell",
        r"1=1",
        r"1=2",
        r"or.*1=1",
        r"and.*1=1",
        r"drop.*table",
        r"insert.*into",
        r"update.*set",
        r"delete.*from",
        r"script.*alert",
        r"waitfor.*delay",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"eval\s*\(",
        r"fromCharCode",
        r"document\.cookie",
        r"document\.write",
        r"innerHTML",
        r"outerHTML",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"..%2f",
        r"..%5c",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r";\s*\w+",
        r"\|\s*\w+",
        r"&&\s*\w+",
        r"`[^`]*`",
        r"\$\(.*\)",
        r"\${[^}]*}",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.security_rules = self.config.get("security", {})
        self.sensitive_keywords = self.security_rules.get("sensitive_keywords", [])
        self.blocked_patterns = self.security_rules.get("blocked_patterns", [])

    def check_sql_injection(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for pattern in self.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "type": "SQL注入",
                                "severity": "HIGH",
                                "location": path,
                                "value": value[:100],
                                "pattern": pattern,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_xss(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for pattern in self.XSS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "type": "XSS攻击",
                                "severity": "HIGH",
                                "location": path,
                                "value": value[:100],
                                "pattern": pattern,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_path_traversal(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for pattern in self.PATH_TRAVERSAL_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "type": "路径遍历",
                                "severity": "HIGH",
                                "location": path,
                                "value": value[:100],
                                "pattern": pattern,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_command_injection(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for pattern in self.COMMAND_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "type": "命令注入",
                                "severity": "CRITICAL",
                                "location": path,
                                "value": value[:100],
                                "pattern": pattern,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_sensitive_data(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for keyword in self.sensitive_keywords:
                    if keyword.lower() in path.lower():
                        vulnerabilities.append(
                            {
                                "type": "敏感数据泄露",
                                "severity": "MEDIUM",
                                "location": path,
                                "value": value[:100],
                                "keyword": keyword,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_blocked_patterns(self, data: Any) -> List[Dict[str, str]]:
        vulnerabilities = []

        def check_value(value, path=""):
            if isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
            elif isinstance(value, str):
                for pattern in self.blocked_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        vulnerabilities.append(
                            {
                                "type": "禁止模式",
                                "severity": "MEDIUM",
                                "location": path,
                                "value": value[:100],
                                "pattern": pattern,
                            }
                        )
                        break

        check_value(data)
        return vulnerabilities

    def check_all(self, data: Any) -> Dict[str, List[Dict[str, str]]]:
        results = {}

        if self.security_rules.get("enable_sql_injection_check", True):
            results["sql_injection"] = self.check_sql_injection(data)

        if self.security_rules.get("enable_xss_check", True):
            results["xss"] = self.check_xss(data)

        if self.security_rules.get("enable_auth_bypass_check", True):
            results["path_traversal"] = self.check_path_traversal(data)
            results["command_injection"] = self.check_command_injection(data)

        if self.security_rules.get("enable_sensitive_data_check", True):
            results["sensitive_data"] = self.check_sensitive_data(data)

        results["blocked_patterns"] = self.check_blocked_patterns(data)

        return results

    def generate_report(self, results: Dict[str, List[Dict[str, str]]]) -> str:
        total_vulnerabilities = sum(len(vulns) for vulns in results.values())

        if total_vulnerabilities == 0:
            return "未发现安全漏洞"

        report_lines = [
            "安全扫描报告",
            f"发现漏洞总数: {total_vulnerabilities}",
            "=" * 50,
        ]

        for vuln_type, vulnerabilities in results.items():
            if vulnerabilities:
                report_lines.append(f"\n{vuln_type.upper()}: {len(vulnerabilities)} 个")
                for vuln in vulnerabilities:
                    report_lines.append(f"  - 位置: {vuln['location']}")
                    report_lines.append(f"    严重程度: {vuln['severity']}")
                    report_lines.append(f"    值: {vuln['value']}")
                    report_lines.append(
                        f"    模式: {vuln.get('pattern', vuln.get('keyword', ''))}"
                    )

        return "\n".join(report_lines)
