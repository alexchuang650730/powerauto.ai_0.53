#!/usr/bin/env python3
"""
PowerAutomation 十层测试架构集成器
完整集成Level 1-10测试架构到分布式协调器

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import logging
import json
import os
import importlib.util
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger("PowerAutomation.TestArchitectureIntegrator")

class TestLevel(Enum):
    """测试级别枚举"""
    LEVEL1 = "level1"  # 单元测试层
    LEVEL2 = "level2"  # 集成测试层
    LEVEL3 = "level3"  # API测试层
    LEVEL4 = "level4"  # UI测试层
    LEVEL5 = "level5"  # 性能测试层
    LEVEL6 = "level6"  # 安全测试层
    LEVEL7 = "level7"  # 端到端测试层
    LEVEL8 = "level8"  # 兼容性测试层
    LEVEL9 = "level9"  # 压力测试层
    LEVEL10 = "level10"  # 业务流程测试层

@dataclass
class TestCapability:
    """测试能力定义"""
    level: TestLevel
    test_types: Set[str]
    required_resources: Dict[str, Any]
    execution_patterns: List[str]
    dependencies: List[TestLevel]
    parallel_support: bool
    estimated_duration_range: Tuple[int, int]  # 秒
    
@dataclass
class TestSuite:
    """测试套件"""
    suite_id: str
    level: TestLevel
    test_files: List[str]
    configuration: Dict[str, Any]
    execution_order: List[str]
    parallel_groups: List[List[str]]
    resource_requirements: Dict[str, Any]

class TestArchitectureIntegrator:
    """十层测试架构集成器"""
    
    def __init__(self, powerauto_repo_path: str):
        self.repo_path = Path(powerauto_repo_path)
        self.test_framework_path = self.repo_path / "tests" / "automated_testing_framework"
        
        # 测试能力映射
        self.test_capabilities: Dict[TestLevel, TestCapability] = {}
        
        # 测试套件注册表
        self.test_suites: Dict[str, TestSuite] = {}
        
        # 级别依赖关系
        self.level_dependencies = self._build_level_dependencies()
        
        # 已发现的测试文件
        self.discovered_tests: Dict[TestLevel, List[str]] = {}
        
    def _build_level_dependencies(self) -> Dict[TestLevel, List[TestLevel]]:
        """构建测试级别依赖关系"""
        return {
            TestLevel.LEVEL1: [],  # 单元测试无依赖
            TestLevel.LEVEL2: [TestLevel.LEVEL1],  # 集成测试依赖单元测试
            TestLevel.LEVEL3: [TestLevel.LEVEL1, TestLevel.LEVEL2],  # API测试
            TestLevel.LEVEL4: [TestLevel.LEVEL2, TestLevel.LEVEL3],  # UI测试
            TestLevel.LEVEL5: [TestLevel.LEVEL1, TestLevel.LEVEL2],  # 性能测试
            TestLevel.LEVEL6: [TestLevel.LEVEL3, TestLevel.LEVEL4],  # 安全测试
            TestLevel.LEVEL7: [TestLevel.LEVEL2, TestLevel.LEVEL3, TestLevel.LEVEL4],  # 端到端
            TestLevel.LEVEL8: [TestLevel.LEVEL4, TestLevel.LEVEL7],  # 兼容性测试
            TestLevel.LEVEL9: [TestLevel.LEVEL5, TestLevel.LEVEL7],  # 压力测试
            TestLevel.LEVEL10: [TestLevel.LEVEL7, TestLevel.LEVEL8]  # 业务流程测试
        }
    
    async def initialize(self):
        """初始化测试架构集成器"""
        logger.info("🔧 初始化十层测试架构集成器...")
        
        # 发现测试文件
        await self._discover_test_files()
        
        # 初始化测试能力
        await self._initialize_test_capabilities()
        
        # 构建测试套件
        await self._build_test_suites()
        
        # 验证架构完整性
        await self._validate_architecture()
        
        logger.info("✅ 十层测试架构集成器初始化完成")
    
    async def _discover_test_files(self):
        """发现所有测试文件"""
        logger.info("🔍 发现测试文件...")
        
        for level in TestLevel:
            level_path = self.test_framework_path / level.value
            if level_path.exists():
                test_files = []
                
                # 递归查找Python测试文件
                for file_path in level_path.rglob("*.py"):
                    if file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
                        test_files.append(str(file_path.relative_to(self.test_framework_path)))
                
                self.discovered_tests[level] = test_files
                logger.info(f"  📁 {level.value}: 发现 {len(test_files)} 个测试文件")
    
    async def _initialize_test_capabilities(self):
        """初始化测试能力定义"""
        logger.info("⚙️ 初始化测试能力...")
        
        # Level 1: 单元测试
        self.test_capabilities[TestLevel.LEVEL1] = TestCapability(
            level=TestLevel.LEVEL1,
            test_types={"unit_test", "component_test", "module_test"},
            required_resources={"cpu_cores": 1, "memory_gb": 2, "disk_gb": 1},
            execution_patterns=["parallel", "isolated"],
            dependencies=[],
            parallel_support=True,
            estimated_duration_range=(10, 300)
        )
        
        # Level 2: 集成测试
        self.test_capabilities[TestLevel.LEVEL2] = TestCapability(
            level=TestLevel.LEVEL2,
            test_types={"integration_test", "service_test", "mcp_integration"},
            required_resources={"cpu_cores": 2, "memory_gb": 4, "disk_gb": 2},
            execution_patterns=["sequential", "grouped_parallel"],
            dependencies=[TestLevel.LEVEL1],
            parallel_support=True,
            estimated_duration_range=(60, 900)
        )
        
        # Level 3: API测试
        self.test_capabilities[TestLevel.LEVEL3] = TestCapability(
            level=TestLevel.LEVEL3,
            test_types={"api_test", "rest_test", "graphql_test"},
            required_resources={"cpu_cores": 2, "memory_gb": 4, "network": True},
            execution_patterns=["parallel", "load_balanced"],
            dependencies=[TestLevel.LEVEL1, TestLevel.LEVEL2],
            parallel_support=True,
            estimated_duration_range=(30, 600)
        )
        
        # Level 4: UI测试
        self.test_capabilities[TestLevel.LEVEL4] = TestCapability(
            level=TestLevel.LEVEL4,
            test_types={"ui_test", "browser_test", "mobile_test"},
            required_resources={"cpu_cores": 4, "memory_gb": 8, "display": True},
            execution_patterns=["sequential", "browser_parallel"],
            dependencies=[TestLevel.LEVEL2, TestLevel.LEVEL3],
            parallel_support=True,
            estimated_duration_range=(120, 1800)
        )
        
        # Level 5: 性能测试
        self.test_capabilities[TestLevel.LEVEL5] = TestCapability(
            level=TestLevel.LEVEL5,
            test_types={"performance_test", "load_test", "benchmark_test"},
            required_resources={"cpu_cores": 8, "memory_gb": 16, "network_bandwidth": "high"},
            execution_patterns=["isolated", "resource_intensive"],
            dependencies=[TestLevel.LEVEL1, TestLevel.LEVEL2],
            parallel_support=False,
            estimated_duration_range=(300, 3600)
        )
        
        # Level 6: 安全测试
        self.test_capabilities[TestLevel.LEVEL6] = TestCapability(
            level=TestLevel.LEVEL6,
            test_types={"security_test", "penetration_test", "vulnerability_test"},
            required_resources={"cpu_cores": 4, "memory_gb": 8, "network": True, "security_tools": True},
            execution_patterns=["isolated", "sequential"],
            dependencies=[TestLevel.LEVEL3, TestLevel.LEVEL4],
            parallel_support=False,
            estimated_duration_range=(600, 7200)
        )
        
        # Level 7: 端到端测试
        self.test_capabilities[TestLevel.LEVEL7] = TestCapability(
            level=TestLevel.LEVEL7,
            test_types={"e2e_test", "workflow_test", "user_journey_test"},
            required_resources={"cpu_cores": 6, "memory_gb": 12, "full_environment": True},
            execution_patterns=["sequential", "environment_isolated"],
            dependencies=[TestLevel.LEVEL2, TestLevel.LEVEL3, TestLevel.LEVEL4],
            parallel_support=True,
            estimated_duration_range=(300, 2400)
        )
        
        # Level 8: 兼容性测试
        self.test_capabilities[TestLevel.LEVEL8] = TestCapability(
            level=TestLevel.LEVEL8,
            test_types={"compatibility_test", "cross_platform_test", "browser_compatibility"},
            required_resources={"cpu_cores": 8, "memory_gb": 16, "multiple_environments": True},
            execution_patterns=["matrix_parallel", "platform_isolated"],
            dependencies=[TestLevel.LEVEL4, TestLevel.LEVEL7],
            parallel_support=True,
            estimated_duration_range=(600, 3600)
        )
        
        # Level 9: 压力测试
        self.test_capabilities[TestLevel.LEVEL9] = TestCapability(
            level=TestLevel.LEVEL9,
            test_types={"stress_test", "spike_test", "volume_test"},
            required_resources={"cpu_cores": 16, "memory_gb": 32, "high_bandwidth": True},
            execution_patterns=["isolated", "resource_exclusive"],
            dependencies=[TestLevel.LEVEL5, TestLevel.LEVEL7],
            parallel_support=False,
            estimated_duration_range=(1800, 7200)
        )
        
        # Level 10: 业务流程测试
        self.test_capabilities[TestLevel.LEVEL10] = TestCapability(
            level=TestLevel.LEVEL10,
            test_types={"business_process_test", "workflow_validation", "end_user_scenario"},
            required_resources={"cpu_cores": 8, "memory_gb": 16, "full_stack": True},
            execution_patterns=["sequential", "business_critical"],
            dependencies=[TestLevel.LEVEL7, TestLevel.LEVEL8],
            parallel_support=True,
            estimated_duration_range=(900, 3600)
        )
        
        logger.info(f"✅ 初始化了 {len(self.test_capabilities)} 个测试级别的能力定义")
    
    async def _build_test_suites(self):
        """构建测试套件"""
        logger.info("🏗️ 构建测试套件...")
        
        for level, test_files in self.discovered_tests.items():
            if not test_files:
                continue
            
            capability = self.test_capabilities[level]
            
            # 创建测试套件
            suite = TestSuite(
                suite_id=f"suite_{level.value}",
                level=level,
                test_files=test_files,
                configuration=await self._load_level_configuration(level),
                execution_order=await self._determine_execution_order(test_files, level),
                parallel_groups=await self._create_parallel_groups(test_files, capability),
                resource_requirements=capability.required_resources
            )
            
            self.test_suites[suite.suite_id] = suite
            logger.info(f"  📦 {level.value}: 创建测试套件，包含 {len(test_files)} 个测试")
    
    async def _load_level_configuration(self, level: TestLevel) -> Dict[str, Any]:
        """加载级别配置"""
        config_file = self.test_framework_path / level.value / "config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # 返回默认配置
        return {
            "timeout": 3600,
            "retry_count": 3,
            "parallel_workers": 4 if self.test_capabilities[level].parallel_support else 1
        }
    
    async def _determine_execution_order(self, test_files: List[str], level: TestLevel) -> List[str]:
        """确定执行顺序"""
        # 简单的字母排序，实际可以基于依赖关系分析
        return sorted(test_files)
    
    async def _create_parallel_groups(self, test_files: List[str], capability: TestCapability) -> List[List[str]]:
        """创建并行执行组"""
        if not capability.parallel_support:
            return [[file] for file in test_files]
        
        # 根据文件大小和复杂度分组
        group_size = 4  # 每组4个测试文件
        groups = []
        
        for i in range(0, len(test_files), group_size):
            group = test_files[i:i + group_size]
            groups.append(group)
        
        return groups
    
    async def _validate_architecture(self):
        """验证架构完整性"""
        logger.info("🔍 验证测试架构完整性...")
        
        validation_results = {
            "total_levels": len(TestLevel),
            "discovered_levels": len(self.discovered_tests),
            "test_suites": len(self.test_suites),
            "total_test_files": sum(len(files) for files in self.discovered_tests.values()),
            "dependency_validation": True,
            "capability_coverage": True
        }
        
        # 验证依赖关系
        for level, dependencies in self.level_dependencies.items():
            for dep_level in dependencies:
                if dep_level not in self.discovered_tests or not self.discovered_tests[dep_level]:
                    logger.warning(f"⚠️ {level.value} 依赖的 {dep_level.value} 没有测试文件")
                    validation_results["dependency_validation"] = False
        
        # 验证能力覆盖
        for level in TestLevel:
            if level not in self.test_capabilities:
                logger.warning(f"⚠️ {level.value} 缺少能力定义")
                validation_results["capability_coverage"] = False
        
        logger.info(f"✅ 架构验证完成: {json.dumps(validation_results, indent=2)}")
        return validation_results
    
    # 对外接口方法
    
    def get_test_capability(self, level: TestLevel) -> Optional[TestCapability]:
        """获取测试能力"""
        return self.test_capabilities.get(level)
    
    def get_test_suite(self, suite_id: str) -> Optional[TestSuite]:
        """获取测试套件"""
        return self.test_suites.get(suite_id)
    
    def get_level_dependencies(self, level: TestLevel) -> List[TestLevel]:
        """获取级别依赖"""
        return self.level_dependencies.get(level, [])
    
    def get_executable_levels(self, completed_levels: Set[TestLevel]) -> List[TestLevel]:
        """获取可执行的测试级别"""
        executable = []
        
        for level in TestLevel:
            dependencies = self.get_level_dependencies(level)
            if all(dep in completed_levels for dep in dependencies):
                if level not in completed_levels:
                    executable.append(level)
        
        return executable
    
    def estimate_execution_time(self, level: TestLevel, test_count: int = None) -> Tuple[int, int]:
        """估算执行时间"""
        capability = self.get_test_capability(level)
        if not capability:
            return (300, 1800)  # 默认5-30分钟
        
        min_time, max_time = capability.estimated_duration_range
        
        if test_count:
            # 根据测试数量调整
            if capability.parallel_support:
                # 并行执行，时间增长较慢
                factor = max(1, test_count / 4)
            else:
                # 串行执行，时间线性增长
                factor = test_count
            
            min_time = int(min_time * factor)
            max_time = int(max_time * factor)
        
        return (min_time, max_time)
    
    def get_resource_requirements(self, levels: List[TestLevel]) -> Dict[str, Any]:
        """获取资源需求"""
        max_requirements = {}
        
        for level in levels:
            capability = self.get_test_capability(level)
            if capability:
                for resource, value in capability.required_resources.items():
                    if isinstance(value, (int, float)):
                        max_requirements[resource] = max(
                            max_requirements.get(resource, 0), 
                            value
                        )
                    else:
                        max_requirements[resource] = value
        
        return max_requirements
    
    async def get_integration_report(self) -> Dict[str, Any]:
        """获取集成报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "architecture_summary": {
                "total_levels": len(TestLevel),
                "integrated_levels": len(self.test_capabilities),
                "total_test_suites": len(self.test_suites),
                "total_test_files": sum(len(files) for files in self.discovered_tests.values())
            },
            "level_details": {
                level.value: {
                    "test_files_count": len(self.discovered_tests.get(level, [])),
                    "has_capability": level in self.test_capabilities,
                    "has_test_suite": f"suite_{level.value}" in self.test_suites,
                    "dependencies": [dep.value for dep in self.get_level_dependencies(level)]
                }
                for level in TestLevel
            },
            "capability_matrix": {
                level.value: {
                    "test_types": list(capability.test_types),
                    "parallel_support": capability.parallel_support,
                    "resource_requirements": capability.required_resources,
                    "execution_patterns": capability.execution_patterns
                }
                for level, capability in self.test_capabilities.items()
            }
        }

