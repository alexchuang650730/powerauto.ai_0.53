#!/usr/bin/env python3
"""
PowerAutomation 端到端测试运行器

统一管理和执行所有端到端测试
"""

import os
import sys
import yaml
import pytest
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class E2ETestRunner:
    """端到端测试运行器"""
    
    def __init__(self):
        self.e2e_dir = Path(__file__).parent
        self.config_path = self.e2e_dir / "configs" / "e2e_config.yaml"
        self.config = self._load_config()
        
        # 创建报告目录
        self.report_dir = self.e2e_dir / "e2e_reports"
        self.report_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def run_all_e2e_tests(self) -> bool:
        """运行所有端到端测试"""
        print("🚀 开始执行PowerAutomation端到端测试套件...")
        
        test_config = self.config.get("end_to_end_tests", {})
        execution_order = test_config.get("execution_order", [])
        
        results = {}
        overall_success = True
        
        for test_level in execution_order:
            print(f"\n📋 执行 {test_level} 测试...")
            
            result = self._run_test_level(test_level)
            results[test_level] = result
            
            if not result["success"]:
                overall_success = False
                print(f"❌ {test_level} 测试失败")
            else:
                print(f"✅ {test_level} 测试成功")
        
        # 生成综合报告
        self._generate_comprehensive_report(results)
        
        if overall_success:
            print("\n🎉 所有端到端测试执行成功！")
        else:
            print("\n⚠️ 部分端到端测试执行失败，请查看详细报告")
        
        return overall_success
    
    def _run_test_level(self, test_level: str) -> Dict[str, Any]:
        """运行特定级别的测试"""
        test_dir = self.e2e_dir / test_level
        
        if not test_dir.exists():
            return {
                "success": False,
                "error": f"测试目录不存在: {test_dir}",
                "execution_time": 0
            }
        
        # 构建pytest参数
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"{test_level}_report_{timestamp}.html"
        
        pytest_args = [
            str(test_dir),
            "-v",
            "--tb=short",
            "--capture=no",
            f"--html={report_file}",
            "--self-contained-html"
        ]
        
        try:
            start_time = datetime.now()
            result = pytest.main(pytest_args)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "success": result == 0,
                "exit_code": result,
                "execution_time": execution_time,
                "report_file": str(report_file),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    def run_specific_test(self, test_level: str, test_name: str = None) -> bool:
        """运行特定的测试"""
        test_dir = self.e2e_dir / test_level
        
        if test_name:
            test_file = test_dir / f"test_{test_name}.py"
            if not test_file.exists():
                print(f"❌ 测试文件不存在: {test_file}")
                return False
            target = str(test_file)
        else:
            target = str(test_dir)
        
        pytest_args = [target, "-v"]
        result = pytest.main(pytest_args)
        
        return result == 0
    
    def _generate_comprehensive_report(self, results: Dict[str, Any]):
        """生成综合报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_data = {
            "execution_timestamp": timestamp,
            "overall_success": all(r.get("success", False) for r in results.values()),
            "test_results": results,
            "summary": {
                "total_test_levels": len(results),
                "successful_levels": sum(1 for r in results.values() if r.get("success", False)),
                "failed_levels": sum(1 for r in results.values() if not r.get("success", False)),
                "total_execution_time": sum(r.get("execution_time", 0) for r in results.values())
            }
        }
        
        # 保存JSON报告
        json_report_path = self.report_dir / f"e2e_comprehensive_report_{timestamp}.json"
        import json
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 综合报告已生成: {json_report_path}")

if __name__ == "__main__":
    runner = E2ETestRunner()
    
    if len(sys.argv) > 1:
        # 运行特定测试
        test_level = sys.argv[1]
        test_name = sys.argv[2] if len(sys.argv) > 2 else None
        runner.run_specific_test(test_level, test_name)
    else:
        # 运行所有测试
        runner.run_all_e2e_tests()
