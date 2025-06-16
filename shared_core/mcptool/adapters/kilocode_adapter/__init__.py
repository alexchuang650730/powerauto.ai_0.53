"""
KiloCode MCP Adapter 模块
按照PowerAutomation 0.53规范实现的兜底创建引擎
"""

from .kilocode_mcp import KiloCodeMCP
from .config import get_mcp_config, get_routing_info, get_capabilities

__version__ = "2.0.0"
__author__ = "PowerAutomation Team"
__description__ = "KiloCode MCP - 工作流兜底创建引擎"

# 导出主要类和函数
__all__ = [
    'KiloCodeMCP',
    'get_mcp_config', 
    'get_routing_info',
    'get_capabilities'
]

# 模块级别的配置信息
MODULE_INFO = {
    "name": "kilocode_mcp",
    "version": __version__,
    "type": "fallback_creator",
    "description": __description__,
    "author": __author__
}

