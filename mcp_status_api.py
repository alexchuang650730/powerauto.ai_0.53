"""
MCP状态API端点 - 为SmartUI提供实时MCP组件状态
"""

from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """获取所有MCP组件状态"""
    try:
        # 从MCP协调器获取注册的组件
        coordinator_response = requests.get('http://localhost:8089/coordinator/mcps', timeout=5)
        
        if coordinator_response.status_code != 200:
            return jsonify({
                "success": False,
                "error": "无法连接到MCP协调器"
            }), 500
        
        coordinator_data = coordinator_response.json()
        registered_mcps = coordinator_data.get('registered_mcps', {})
        
        # 检查每个MCP的健康状态
        mcp_status = {}
        for mcp_id, mcp_config in registered_mcps.items():
            try:
                health_url = f"{mcp_config['url']}/health"
                health_response = requests.get(health_url, timeout=3)
                
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    mcp_status[mcp_id] = {
                        "name": mcp_config.get('name', mcp_id),
                        "status": "running",
                        "health": health_data.get('status', 'unknown'),
                        "version": mcp_config.get('version', health_data.get('version', 'unknown')),
                        "url": mcp_config['url'],
                        "capabilities": mcp_config.get('capabilities', []),
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    mcp_status[mcp_id] = {
                        "name": mcp_config.get('name', mcp_id),
                        "status": "error",
                        "error": f"HTTP {health_response.status_code}",
                        "url": mcp_config['url'],
                        "last_check": datetime.now().isoformat()
                    }
            except Exception as e:
                mcp_status[mcp_id] = {
                    "name": mcp_config.get('name', mcp_id),
                    "status": "error",
                    "error": str(e),
                    "url": mcp_config['url'],
                    "last_check": datetime.now().isoformat()
                }
        
        return jsonify({
            "success": True,
            "data": {
                "mcps": mcp_status,
                "total": len(mcp_status),
                "coordinator_status": "running",
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/mcp/coordinator/status', methods=['GET'])
def get_coordinator_status():
    """获取MCP协调器状态"""
    try:
        response = requests.get('http://localhost:8089/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "success": True,
                "data": {
                    "status": "running",
                    "coordinator_info": data,
                    "timestamp": datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": f"协调器响应错误: HTTP {response.status_code}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"无法连接到协调器: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("启动MCP状态API服务...")
    app.run(host='0.0.0.0', port=8095, debug=False)

