import os
from pathlib import Path

import pytest

from config.settings import config
from utils.notification import NotificationSender, SlackNotifier
from utils.report_generator import TestReportGenerator


def pytest_configure(config_obj):
    config_obj.addinivalue_line("markers", "report: 生成测试报告")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if not hasattr(item.config, "_test_report_generator"):
            item.config._test_report_generator = TestReportGenerator()

        generator = item.config._test_report_generator

        test_name = f"{item.nodeid}"
        status = "passed" if report.passed else "failed"
        duration = report.duration
        error = str(report.longrepr) if report.failed else None

        generator.add_test_result(test_name, status, duration, error)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    if hasattr(session.config, "_test_report_generator"):
        generator = session.config._test_report_generator

        json_report = generator.save_json_report()
        html_report = generator.save_html_report()

        print(f"\n{'=' * 50}")
        print(generator.get_summary_text())
        print(f"{'=' * 50}")
        print(f"\n报告已生成:")
        print(f"  JSON: {json_report}")
        print(f"  HTML: {html_report}")

        if config.get("notification.enabled", False):
            summary = generator.report_data["summary"]
            summary["status"] = "通过" if exitstatus == 0 else "失败"
            summary["timestamp"] = generator.report_data["timestamp"]

            email_notifier = NotificationSender(config.get("notification.email", {}))
            email_notifier.send_test_report(summary)

            slack_webhook = config.get("notification.slack_webhook")
            if slack_webhook:
                slack_notifier = SlackNotifier(slack_webhook)
                slack_notifier.send_test_report(summary)
