"""
KiloCode MCP Adapter 配置
供工作流系统读取的标准化配置
"""

# MCP基本信息
MCP_INFO = {
    "name": "kilocode_mcp",
    "display_name": "KiloCode兜底创建引擎",
    "version": "2.0.0",
    "type": "fallback_creator",
    "category": "creation_engine",
    "description": "当所有其他MCP都无法处理时的兜底创建引擎"
}

# 支持的工作流
SUPPORTED_WORKFLOWS = [
    "requirements_analysis",
    "architecture_design", 
    "coding_implementation",
    "testing_verification",
    "deployment_release",
    "monitoring_operations"
]

# 创建能力
CREATION_CAPABILITIES = {
    "document_types": ["ppt", "report", "specification", "manual"],
    "code_types": ["python", "javascript", "html", "css", "bash"],
    "game_types": ["snake", "simple_games", "demos"],
    "tool_types": ["test_scripts", "deploy_scripts", "monitor_tools"]
}

# 工作流路由配置
ROUTING_CONFIG = {
    "priority": "fallback",  # 兜底优先级
    "trigger_conditions": [
        "all_other_mcps_failed",
        "cross_workflow_request", 
        "complex_creation_task",
        "ai_assistance_failed"
    ],
    "fallback_scenarios": {
        "requirements_analysis": ["ppt_creation", "document_generation"],
        "coding_implementation": ["game_development", "code_generation"],
        "architecture_design": ["framework_creation", "design_templates"],
        "testing_verification": ["test_automation", "verification_tools"],
        "deployment_release": ["deployment_scripts", "release_tools"],
        "monitoring_operations": ["monitoring_tools", "alert_systems"]
    }
}

# 性能配置
PERFORMANCE_CONFIG = {
    "max_concurrent_requests": 5,
    "request_timeout": 120,
    "avg_response_time": "2-5秒",
    "success_rate_target": 0.95,
    "memory_limit": "512MB",
    "cpu_limit": "1 core"
}

# API接口配置
API_CONFIG = {
    "endpoints": {
        "create": "/adapter/kilocode_mcp/create",
        "health": "/adapter/kilocode_mcp/health", 
        "capabilities": "/adapter/kilocode_mcp/capabilities"
    },
    "methods": {
        "create": "POST",
        "health": "GET",
        "capabilities": "GET"
    },
    "request_format": {
        "content": "string",
        "workflow_type": "string", 
        "context": "object",
        "options": "object"
    },
    "response_format": {
        "success": "boolean",
        "type": "string",
        "content": "string",
        "metadata": "object"
    }
}

# 依赖配置
DEPENDENCIES = {
    "required": ["asyncio", "logging"],
    "optional": ["aiohttp", "flask"],
    "system": [],
    "external_services": []
}

# 质量控制配置
QUALITY_CONFIG = {
    "code_standards": {
        "min_lines": 10,
        "max_lines": 1000,
        "require_comments": True,
        "require_error_handling": True
    },
    "document_standards": {
        "min_sections": 3,
        "require_structure": True,
        "require_examples": True
    },
    "validation_rules": [
        "syntax_check",
        "security_scan",
        "performance_check"
    ]
}

# 监控配置
MONITORING_CONFIG = {
    "metrics": [
        "request_count",
        "success_rate", 
        "response_time",
        "error_rate",
        "resource_usage"
    ],
    "alerts": [
        "high_error_rate",
        "slow_response",
        "resource_exhaustion"
    ],
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "/var/log/kilocode_mcp.log"
    }
}

# 工作流集成配置
WORKFLOW_INTEGRATION = {
    "registration": {
        "auto_register": True,
        "coordinator_endpoint": "http://localhost:8080/coordinator",
        "heartbeat_interval": 60,
        "health_check_timeout": 30
    },
    "communication": {
        "protocol": "http",
        "format": "json",
        "compression": False,
        "encryption": False
    },
    "failover": {
        "retry_count": 3,
        "retry_delay": 5,
        "circuit_breaker": True,
        "fallback_message": "KiloCode MCP暂时不可用"
    }
}

# 开发配置
DEVELOPMENT_CONFIG = {
    "debug_mode": False,
    "test_mode": False,
    "mock_dependencies": False,
    "verbose_logging": False,
    "profiling": False
}

# 导出配置供工作流读取
def get_mcp_config():
    """获取完整的MCP配置"""
    return {
        "mcp_info": MCP_INFO,
        "supported_workflows": SUPPORTED_WORKFLOWS,
        "creation_capabilities": CREATION_CAPABILITIES,
        "routing_config": ROUTING_CONFIG,
        "performance_config": PERFORMANCE_CONFIG,
        "api_config": API_CONFIG,
        "dependencies": DEPENDENCIES,
        "quality_config": QUALITY_CONFIG,
        "monitoring_config": MONITORING_CONFIG,
        "workflow_integration": WORKFLOW_INTEGRATION,
        "development_config": DEVELOPMENT_CONFIG
    }

def get_routing_info():
    """获取路由信息供工作流使用"""
    return {
        "mcp_id": MCP_INFO["name"],
        "mcp_type": MCP_INFO["type"],
        "priority": ROUTING_CONFIG["priority"],
        "trigger_conditions": ROUTING_CONFIG["trigger_conditions"],
        "supported_workflows": SUPPORTED_WORKFLOWS,
        "api_endpoints": API_CONFIG["endpoints"]
    }

def get_capabilities():
    """获取能力信息供工作流匹配"""
    return {
        "creation_types": list(CREATION_CAPABILITIES.keys()),
        "workflow_support": SUPPORTED_WORKFLOWS,
        "fallback_scenarios": ROUTING_CONFIG["fallback_scenarios"],
        "performance_metrics": PERFORMANCE_CONFIG
    }

