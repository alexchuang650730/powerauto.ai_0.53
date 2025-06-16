"""
MCP状态检查API端点 - 为SmartUI提供MCP组件状态
"""

import requests
import json
from datetime import datetime

# MCP组件配置
MCP_COMPONENTS = {
    "KILOCODE_MCP": {
        "name": "KiloCode MCP",
        "url": "http://localhost:8080/health",
        "port": 8080
    },
    "TEST_MANAGER_MCP": {
        "name": "Test Manager MCP", 
        "url": "http://localhost:8081/health",
        "port": 8081
    },
    "RELEASE_MANAGER_MCP": {
        "name": "Release Manager MCP",
        "url": "http://localhost:8082/health", 
        "port": 8082
    },
    "SMART_UI_MCP": {
        "name": "Smart UI MCP",
        "url": "http://localhost:8090/health",
        "port": 8090
    },
    "GITHUB_MCP": {
        "name": "GitHub MCP",
        "url": "http://localhost:8084/health",
        "port": 8084
    },
    "MCP_COORDINATOR": {
        "name": "MCP Coordinator",
        "url": "http://localhost:8089/health",
        "port": 8089
    }
}

def check_mcp_status():
    """检查所有MCP组件状态"""
    results = {}
    
    for component_id, config in MCP_COMPONENTS.items():
        try:
            response = requests.get(config["url"], timeout=3)
            if response.status_code == 200:
                data = response.json()
                results[component_id] = {
                    "status": "running",
                    "name": config["name"],
                    "port": config["port"],
                    "version": data.get("version", "unknown"),
                    "health": data.get("status", "unknown"),
                    "last_check": datetime.now().isoformat()
                }
            else:
                results[component_id] = {
                    "status": "error",
                    "name": config["name"],
                    "port": config["port"],
                    "error": f"HTTP {response.status_code}",
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            results[component_id] = {
                "status": "error",
                "name": config["name"],
                "port": config["port"],
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    return results

def get_mcp_coordinator_status():
    """获取MCP协调器状态"""
    try:
        response = requests.get("http://localhost:8089/health", timeout=3)
        if response.status_code == 200:
            return {
                "status": "running",
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error", 
                "error": f"HTTP {response.status_code}",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # 测试MCP状态检查
    print("🔍 MCP组件状态检查:")
    print("=" * 50)
    
    results = check_mcp_status()
    for component_id, status in results.items():
        status_icon = "✅" if status["status"] == "running" else "❌"
        print(f"{status_icon} {status['name']:20} (:{status['port']}): {status['status']}")
    
    print("\n🎯 MCP协调器状态:")
    coordinator_status = get_mcp_coordinator_status()
    print(f"状态: {coordinator_status['status']}")
    if coordinator_status['status'] == 'running':
        print(f"数据: {coordinator_status['data']}")

