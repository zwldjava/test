#!/usr/bin/env python3
"""
生成 Allure HTML 报告的脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def generate_allure_report():
    """生成 Allure HTML 报告"""
    # 设置路径
    project_root = Path(__file__).parent
    allure_results = project_root / "allure-results"
    allure_report = project_root / "allure-report"
    
    # 检查 allure-results 目录是否存在
    if not allure_results.exists():
        print(f"❌ 错误: {allure_results} 目录不存在，请先运行测试生成测试数据")
        return False
    
    # 检查是否有测试数据
    if not list(allure_results.glob("*")):
        print(f"❌ 错误: {allure_results} 目录为空，请先运行测试生成测试数据")
        return False
    
    # 尝试查找 allure 命令
    allure_cmd = find_allure_command()
    if not allure_cmd:
        print("❌ 错误: 未找到 allure 命令行工具")
        print("请安装 Allure 命令行工具:")
        print("  1. 下载: https://github.com/allure-framework/allure2/releases")
        print("  2. 解压并将 bin 目录添加到 PATH")
        print("  3. 或使用包管理器安装: npm install -g allure-commandline")
        return False
    
    # 清理旧的报告目录
    if allure_report.exists():
        shutil.rmtree(allure_report)
    
    # 生成报告
    cmd = [allure_cmd, "generate", str(allure_results), "-o", str(allure_report), "--clean"]
    print(f"🚀 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            print(f"✅ Allure 报告已生成: {allure_report}")
            print(f"🌐 请在浏览器中打开: {allure_report}/index.html")
            return True
        else:
            print(f"❌ 生成报告失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False

def find_allure_command():
    """查找 allure 命令"""
    # 尝试直接使用 allure 命令
    if shutil.which("allure"):
        return "allure"
    
    # 尝试常见的安装路径
    common_paths = [
        r"C:\Program Files\allure\bin\allure.bat",
        r"C:\Program Files (x86)\allure\bin\allure.bat",
        r"C:\tools\allure\bin\allure.bat",
        os.path.expanduser("~/scoop/apps/allure/current/allure.bat"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # 尝试使用 npx
    if shutil.which("npx"):
        return "npx allure-commandline"
    
    return None

if __name__ == "__main__":
    success = generate_allure_report()
    sys.exit(0 if success else 1)