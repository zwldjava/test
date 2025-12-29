import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class TestReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "tests": [],
            "security": {},
            "performance": {},
        }

    def add_test_result(
        self, test_name: str, status: str, duration: float, error: Optional[str] = None
    ):
        self.report_data["tests"].append(
            {
                "name": test_name,
                "status": status,
                "duration": duration,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_security_results(self, security_results: Dict[str, List[Dict]]):
        self.report_data["security"] = security_results

    def add_performance_metrics(self, metrics: Dict[str, Any]):
        self.report_data["performance"] = metrics

    def generate_summary(self) -> Dict[str, Any]:
        total_tests = len(self.report_data["tests"])
        passed = sum(1 for t in self.report_data["tests"] if t["status"] == "passed")
        failed = sum(1 for t in self.report_data["tests"] if t["status"] == "failed")
        skipped = sum(1 for t in self.report_data["tests"] if t["status"] == "skipped")

        total_duration = sum(t["duration"] for t in self.report_data["tests"])

        summary = {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round(
                (passed / total_tests * 100) if total_tests > 0 else 0, 2
            ),
            "total_duration": round(total_duration, 2),
        }
        self.report_data["summary"] = summary
        return dict(summary)

    def save_json_report(self, filename: str = "test-report.json"):
        self.generate_summary()
        report_path = self.output_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON报告已保存: {report_path}")
        return report_path

    def save_html_report(self, filename: str = "test-report.html"):
        self.generate_summary()
        report_path = self.output_dir / filename

        html_content = self._generate_html()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML报告已保存: {report_path}")
        return report_path

    def _generate_html(self) -> str:
        summary = self.report_data["summary"]

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .summary-card .value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .summary-card.passed .value {{ color: #28a745; }}
        .summary-card.failed .value {{ color: #dc3545; }}
        .summary-card.skipped .value {{ color: #ffc107; }}
        .section {{ padding: 30px; border-top: 1px solid #eee; }}
        .section h2 {{ color: #333; margin-bottom: 20px; }}
        .test-table {{ width: 100%; border-collapse: collapse; }}
        .test-table th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; }}
        .test-table td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        .test-table tr:hover {{ background: #f8f9fa; }}
        .status {{ padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .status.passed {{ background: #d4edda; color: #155724; }}
        .status.failed {{ background: #f8d7da; color: #721c24; }}
        .status.skipped {{ background: #fff3cd; color: #856404; }}
        .security-alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 10px; }}
        .security-alert.high {{ background: #f8d7da; border-left-color: #dc3545; }}
        .security-alert.medium {{ background: #fff3cd; border-left-color: #ffc107; }}
        .security-alert.low {{ background: #d1ecf1; border-left-color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API自动化测试报告</h1>
            <p>生成时间: {self.report_data['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{summary['total']}</div>
            </div>
            <div class="summary-card passed">
                <h3>通过</h3>
                <div class="value">{summary['passed']}</div>
            </div>
            <div class="summary-card failed">
                <h3>失败</h3>
                <div class="value">{summary['failed']}</div>
            </div>
            <div class="summary-card skipped">
                <h3>跳过</h3>
                <div class="value">{summary['skipped']}</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value">{summary['pass_rate']}%</div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="value">{summary['total_duration']}s</div>
            </div>
        </div>
        
        <div class="section">
            <h2>测试详情</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>状态</th>
                        <th>耗时</th>
                        <th>错误信息</th>
                    </tr>
                </thead>
                <tbody>
        """

        for test in self.report_data["tests"]:
            status_class = test["status"]
            html += f"""
                    <tr>
                        <td>{test['name']}</td>
                        <td><span class="status {status_class}">{test['status'].upper()}</span></td>
                        <td>{test['duration']:.2f}s</td>
                        <td>{test.get('error', '-')}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        if self.report_data["security"]:
            html += """
        <div class="section">
            <h2>安全扫描结果</h2>
        """

            for vuln_type, vulnerabilities in self.report_data["security"].items():
                if vulnerabilities:
                    html += f"""
                    <div class="security-alert {vulnerabilities[0].get('severity', 'low').lower()}">
                        <strong>{vuln_type.upper()}</strong>: 发现 {len(vulnerabilities)} 个漏洞
                    </div>
            """

            html += "</div>"

        html += """
    </div>
</body>
</html>
        """

        return html

    def get_summary_text(self) -> str:
        self.generate_summary()
        summary = self.report_data["summary"]

        text = f"""
API测试报告摘要
{'=' * 50}
生成时间: {self.report_data['timestamp']}

测试统计:
- 总测试数: {summary['total']}
- 通过: {summary['passed']}
- 失败: {summary['failed']}
- 跳过: {summary['skipped']}
- 通过率: {summary['pass_rate']}%
- 总耗时: {summary['total_duration']}s
        """

        if self.report_data["security"]:
            total_vulns = sum(
                len(vulns) for vulns in self.report_data["security"].values()
            )
            text += f"\n\n安全扫描:\n- 发现漏洞总数: {total_vulns}\n"

            for vuln_type, vulnerabilities in self.report_data["security"].items():
                if vulnerabilities:
                    text += f"- {vuln_type}: {len(vulnerabilities)} 个\n"

        return text
