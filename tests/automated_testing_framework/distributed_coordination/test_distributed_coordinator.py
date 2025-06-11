#!/usr/bin/env python3
"""
PowerAutomation 分布式协调器测试套件
集成到现有测试框架的分布式协调器测试

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import unittest
import logging
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# 导入分布式协调器组件
try:
    from shared_core.engines.distributed_coordinator import (
        DistributedTestCoordinator,
        SmartSchedulingEngine,
        PerformanceOptimizationEngine
    )
    from tests.automated_testing_framework.integrations.test_architecture_integrator import (
        TestArchitectureIntegrator,
        TestLevel
    )
    from tests.automated_testing_framework.integrations.ai_integrator import (
        PowerAutoAIIntegrator
    )
    from shared_core.mcptool.adapters.distributed_test_coordinator_mcp import (
        DistributedTestCoordinatorMCP
    )
except ImportError as e:
    logging.warning(f"导入分布式协调器组件失败: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PowerAutomation.DistributedCoordinatorTests")

class TestDistributedCoordinator(unittest.TestCase):
    """分布式协调器核心测试"""
    
    def setUp(self):
        """测试设置"""
        self.coordinator = DistributedTestCoordinator()
    
    async def test_coordinator_initialization(self):
        """测试协调器初始化"""
        await self.coordinator.initialize()
        status = await self.coordinator.get_status()
        self.assertIsNotNone(status)
        self.assertEqual(status.get("status"), "active")
    
    def test_coordinator_sync(self):
        """同步测试协调器"""
        asyncio.run(self.test_coordinator_initialization())

class TestSmartScheduler(unittest.TestCase):
    """智能调度器测试"""
    
    def setUp(self):
        """测试设置"""
        self.scheduler = SmartSchedulingEngine()
    
    async def test_scheduler_initialization(self):
        """测试调度器初始化"""
        await self.scheduler.initialize()
        insights = await self.scheduler.get_scheduling_insights()
        self.assertIsNotNone(insights)
        self.assertIn("models_trained", insights)
    
    def test_scheduler_sync(self):
        """同步测试调度器"""
        asyncio.run(self.test_scheduler_initialization())

class TestPerformanceEngine(unittest.TestCase):
    """性能优化引擎测试"""
    
    def setUp(self):
        """测试设置"""
        self.engine = PerformanceOptimizationEngine()
    
    async def test_engine_initialization(self):
        """测试引擎初始化"""
        await self.engine.initialize()
        report = self.engine.get_performance_report()
        self.assertIsNotNone(report)
        self.assertIn("cache_performance", report)
    
    def test_engine_sync(self):
        """同步测试引擎"""
        asyncio.run(self.test_engine_initialization())

class TestArchitectureIntegration(unittest.TestCase):
    """测试架构集成测试"""
    
    def setUp(self):
        """测试设置"""
        self.integrator = TestArchitectureIntegrator(str(project_root))
    
    async def test_integrator_initialization(self):
        """测试集成器初始化"""
        await self.integrator.initialize()
        
        # 测试能力查询
        level1_capability = self.integrator.get_test_capability(TestLevel.LEVEL1)
        self.assertIsNotNone(level1_capability)
        
        # 测试依赖关系
        dependencies = self.integrator.get_level_dependencies(TestLevel.LEVEL3)
        self.assertIsInstance(dependencies, list)
    
    def test_integrator_sync(self):
        """同步测试集成器"""
        asyncio.run(self.test_integrator_initialization())

class TestAIIntegration(unittest.TestCase):
    """AI集成测试"""
    
    def setUp(self):
        """测试设置"""
        self.ai_integrator = PowerAutoAIIntegrator(str(project_root))
    
    async def test_ai_integrator_initialization(self):
        """测试AI集成器初始化"""
        await self.ai_integrator.initialize()
        status = self.ai_integrator.get_integration_status()
        self.assertIsNotNone(status)
        self.assertIn("total_modules", status)
    
    def test_ai_integrator_sync(self):
        """同步测试AI集成器"""
        asyncio.run(self.test_ai_integrator_initialization())

class TestMCPAdapter(unittest.TestCase):
    """MCP适配器测试"""
    
    def setUp(self):
        """测试设置"""
        self.mcp_adapter = DistributedTestCoordinatorMCP()
    
    async def test_mcp_initialization(self):
        """测试MCP适配器初始化"""
        from shared_core.mcptool.adapters.distributed_test_coordinator_mcp import MCPRequest
        
        # 创建初始化请求
        init_request = MCPRequest(
            method="coordinator.initialize",
            params={"powerauto_repo_path": str(project_root)},
            id="test_init"
        )
        
        # 处理请求
        response = await self.mcp_adapter.handle_request(init_request)
        self.assertIsNotNone(response)
        self.assertIsNone(response.error)
        self.assertEqual(response.result.get("status"), "success")
    
    async def test_mcp_health_check(self):
        """测试MCP健康检查"""
        from shared_core.mcptool.adapters.distributed_test_coordinator_mcp import MCPRequest
        
        health_request = MCPRequest(
            method="system.health_check",
            params={},
            id="test_health"
        )
        
        response = await self.mcp_adapter.handle_request(health_request)
        self.assertIsNotNone(response)
        self.assertIn("overall_status", response.result)
    
    def test_mcp_sync(self):
        """同步测试MCP适配器"""
        asyncio.run(self.test_mcp_initialization())
        asyncio.run(self.test_mcp_health_check())

class TestEndToEndIntegration(unittest.TestCase):
    """端到端集成测试"""
    
    async def test_full_integration_workflow(self):
        """测试完整集成工作流"""
        logger.info("🚀 开始端到端集成测试...")
        
        # 1. 初始化MCP适配器
        mcp_adapter = DistributedTestCoordinatorMCP()
        
        from shared_core.mcptool.adapters.distributed_test_coordinator_mcp import MCPRequest
        
        init_request = MCPRequest(
            method="coordinator.initialize",
            params={"powerauto_repo_path": str(project_root)},
            id="e2e_init"
        )
        
        init_response = await mcp_adapter.handle_request(init_request)
        self.assertEqual(init_response.result.get("status"), "success")
        
        # 2. 获取系统状态
        status_request = MCPRequest(
            method="coordinator.get_status",
            params={},
            id="e2e_status"
        )
        
        status_response = await mcp_adapter.handle_request(status_request)
        self.assertEqual(status_response.result.get("status"), "active")
        
        # 3. 获取性能报告
        perf_request = MCPRequest(
            method="performance.get_report",
            params={},
            id="e2e_perf"
        )
        
        perf_response = await mcp_adapter.handle_request(perf_request)
        self.assertEqual(perf_response.result.get("status"), "success")
        
        # 4. 获取AI集成状态
        ai_request = MCPRequest(
            method="ai.get_integration_status",
            params={},
            id="e2e_ai"
        )
        
        ai_response = await mcp_adapter.handle_request(ai_request)
        self.assertEqual(ai_response.result.get("status"), "success")
        
        logger.info("✅ 端到端集成测试完成")
    
    def test_e2e_sync(self):
        """同步端到端测试"""
        asyncio.run(self.test_full_integration_workflow())

def run_distributed_coordinator_tests():
    """运行分布式协调器测试套件"""
    logger.info("🧪 开始运行分布式协调器测试套件...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDistributedCoordinator,
        TestSmartScheduler,
        TestPerformanceEngine,
        TestArchitectureIntegration,
        TestAIIntegration,
        TestMCPAdapter,
        TestEndToEndIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 报告结果
    logger.info(f"📊 测试结果: 运行 {result.testsRun} 个测试")
    logger.info(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"❌ 失败: {len(result.failures)}")
    logger.info(f"🚨 错误: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_distributed_coordinator_tests()
    sys.exit(0 if success else 1)

