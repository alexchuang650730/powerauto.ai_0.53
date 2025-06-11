#!/usr/bin/env python3
"""
PowerAutomation 测试框架集成包
集成分布式协调器和AI组件到现有测试框架

作者: PowerAutomation团队
版本: 1.0.0-production
"""

from .test_architecture_integrator import (
    TestArchitectureIntegrator,
    TestLevel,
    TestCapability,
    TestSuite
)

from .ai_integrator import (
    PowerAutoAIIntegrator,
    AIModuleType
)

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"

__all__ = [
    # 测试架构集成
    'TestArchitectureIntegrator',
    'TestLevel',
    'TestCapability', 
    'TestSuite',
    
    # AI集成
    'PowerAutoAIIntegrator',
    'AIModuleType'
]

# 集成信息
INTEGRATIONS_INFO = {
    "name": "PowerAutomation 测试框架集成",
    "version": __version__,
    "description": "将分布式协调器和AI组件集成到PowerAutomation测试框架",
    "features": [
        "十层测试架构集成",
        "AI组件深度集成",
        "智能测试协调",
        "性能优化集成"
    ],
    "compatibility": {
        "powerautomation_version": ">=0.571",
        "test_framework_version": ">=2.0.0"
    }
}

