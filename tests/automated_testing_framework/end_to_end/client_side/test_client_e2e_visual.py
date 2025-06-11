#!/usr/bin/env python3
"""
PowerAutomation 客户端端到端视觉测试

集成视觉验证的客户端端到端测试
"""

import pytest
import sys
from pathlib import Path

# 添加测试框架路径
sys.path.append(str(Path(__file__).parent.parent.parent))
from enhanced_test_preconditions import EnhancedPreconditionValidator
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig

class TestClientSideE2EVisual:
    """客户端端到端视觉测试"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.validator = EnhancedPreconditionValidator()
        cls.visual_config = VisualTestConfig(
            browser_type="chromium",
            headless=True,
            visual_threshold=0.05
        )
        cls.visual_tester = PowerAutomationVisualTester(config=cls.visual_config)
        
        cls.test_config = {
            "test_id": "CLIENT_E2E_VISUAL_001",
            "test_name": "客户端端到端视觉测试",
            "preconditions": {
                "platform": {
                    "required_platforms": ["windows", "macos", "linux"],
                    "preferred_platforms": ["linux"],
                    "excluded_platforms": []
                },
                "resources": {
                    "min_memory_gb": 4,
                    "min_cpu_cores": 2,
                    "gpu_required": False
                },
                "capabilities": ["ui_test", "automation_test", "visual_test"],
                "environment": {
                    "browser_support": "chromium"
                },
                "dependencies": ["playwright", "automation_engine"]
            }
        }
    
    def setup_method(self):
        """每个测试方法前的设置"""
        validation_result = self.validator.validate_preconditions(
            self.test_config["preconditions"]
        )
        
        if not validation_result["valid"]:
            pytest.skip(f"前置条件不满足: {validation_result['reason']}")
        
        # 启动视觉测试浏览器
        if not self.visual_tester.start_browser():
            pytest.skip("视觉测试浏览器启动失败")
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.visual_tester.stop_browser()
    
    def test_client_ui_visual_verification(self):
        """测试客户端UI视觉验证"""
        # 模拟客户端应用URL（实际应用中应该是真实的客户端界面）
        test_url = "https://www.google.com"  # 示例URL
        
        # 执行视觉测试
        result = self.visual_tester.run_visual_test(
            test_name="client_main_interface",
            url=test_url,
            test_id="CLIENT_UI_001",
            wait_selector="body"
        )
        
        assert result.passed or result.error == "基线图片已创建/更新", f"客户端UI视觉验证失败: {result.error}"
        
        if result.passed:
            print(f"✅ 客户端UI视觉验证通过 (差异: {result.mismatch_percentage:.2f}%)")
    
    def test_client_automation_workflow_visual(self):
        """测试客户端自动化工作流视觉验证"""
        # 模拟自动化工作流界面
        test_url = "https://github.com"  # 示例URL
        
        result = self.visual_tester.run_visual_test(
            test_name="client_automation_workflow",
            url=test_url,
            test_id="CLIENT_WORKFLOW_001",
            wait_selector="main"
        )
        
        assert result.passed or result.error == "基线图片已创建/更新", f"自动化工作流视觉验证失败: {result.error}"
        
        if result.passed:
            print(f"✅ 自动化工作流视觉验证通过 (差异: {result.mismatch_percentage:.2f}%)")
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 生成视觉测试报告
        try:
            cls.visual_tester.generate_visual_report("json")
            cls.visual_tester.generate_visual_report("html")
        except Exception as e:
            print(f"⚠️ 生成视觉测试报告失败: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
