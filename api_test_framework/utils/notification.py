import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationSender:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.smtp_host = self.config.get("smtp_host", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.smtp_username = self.config.get("smtp_username", "")
        self.smtp_password = self.config.get("smtp_password", "")
        self.from_email = self.config.get("from_email", self.smtp_username)
        self.to_emails = self.config.get("to_emails", [])

    def send_email(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[list] = None,
    ) -> bool:
        _ = attachments
        if not self.to_emails:
            logger.warning("未配置收件人邮箱，跳过发送邮件")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            text_part = MIMEText(body, "plain", "utf-8")
            msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def send_test_report(
        self, summary: Dict[str, Any], report_path: Optional[str] = None
    ) -> bool:
        _ = report_path
        subject = f"API测试报告 - {summary.get('status', '完成')}"

        body = f"""
API测试报告摘要
{'=' * 50}

测试统计:
- 总测试数: {summary.get('total', 0)}
- 通过: {summary.get('passed', 0)}
- 失败: {summary.get('failed', 0)}
- 跳过: {summary.get('skipped', 0)}
- 通过率: {summary.get('pass_rate', 0)}%
- 总耗时: {summary.get('total_duration', 0)}s

状态: {summary.get('status', '完成')}
时间: {summary.get('timestamp', 'N/A')}
        """

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h2>API测试报告</h2>
    <div class="summary">
        <div class="stat">
            <div>总测试数</div>
            <div class="stat-value">{summary.get('total', 0)}</div>
        </div>
        <div class="stat">
            <div>通过</div>
            <div class="stat-value passed">{summary.get('passed', 0)}</div>
        </div>
        <div class="stat">
            <div>失败</div>
            <div class="stat-value failed">{summary.get('failed', 0)}</div>
        </div>
        <div class="stat">
            <div>通过率</div>
            <div class="stat-value">{summary.get('pass_rate', 0)}%</div>
        </div>
    </div>
    <p>状态: {summary.get('status', '完成')}</p>
    <p>时间: {summary.get('timestamp', 'N/A')}</p>
</body>
</html>
        """

        return self.send_email(subject, body, html_body)

    def send_security_alert(
        self, vulnerabilities: Dict[str, list], severity: str = "HIGH"
    ) -> bool:
        subject = f"安全警报 - 发现{severity}级别漏洞"

        total_vulns = sum(len(vulns) for vulns in vulnerabilities.values())

        body = f"""
安全警报
{'=' * 50}

发现漏洞总数: {total_vulns}
严重程度: {severity}

详情:
"""

        for vuln_type, vulns in vulnerabilities.items():
            if vulns:
                body += f"\n{vuln_type.upper()}:\n"
                for vuln in vulns[:5]:
                    body += f"  - 位置: {vuln.get('location', 'N/A')}\n"
                    body += f"    严重程度: {vuln.get('severity', 'N/A')}\n"
                    body += f"    值: {vuln.get('value', 'N/A')}\n"

                if len(vulns) > 5:
                    body += f"  ... 还有 {len(vulns) - 5} 个\n"

        return self.send_email(subject, body)


class SlackNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def send_message(self, message: str, attachments: Optional[list] = None) -> bool:
        if not self.webhook_url:
            logger.warning("未配置Slack Webhook，跳过发送Slack消息")
            return False

        try:
            import requests

            payload = {"text": message, "attachments": attachments or []}

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Slack消息发送成功")
            return True

        except Exception as e:
            logger.error(f"Slack消息发送失败: {e}")
            return False

    def send_test_report(self, summary: Dict[str, Any]) -> bool:
        color = (
            "#36a64f"
            if summary.get("passed", 0) == summary.get("total", 0)
            else "#dc3545"
        )

        message = f"""
*API测试报告*
• 总测试数: {summary.get('total', 0)}
• 通过: {summary.get('passed', 0)}
• 失败: {summary.get('failed', 0)}
• 通过率: {summary.get('pass_rate', 0)}%
• 总耗时: {summary.get('total_duration', 0)}s
        """

        attachments = [
            {
                "color": color,
                "title": "测试详情",
                "text": f"状态: {summary.get('status', '完成')}\n时间: {summary.get('timestamp', 'N/A')}",
                "footer": "API测试框架",
            }
        ]

        return self.send_message(message, attachments)

    def send_security_alert(self, vulnerabilities: Dict[str, list]) -> bool:
        total_vulns = sum(len(vulns) for vulns in vulnerabilities.values())

        message = f"""
*安全警报*
发现漏洞总数: {total_vulns}
        """

        attachments = [
            {
                "color": "#dc3545",
                "title": "漏洞详情",
                "fields": [
                    {"title": vuln_type, "value": f"{len(vulns)} 个", "short": True}
                    for vuln_type, vulns in vulnerabilities.items()
                    if vulns
                ],
                "footer": "API测试框架",
            }
        ]

        return self.send_message(message, attachments)
