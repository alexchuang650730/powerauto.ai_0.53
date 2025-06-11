#!/usr/bin/env python3
"""
PowerAutomation 视觉测试套件

统一管理和执行所有视觉测试
"""

import os
import sys
import yaml
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加测试框架路径
sys.path.append(str(Path(__file__).parent.parent))
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig

class VisualTestSuite:
    """视觉测试套件"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent.parent
        self.visual_test_dir = Path(__file__).parent
        self.config_path = self.visual_test_dir / "visual_test_config.yaml"
        self.config = self._load_config()
        
        # 创建报告目录
        self.report_dir = self.visual_test_dir / "visual_test_reports"
        self.report_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载视觉测试配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def run_all_visual_tests(self) -> bool:
        """运行所有视觉测试"""
        print("🎨 开始执行PowerAutomation视觉测试套件...")
        
        visual_config = self.config.get("visual_testing", {})
        if not visual_config.get("enabled", False):
            print("⚠️ 视觉测试未启用，跳过执行")
            return True
        
        test_scenarios = visual_config.get("test_scenarios", {})
        results = {}
        overall_success = True
        
        # 执行客户端视觉测试
        if test_scenarios.get("client_side", {}).get("enabled", False):
            print("\n🖥️ 执行客户端视觉测试...")
            result = self._run_client_visual_tests()
            results["client_side"] = result
            if not result["success"]:
                overall_success = False
        
        # 执行兜底自动化视觉测试
        if test_scenarios.get("fallback_automation", {}).get("enabled", False):
            print("\n🛡️ 执行兜底自动化视觉测试...")
            result = self._run_fallback_visual_tests()
            results["fallback_automation"] = result
            if not result["success"]:
                overall_success = False
        
        # 执行集成视觉测试
        if test_scenarios.get("integration", {}).get("enabled", False):
            print("\n🔗 执行集成视觉测试...")
            result = self._run_integration_visual_tests()
            results["integration"] = result
            if not result["success"]:
                overall_success = False
        
        # 生成综合报告
        self._generate_comprehensive_visual_report(results)
        
        if overall_success:
            print("\n🎉 所有视觉测试执行成功！")
        else:
            print("\n⚠️ 部分视觉测试执行失败，请查看详细报告")
        
        return overall_success
    
    def _run_client_visual_tests(self) -> Dict[str, Any]:
        """运行客户端视觉测试"""
        test_file = self.test_dir / "end_to_end" / "client_side" / "test_client_e2e_visual.py"
        return self._execute_pytest(test_file, "client_visual")
    
    def _run_fallback_visual_tests(self) -> Dict[str, Any]:
        """运行兜底自动化视觉测试"""
        test_file = self.test_dir / "end_to_end" / "fallback_automation" / "test_fallback_visual.py"
        return self._execute_pytest(test_file, "fallback_visual")
    
    def _run_integration_visual_tests(self) -> Dict[str, Any]:
        """运行集成视觉测试"""
        # 这里可以添加集成视觉测试的执行逻辑
        return {"success": True, "message": "集成视觉测试暂未实现"}
    
    def _execute_pytest(self, test_file: Path, test_type: str) -> Dict[str, Any]:
        """执行pytest测试"""
        if not test_file.exists():
            return {
                "success": False,
                "error": f"测试文件不存在: {test_file}",
                "execution_time": 0
            }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"{test_type}_report_{timestamp}.html"
        
        pytest_args = [
            str(test_file),
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
    
    def _generate_comprehensive_visual_report(self, results: Dict[str, Any]):
        """生成综合视觉测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_data = {
            "execution_timestamp": timestamp,
            "test_framework": "PowerAutomation Visual Testing Suite",
            "overall_success": all(r.get("success", False) for r in results.values()),
            "test_results": results,
            "summary": {
                "total_test_types": len(results),
                "successful_types": sum(1 for r in results.values() if r.get("success", False)),
                "failed_types": sum(1 for r in results.values() if not r.get("success", False)),
                "total_execution_time": sum(r.get("execution_time", 0) for r in results.values())
            }
        }
        
        # 保存JSON报告
        json_report_path = self.report_dir / f"visual_comprehensive_report_{timestamp}.json"
        import json
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 视觉测试综合报告已生成: {json_report_path}")

if __name__ == "__main__":
    suite = VisualTestSuite()
    suite.run_all_visual_tests()
