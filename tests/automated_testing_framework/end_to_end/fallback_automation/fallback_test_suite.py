#!/usr/bin/env python3
"""
PowerAutomation 兜底自动化测试套件

集成所有兜底自动化测试用例的执行套件
"""

import pytest
import sys
from pathlib import Path

# 添加测试框架路径
sys.path.append(str(Path(__file__).parent.parent.parent))

class FallbackTestSuite:
    """兜底自动化测试套件"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.test_files = list(self.test_dir.glob("test_*_op_*.py"))
    
    def run_all_tests(self):
        """运行所有兜底测试"""
        print("🚀 开始执行兜底自动化测试套件...")
        
        # 构建pytest参数
        pytest_args = [
            str(self.test_dir),
            "-v",
            "--tb=short",
            "--capture=no",
            f"--html={self.test_dir}/fallback_test_report.html",
            "--self-contained-html"
        ]
        
        # 执行测试
        result = pytest.main(pytest_args)
        
        if result == 0:
            print("✅ 所有兜底测试执行成功")
        else:
            print(f"❌ 兜底测试执行失败，退出代码: {result}")
        
        return result
    
    def run_specific_test(self, test_id: str):
        """运行特定的兜底测试"""
        test_file = self.test_dir / f"test_{test_id.lower()}.py"
        
        if not test_file.exists():
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        pytest_args = [str(test_file), "-v"]
        result = pytest.main(pytest_args)
        
        return result == 0

if __name__ == "__main__":
    suite = FallbackTestSuite()
    suite.run_all_tests()
