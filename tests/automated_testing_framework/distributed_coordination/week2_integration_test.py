#!/usr/bin/env python3
"""
PowerAutomation 分布式协调器集成测试
验证Week 2开发的所有组件集成

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import logging
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目路径
sys.path.append('/home/ubuntu/powerauto-distributed-coordinator/src')
sys.path.append('/home/ubuntu/powerauto.ai_0.53')

# 导入我们开发的组件
from coordinator.smart_scheduler import SmartSchedulingEngine, TaskCharacteristics, NodePerformanceMetrics
from coordinator.performance_engine import PerformanceOptimizationEngine
from integrations.test_architecture_integrator import TestArchitectureIntegrator, TestLevel
from integrations.ai_integrator import PowerAutoAIIntegrator, AIModuleType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PowerAutomation.IntegrationTest")

class Week2IntegrationTester:
    """Week 2集成测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.powerauto_repo_path = "/home/ubuntu/powerauto.ai_0.53"
        
        # 组件实例
        self.smart_scheduler = None
        self.performance_engine = None
        self.test_architecture_integrator = None
        self.ai_integrator = None
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """运行完整的集成测试"""
        logger.info("🚀 开始Week 2集成测试...")
        start_time = time.time()
        
        test_suite = [
            ("智能调度引擎测试", self.test_smart_scheduling_engine),
            ("性能优化引擎测试", self.test_performance_optimization_engine),
            ("十层测试架构集成测试", self.test_architecture_integration),
            ("AI组件集成测试", self.test_ai_integration),
            ("端到端集成测试", self.test_end_to_end_integration)
        ]
        
        for test_name, test_func in test_suite:
            logger.info(f"🔍 执行测试: {test_name}")
            try:
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"✅ {test_name} - 通过")
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"❌ {test_name} - 失败: {e}")
        
        execution_time = time.time() - start_time
        
        # 生成综合报告
        report = await self.generate_integration_report(execution_time)
        
        logger.info(f"🎯 Week 2集成测试完成 ({execution_time:.2f}s)")
        return report
    
    async def test_smart_scheduling_engine(self) -> Dict[str, Any]:
        """测试智能调度引擎"""
        logger.info("🧠 测试智能调度引擎...")
        
        # 初始化智能调度引擎
        self.smart_scheduler = SmartSchedulingEngine()
        await self.smart_scheduler.initialize()
        
        # 创建测试任务
        test_task = TaskCharacteristics(
            task_type="integration_test",
            test_level="level2",
            estimated_duration=300.0,
            resource_requirements={"cpu_cores": 2, "memory_gb": 4},
            priority=2,
            dependencies=[]
        )
        
        # 创建测试节点
        test_nodes = [
            NodePerformanceMetrics(
                node_id="test_node_1",
                timestamp=datetime.now(),
                cpu_usage=45.0,
                memory_usage=60.0,
                disk_io=20.0,
                network_io=15.0,
                task_completion_rate=0.95,
                average_execution_time=180.0,
                error_rate=0.02,
                concurrent_tasks=3
            ),
            NodePerformanceMetrics(
                node_id="test_node_2",
                timestamp=datetime.now(),
                cpu_usage=70.0,
                memory_usage=80.0,
                disk_io=40.0,
                network_io=30.0,
                task_completion_rate=0.88,
                average_execution_time=220.0,
                error_rate=0.05,
                concurrent_tasks=6
            )
        ]
        
        # 测试节点选择
        selected_node = await self.smart_scheduler.select_optimal_node(test_task, test_nodes)
        
        # 记录执行结果
        await self.smart_scheduler.record_execution_result(
            test_task, test_nodes[0], True, 280.0
        )
        
        # 获取调度洞察
        insights = await self.smart_scheduler.get_scheduling_insights()
        
        return {
            "selected_node": selected_node,
            "scheduling_insights": insights,
            "models_trained": {
                "performance_predictor": self.smart_scheduler.performance_predictor.is_trained,
                "task_matcher": self.smart_scheduler.task_matcher.is_trained
            }
        }
    
    async def test_performance_optimization_engine(self) -> Dict[str, Any]:
        """测试性能优化引擎"""
        logger.info("⚡ 测试性能优化引擎...")
        
        # 初始化性能优化引擎
        self.performance_engine = PerformanceOptimizationEngine(cache_size_mb=512)
        await self.performance_engine.initialize()
        
        # 创建测试任务
        test_tasks = [
            {
                "task_id": "test_task_1",
                "test_type": "unit_test",
                "test_level": "level1",
                "test_file": "/test/unit/test_example.py"
            },
            {
                "task_id": "test_task_2", 
                "test_type": "integration_test",
                "test_level": "level2",
                "test_file": "/test/integration/test_api.py"
            },
            {
                "task_id": "test_task_3",
                "test_type": "ui_test",
                "test_level": "level4",
                "test_file": "/test/ui/test_login.py"
            }
        ]
        
        # 测试执行优化
        optimized_groups, optimization_report = await self.performance_engine.optimize_test_execution(
            test_tasks, ["/src/example.py", "/src/api.py"]
        )
        
        # 测试缓存功能
        for task in test_tasks:
            await self.performance_engine.cache_task_result(
                task, 
                {"status": "passed", "duration": 120.0}, 
                120.0
            )
        
        # 获取性能报告
        performance_report = self.performance_engine.get_performance_report()
        
        return {
            "optimized_groups_count": len(optimized_groups),
            "optimization_report": optimization_report,
            "performance_report": performance_report,
            "cache_stats": self.performance_engine.cache.get_stats()
        }
    
    async def test_architecture_integration(self) -> Dict[str, Any]:
        """测试十层测试架构集成"""
        logger.info("🏗️ 测试十层测试架构集成...")
        
        # 初始化测试架构集成器
        self.test_architecture_integrator = TestArchitectureIntegrator(self.powerauto_repo_path)
        await self.test_architecture_integrator.initialize()
        
        # 测试能力查询
        level1_capability = self.test_architecture_integrator.get_test_capability(TestLevel.LEVEL1)
        level5_capability = self.test_architecture_integrator.get_test_capability(TestLevel.LEVEL5)
        
        # 测试依赖关系
        level7_dependencies = self.test_architecture_integrator.get_level_dependencies(TestLevel.LEVEL7)
        
        # 测试可执行级别
        completed_levels = {TestLevel.LEVEL1, TestLevel.LEVEL2, TestLevel.LEVEL3}
        executable_levels = self.test_architecture_integrator.get_executable_levels(completed_levels)
        
        # 测试资源需求计算
        resource_requirements = self.test_architecture_integrator.get_resource_requirements(
            [TestLevel.LEVEL1, TestLevel.LEVEL2, TestLevel.LEVEL5]
        )
        
        # 获取集成报告
        integration_report = await self.test_architecture_integrator.get_integration_report()
        
        return {
            "level1_capability": {
                "test_types": list(level1_capability.test_types) if level1_capability else [],
                "parallel_support": level1_capability.parallel_support if level1_capability else False
            },
            "level5_capability": {
                "test_types": list(level5_capability.test_types) if level5_capability else [],
                "parallel_support": level5_capability.parallel_support if level5_capability else False
            },
            "level7_dependencies": [dep.value for dep in level7_dependencies],
            "executable_levels": [level.value for level in executable_levels],
            "resource_requirements": resource_requirements,
            "integration_summary": integration_report["architecture_summary"]
        }
    
    async def test_ai_integration(self) -> Dict[str, Any]:
        """测试AI组件集成"""
        logger.info("🤖 测试AI组件集成...")
        
        # 初始化AI集成器
        self.ai_integrator = PowerAutoAIIntegrator(self.powerauto_repo_path)
        await self.ai_integrator.initialize()
        
        # 测试智能任务协调
        test_task_data = {
            "task_id": "ai_test_task_1",
            "task_type": "test_execution",
            "complexity": "medium",
            "privacy_level": "medium_sensitive",
            "resource_requirements": {"cpu_cores": 4, "memory_gb": 8}
        }
        
        coordination_result = await self.ai_integrator.coordinate_intelligent_task(test_task_data)
        
        # 测试部署任务协调
        deployment_task_data = {
            "task_id": "ai_deploy_task_1",
            "task_type": "deployment",
            "target_environment": "staging",
            "deployment_strategy": "blue_green"
        }
        
        deployment_result = await self.ai_integrator.coordinate_intelligent_task(deployment_task_data)
        
        # 获取集成状态
        integration_status = self.ai_integrator.get_integration_status()
        
        # 获取AI集成报告
        ai_report = await self.ai_integrator.get_ai_integration_report()
        
        return {
            "coordination_result": coordination_result,
            "deployment_result": deployment_result,
            "integration_status": integration_status,
            "ai_integration_summary": ai_report["integration_summary"]
        }
    
    async def test_end_to_end_integration(self) -> Dict[str, Any]:
        """测试端到端集成"""
        logger.info("🔄 测试端到端集成...")
        
        # 模拟完整的测试执行流程
        
        # 1. AI协调决定测试策略
        test_strategy_task = {
            "task_id": "e2e_strategy",
            "task_type": "test_strategy_planning",
            "test_levels": ["level1", "level2", "level3"],
            "complexity": "medium"
        }
        
        strategy_result = await self.ai_integrator.coordinate_intelligent_task(test_strategy_task)
        
        # 2. 测试架构集成器分析测试能力
        test_levels = [TestLevel.LEVEL1, TestLevel.LEVEL2, TestLevel.LEVEL3]
        resource_requirements = self.test_architecture_integrator.get_resource_requirements(test_levels)
        
        # 3. 性能引擎优化测试执行
        e2e_test_tasks = [
            {
                "task_id": "e2e_unit_tests",
                "test_type": "unit_test",
                "test_level": "level1",
                "estimated_duration": 180
            },
            {
                "task_id": "e2e_integration_tests",
                "test_type": "integration_test", 
                "test_level": "level2",
                "estimated_duration": 300
            },
            {
                "task_id": "e2e_api_tests",
                "test_type": "api_test",
                "test_level": "level3",
                "estimated_duration": 240
            }
        ]
        
        optimized_groups, optimization_report = await self.performance_engine.optimize_test_execution(e2e_test_tasks)
        
        # 4. 智能调度器选择执行节点
        test_task = TaskCharacteristics(
            task_type="e2e_test",
            test_level="level3",
            estimated_duration=600.0,
            resource_requirements=resource_requirements,
            priority=1,
            dependencies=[]
        )
        
        available_nodes = [
            NodePerformanceMetrics(
                node_id="e2e_node_1",
                timestamp=datetime.now(),
                cpu_usage=30.0,
                memory_usage=40.0,
                disk_io=10.0,
                network_io=5.0,
                task_completion_rate=0.98,
                average_execution_time=150.0,
                error_rate=0.01,
                concurrent_tasks=2
            )
        ]
        
        selected_node = await self.smart_scheduler.select_optimal_node(test_task, available_nodes)
        
        return {
            "strategy_coordination": strategy_result["integration_status"],
            "resource_requirements": resource_requirements,
            "optimization_applied": optimization_report["optimizations_applied"],
            "selected_execution_node": selected_node,
            "total_optimized_groups": len(optimized_groups),
            "end_to_end_status": "success"
        }
    
    async def generate_integration_report(self, execution_time: float) -> Dict[str, Any]:
        """生成集成报告"""
        
        # 计算成功率
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["status"] == "success")
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # 收集性能指标
        performance_summary = {}
        if self.performance_engine:
            performance_summary = self.performance_engine.get_performance_report()
        
        # 收集AI集成状态
        ai_integration_summary = {}
        if self.ai_integrator:
            ai_status = self.ai_integrator.get_integration_status()
            ai_integration_summary = {
                "total_modules": ai_status["total_modules"],
                "initialized_modules": ai_status["initialized_modules"],
                "integration_rate": ai_status["initialized_modules"] / ai_status["total_modules"] if ai_status["total_modules"] > 0 else 0
            }
        
        # 收集架构集成状态
        architecture_summary = {}
        if self.test_architecture_integrator:
            arch_report = await self.test_architecture_integrator.get_integration_report()
            architecture_summary = arch_report["architecture_summary"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time,
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate
            },
            "component_status": {
                "smart_scheduler": self.smart_scheduler is not None,
                "performance_engine": self.performance_engine is not None,
                "test_architecture_integrator": self.test_architecture_integrator is not None,
                "ai_integrator": self.ai_integrator is not None
            },
            "performance_summary": performance_summary,
            "ai_integration_summary": ai_integration_summary,
            "architecture_summary": architecture_summary,
            "detailed_test_results": self.test_results,
            "week2_completion_status": {
                "target_completion": "65%",
                "actual_completion": f"{min(100, success_rate * 100):.1f}%",
                "status": "success" if success_rate >= 0.8 else "needs_improvement"
            }
        }

async def main():
    """主函数"""
    tester = Week2IntegrationTester()
    report = await tester.run_integration_tests()
    
    # 保存报告
    report_file = "/home/ubuntu/week2_integration_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 Week 2集成测试报告已保存: {report_file}")
    print(f"📊 测试成功率: {report['test_summary']['success_rate']:.1%}")
    print(f"⚡ 完成度: {report['week2_completion_status']['actual_completion']}")
    print(f"✅ 状态: {report['week2_completion_status']['status']}")

if __name__ == "__main__":
    asyncio.run(main())

