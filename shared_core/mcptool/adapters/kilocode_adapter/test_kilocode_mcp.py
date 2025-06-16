#!/usr/bin/env python3
"""
KiloCode MCP 测试用例
供test框架读取和执行的标准化测试
"""

import unittest
import asyncio
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加路径以导入kilocode_mcp
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kilocode_mcp import KiloCodeMCP

class TestKiloCodeMCP(unittest.TestCase):
    """KiloCode MCP 测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.kilocode_mcp = KiloCodeMCP()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.kilocode_mcp.name, "kilocode_mcp")
        self.assertEqual(self.kilocode_mcp.version, "2.0.0")
        self.assertIsNotNone(self.kilocode_mcp.workflow_strategies)
    
    def test_get_capabilities(self):
        """测试获取能力信息"""
        capabilities = self.kilocode_mcp.get_capabilities()
        
        self.assertIn("creation_types", capabilities)
        self.assertIn("workflow_support", capabilities)
        self.assertIn("fallback_scenarios", capabilities)
    
    def test_get_routing_info(self):
        """测试获取路由信息"""
        routing_info = self.kilocode_mcp.get_routing_info()
        
        self.assertEqual(routing_info["mcp_id"], "kilocode_mcp")
        self.assertEqual(routing_info["mcp_type"], "fallback_creator")
        self.assertEqual(routing_info["priority"], "fallback")
    
    def test_ppt_creation(self):
        """测试PPT创建功能"""
        request = {
            "content": "为华为终端业务创建年终汇报PPT",
            "workflow_type": "requirements_analysis",
            "context": {}
        }
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "business_ppt")
        self.assertIn("slides_count", result)
        self.assertEqual(result["slides_count"], 8)
        self.assertIn("华为终端业务", result["content"])
    
    def test_snake_game_creation(self):
        """测试贪吃蛇游戏创建"""
        request = {
            "content": "创建贪吃蛇游戏",
            "workflow_type": "coding_implementation",
            "context": {}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "snake_game")
        self.assertEqual(result["language"], "python")
        self.assertIn("class SnakeGame", result["content"])
        self.assertIn("features", result)
    
    def test_python_script_creation(self):
        """测试Python脚本创建"""
        request = {
            "content": "创建数据处理脚本",
            "workflow_type": "coding_implementation",
            "context": {}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "python_script")
        self.assertEqual(result["language"], "python")
        self.assertIn("def main()", result["content"])
    
    def test_unsupported_workflow(self):
        """测试不支持的工作流"""
        request = {
            "content": "测试内容",
            "workflow_type": "unsupported_workflow",
            "context": {}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("不支持的工作流类型", result["error"])
    
    def test_all_workflow_strategies(self):
        """测试所有工作流策略"""
        workflows = [
            "requirements_analysis",
            "architecture_design",
            "coding_implementation", 
            "testing_verification",
            "deployment_release",
            "monitoring_operations"
        ]
        
        for workflow in workflows:
            with self.subTest(workflow=workflow):
                request = {
                    "content": f"测试{workflow}工作流",
                    "workflow_type": workflow,
                    "context": {}
                }
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
                loop.close()
                
                self.assertTrue(result["success"])
                self.assertIn("type", result)
                self.assertEqual(result["created_by"], "kilocode_mcp")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的请求格式
        invalid_request = {
            "workflow_type": "invalid_workflow_type_that_does_not_exist",
            "content": "测试错误处理"
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(invalid_request))
        loop.close()
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("不支持的工作流类型", result["error"])
    
    def test_metadata_inclusion(self):
        """测试元数据包含"""
        request = {
            "content": "测试元数据",
            "workflow_type": "coding_implementation",
            "context": {}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        # 检查必要的元数据
        self.assertIn("created_by", result)
        self.assertIn("version", result)
        self.assertIn("timestamp", result)
        self.assertIn("workflow_type", result)
        
        self.assertEqual(result["created_by"], "kilocode_mcp")
        self.assertEqual(result["version"], "2.0.0")
        self.assertEqual(result["workflow_type"], "coding_implementation")

class TestKiloCodeMCPIntegration(unittest.TestCase):
    """KiloCode MCP 集成测试"""
    
    def setUp(self):
        """集成测试前置设置"""
        self.kilocode_mcp = KiloCodeMCP()
    
    def test_workflow_integration_compatibility(self):
        """测试与工作流系统的兼容性"""
        # 测试配置接口
        capabilities = self.kilocode_mcp.get_capabilities()
        routing_info = self.kilocode_mcp.get_routing_info()
        
        # 验证工作流系统需要的字段
        required_capability_fields = ["creation_types", "workflow_support", "fallback_scenarios"]
        for field in required_capability_fields:
            self.assertIn(field, capabilities)
        
        required_routing_fields = ["mcp_id", "mcp_type", "priority", "supported_workflows"]
        for field in required_routing_fields:
            self.assertIn(field, routing_info)
    
    def test_fallback_scenario_coverage(self):
        """测试兜底场景覆盖"""
        capabilities = self.kilocode_mcp.get_capabilities()
        fallback_scenarios = capabilities["fallback_scenarios"]
        
        # 确保所有工作流都有兜底场景
        supported_workflows = capabilities["workflow_support"]
        for workflow in supported_workflows:
            self.assertIn(workflow, fallback_scenarios)
            self.assertIsInstance(fallback_scenarios[workflow], list)
            self.assertGreater(len(fallback_scenarios[workflow]), 0)
    
    def test_performance_requirements(self):
        """测试性能要求"""
        import time
        
        request = {
            "content": "性能测试请求",
            "workflow_type": "coding_implementation",
            "context": {}
        }
        
        # 测试响应时间
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.kilocode_mcp.process_request(request))
        loop.close()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 响应时间应该在合理范围内（5秒以内）
        self.assertLess(response_time, 5.0)
        self.assertTrue(result["success"])

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加基础测试
    test_suite.addTest(unittest.makeSuite(TestKiloCodeMCP))
    
    # 添加集成测试
    test_suite.addTest(unittest.makeSuite(TestKiloCodeMCPIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 运行KiloCode MCP测试用例")
    print("=" * 50)
    
    success = run_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")
    
    print(f"📊 测试框架兼容性: {'✅ 兼容' if success else '❌ 需要修复'}")
    
    # 返回退出码供test框架使用
    exit(0 if success else 1)

