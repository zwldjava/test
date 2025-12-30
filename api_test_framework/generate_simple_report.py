#!/usr/bin/env python3
"""
从 allure-results 生成简单的 HTML 报告
"""
import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def parse_allure_results(results_dir):
    """解析 allure-results 目录中的测试结果"""
    results_dir = Path(results_dir)
    
    # 收集所有 result.json 文件
    result_files = list(results_dir.glob("*-result.json"))
    
    test_cases = []
    
    for result_file in result_files:
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                test_cases.append(data)
        except Exception as e:
            print(f"读取文件 {result_file} 时出错: {e}")
    
    return test_cases

def generate_html_report(test_cases, output_file):
    """生成 HTML 报告"""
    # 统计数据
    total = len(test_cases)
    passed = sum(1 for tc in test_cases if tc.get('status') == 'passed')
    failed = sum(1 for tc in test_cases if tc.get('status') == 'failed')
    broken = sum(1 for tc in test_cases if tc.get('status') == 'broken')
    skipped = sum(1 for tc in test_cases if tc.get('status') == 'skipped')
    
    # 按状态分组
    by_status = defaultdict(list)
    for tc in test_cases:
        status = tc.get('status', 'unknown')
        by_status[status].append(tc)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - Allure</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card h3 {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-card.total .number {{ color: #667eea; }}
        .stat-card.passed .number {{ color: #28a745; }}
        .stat-card.failed .number {{ color: #dc3545; }}
        .stat-card.broken .number {{ color: #ffc107; }}
        .stat-card.skipped .number {{ color: #6c757d; }}
        .progress {{
            padding: 30px;
        }}
        .progress-bar {{
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            display: flex;
        }}
        .progress-segment {{
            height: 100%;
            transition: width 0.5s;
        }}
        .progress-segment.passed {{ background: #28a745; }}
        .progress-segment.failed {{ background: #dc3545; }}
        .progress-segment.broken {{ background: #ffc107; }}
        .progress-segment.skipped {{ background: #6c757d; }}
        .test-cases {{
            padding: 30px;
        }}
        .test-cases h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        .test-case {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin-bottom: 15px;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        .test-case:hover {{
            background: #e9ecef;
        }}
        .test-case.passed {{ border-left-color: #28a745; }}
        .test-case.failed {{ border-left-color: #dc3545; }}
        .test-case.broken {{ border-left-color: #ffc107; }}
        .test-case.skipped {{ border-left-color: #6c757d; }}
        .test-case-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .test-case-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
        }}
        .test-case-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .test-case-status.passed {{ background: #d4edda; color: #155724; }}
        .test-case-status.failed {{ background: #f8d7da; color: #721c24; }}
        .test-case-status.broken {{ background: #fff3cd; color: #856404; }}
        .test-case-status.skipped {{ background: #e2e3e5; color: #383d41; }}
        .test-case-details {{
            font-size: 0.9em;
            color: #666;
        }}
        .test-case-error {{
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 测试报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card total">
                <h3>总计</h3>
                <div class="number">{total}</div>
            </div>
            <div class="stat-card passed">
                <h3>通过</h3>
                <div class="number">{passed}</div>
            </div>
            <div class="stat-card failed">
                <h3>失败</h3>
                <div class="number">{failed}</div>
            </div>
            <div class="stat-card broken">
                <h3>损坏</h3>
                <div class="number">{broken}</div>
            </div>
            <div class="stat-card skipped">
                <h3>跳过</h3>
                <div class="number">{skipped}</div>
            </div>
        </div>
        
        <div class="progress">
            <div class="progress-bar">
                <div class="progress-segment passed" style="width: {passed/total*100 if total > 0 else 0}%"></div>
                <div class="progress-segment failed" style="width: {failed/total*100 if total > 0 else 0}%"></div>
                <div class="progress-segment broken" style="width: {broken/total*100 if total > 0 else 0}%"></div>
                <div class="progress-segment skipped" style="width: {skipped/total*100 if total > 0 else 0}%"></div>
            </div>
        </div>
        
        <div class="test-cases">
            <h2>测试用例详情</h2>
"""
    
    # 添加测试用例详情
    for tc in test_cases:
        status = tc.get('status', 'unknown')
        name = tc.get('name', tc.get('fullName', '未知测试用例'))
        duration = tc.get('time', {}).get('duration', 0) / 1000 if tc.get('time') else 0
        
        html += f"""
            <div class="test-case {status}">
                <div class="test-case-header">
                    <div class="test-case-name">{name}</div>
                    <div class="test-case-status {status}">{status}</div>
                </div>
                <div class="test-case-details">
                    耗时: {duration:.2f}s
                </div>
"""
        
        # 如果有错误信息
        if status in ['failed', 'broken'] and 'statusDetails' in tc:
            error_msg = tc['statusDetails'].get('message', '')
            if error_msg:
                html += f"""
                <div class="test-case-error">{error_msg}</div>
"""
        
        html += """
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>由 Allure 测试框架生成 | 共 {total} 个测试用例</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML 报告已生成: {output_file}")

def main():
    """主函数"""
    project_root = Path(__file__).parent
    results_dir = project_root / "allure-results"
    output_file = project_root / "allure-report" / "index.html"
    
    # 创建输出目录
    output_file.parent.mkdir(exist_ok=True)
    
    # 解析测试结果
    print("📊 正在解析测试结果...")
    test_cases = parse_allure_results(results_dir)
    
    if not test_cases:
        print("❌ 未找到测试结果，请先运行测试")
        return False
    
    print(f"✅ 找到 {len(test_cases)} 个测试用例")
    
    # 生成 HTML 报告
    print("📝 正在生成 HTML 报告...")
    generate_html_report(test_cases, output_file)
    
    print(f"🌐 请在浏览器中打开: {output_file}")
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)