from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class APISpecValidator:
    VALID_HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    STATUS_CODE_CATEGORIES = {
        "2xx": [200, 201, 202, 204, 206],
        "4xx": [400, 401, 403, 404, 405, 409, 422, 429],
        "5xx": [500, 502, 503, 504],
    }

    def __init__(self):
        self.issues = []

    def validate_endpoint(
        self, method: str, endpoint: str, response, request_data: Any = None
    ) -> Dict[str, Any]:
        self.issues = []

        self._validate_http_method(method)
        self._validate_endpoint_format(endpoint)
        self._validate_status_code(response.status_code, method)
        self._validate_response_headers(response)
        self._validate_response_content_type(response)

        if request_data:
            self._validate_request_data(request_data, method)

        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "method": method,
            "endpoint": endpoint,
        }

    def _validate_http_method(self, method: str):
        if method.upper() not in self.VALID_HTTP_METHODS:
            self.issues.append(
                {
                    "type": "HTTP方法规范",
                    "severity": "ERROR",
                    "message": f"不支持的HTTP方法: {method}",
                    "recommendation": f'使用标准HTTP方法: {", ".join(self.VALID_HTTP_METHODS)}',
                }
            )

    def _validate_endpoint_format(self, endpoint: str):
        if not endpoint.startswith("/"):
            self.issues.append(
                {
                    "type": "端点格式",
                    "severity": "WARNING",
                    "message": f"端点应以/开头: {endpoint}",
                    "recommendation": "端点路径应以/开头，如 /api/users",
                }
            )

        if " " in endpoint:
            self.issues.append(
                {
                    "type": "端点格式",
                    "severity": "ERROR",
                    "message": f"端点包含空格: {endpoint}",
                    "recommendation": "移除端点中的空格",
                }
            )

    def _validate_status_code(self, status_code: int, method: str):
        if not isinstance(status_code, int):
            self.issues.append(
                {
                    "type": "状态码规范",
                    "severity": "ERROR",
                    "message": f"状态码应为整数: {status_code}",
                    "recommendation": "返回标准的HTTP状态码",
                }
            )
            return

        if status_code < 100 or status_code >= 600:
            self.issues.append(
                {
                    "type": "状态码规范",
                    "severity": "ERROR",
                    "message": f"无效的状态码: {status_code}",
                    "recommendation": "使用100-599范围内的标准状态码",
                }
            )

        if method.upper() == "POST" and status_code not in [201, 200, 202]:
            self.issues.append(
                {
                    "type": "状态码规范",
                    "severity": "WARNING",
                    "message": f"POST请求推荐返回201或200，实际返回: {status_code}",
                    "recommendation": "POST创建资源应返回201，其他情况返回200或202",
                }
            )

        if method.upper() == "DELETE" and status_code not in [204, 200, 202]:
            self.issues.append(
                {
                    "type": "状态码规范",
                    "severity": "WARNING",
                    "message": f"DELETE请求推荐返回204或200，实际返回: {status_code}",
                    "recommendation": "DELETE删除资源应返回204，其他情况返回200或202",
                }
            )

    def _validate_response_headers(self, response):
        required_headers = ["content-type"]
        missing_headers = []

        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)

        if missing_headers:
            self.issues.append(
                {
                    "type": "响应头规范",
                    "severity": "WARNING",
                    "message": f'缺少推荐的响应头: {", ".join(missing_headers)}',
                    "recommendation": "添加Content-Type等标准响应头",
                }
            )

        if "X-Frame-Options" not in response.headers:
            self.issues.append(
                {
                    "type": "安全响应头",
                    "severity": "INFO",
                    "message": "缺少X-Frame-Options响应头",
                    "recommendation": "添加X-Frame-Options防止点击劫持",
                }
            )

        if "X-Content-Type-Options" not in response.headers:
            self.issues.append(
                {
                    "type": "安全响应头",
                    "severity": "INFO",
                    "message": "缺少X-Content-Type-Options响应头",
                    "recommendation": "添加X-Content-Type-Options: nosniff",
                }
            )

    def _validate_response_content_type(self, response):
        content_type = response.headers.get("content-type", "")

        if not content_type:
            self.issues.append(
                {
                    "type": "响应头规范",
                    "severity": "ERROR",
                    "message": "缺少Content-Type响应头",
                    "recommendation": "所有响应都应包含Content-Type头",
                }
            )

        if "application/json" in content_type and "charset" not in content_type:
            self.issues.append(
                {
                    "type": "响应头规范",
                    "severity": "INFO",
                    "message": "JSON响应建议指定字符集",
                    "recommendation": "使用Content-Type: application/json; charset=utf-8",
                }
            )

    def _validate_request_data(self, data: Any, method: str):
        if method.upper() in ["GET", "DELETE"] and data:
            self.issues.append(
                {
                    "type": "请求体规范",
                    "severity": "WARNING",
                    "message": f"{method}方法不应包含请求体",
                    "recommendation": f"{method}请求应使用查询参数而非请求体",
                }
            )

        if isinstance(data, dict):
            if "id" in data and method.upper() == "POST":
                self.issues.append(
                    {
                        "type": "RESTful规范",
                        "severity": "INFO",
                        "message": "POST请求不应在请求体中包含id字段",
                        "recommendation": "id应由服务端生成，客户端不应指定",
                    }
                )

    def validate_response_structure(
        self, response, expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        self.issues = []

        try:
            data = response.json()

            if not isinstance(data, dict):
                self.issues.append(
                    {
                        "type": "响应结构",
                        "severity": "ERROR",
                        "message": f"响应应为JSON对象，实际类型: {type(data).__name__}",
                        "recommendation": "返回标准的JSON对象格式",
                    }
                )
                return {"valid": False, "issues": self.issues}

            if expected_fields:
                missing_fields = [
                    field for field in expected_fields if field not in data
                ]
                if missing_fields:
                    self.issues.append(
                        {
                            "type": "响应结构",
                            "severity": "ERROR",
                            "message": f'响应缺少必需字段: {", ".join(missing_fields)}',
                            "recommendation": f'确保响应包含字段: {", ".join(expected_fields)}',
                        }
                    )

            if "data" in data and "meta" not in data:
                self.issues.append(
                    {
                        "type": "响应结构",
                        "severity": "INFO",
                        "message": "包含data字段时建议添加meta元数据",
                        "recommendation": "添加meta字段包含分页、总数等信息",
                    }
                )

            if "error" in data and "code" not in data.get("error", {}):
                self.issues.append(
                    {
                        "type": "错误响应规范",
                        "severity": "WARNING",
                        "message": "错误响应应包含错误码",
                        "recommendation": "错误响应应包含code和message字段",
                    }
                )

        except Exception as e:
            self.issues.append(
                {
                    "type": "响应结构",
                    "severity": "ERROR",
                    "message": f"无法解析JSON响应: {str(e)}",
                    "recommendation": "确保返回有效的JSON格式",
                }
            )

        return {"valid": len(self.issues) == 0, "issues": self.issues}

    def generate_report(self, validation_result: Dict[str, Any]) -> str:
        if validation_result["valid"]:
            return "接口规范验证通过"

        lines = [
            f"接口规范验证失败",
            f"方法: {validation_result.get('method', 'N/A')}",
            f"端点: {validation_result.get('endpoint', 'N/A')}",
            "=" * 50,
        ]

        for issue in validation_result["issues"]:
            lines.append(f"\n[{issue['severity']}] {issue['type']}")
            lines.append(f"  问题: {issue['message']}")
            lines.append(f"  建议: {issue['recommendation']}")

        return "\n".join(lines)
