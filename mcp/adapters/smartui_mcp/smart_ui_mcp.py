#!/usr/bin/env python3
"""
Smart UI MCP - PowerAutomation 智能用户界面管理组件

负责：
- UI组件管理和协调
- 会话管理
- 用户界面状态同步
- 与其他MCP组件的UI交互
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Smart UI MCP 配置
SMARTUI_MCP_CONFIG = {
    "name": "Smart UI MCP",
    "version": "1.0.0",
    "description": "PowerAutomation 智能用户界面管理组件",
    "port": 8090,
    "coordinator_url": "http://localhost:8089"
}

class SmartUIMCP:
    """Smart UI MCP 核心类"""
    
    def __init__(self):
        self.mcp_id = "smart_ui_mcp"
        self.status = "running"
        self.sessions = {}
        self.ui_components = {}
        
        # 注册到MCP协调器
        self.register_to_coordinator()
        
        logger.info(f"✅ Smart UI MCP 初始化完成")
    
    def register_to_coordinator(self):
        """注册到MCP协调器"""
        try:
            registration_data = {
                "mcp_id": self.mcp_id,
                "name": SMARTUI_MCP_CONFIG["name"],
                "version": SMARTUI_MCP_CONFIG["version"],
                "url": f"http://localhost:{SMARTUI_MCP_CONFIG['port']}",
                "capabilities": [
                    "ui_management",
                    "session_management", 
                    "component_coordination",
                    "user_interface_sync"
                ]
            }
            
            response = requests.post(
                f"{SMARTUI_MCP_CONFIG['coordinator_url']}/register",
                json=registration_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("✅ 成功注册到MCP协调器")
            else:
                logger.warning(f"⚠️ 注册到协调器失败: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ 无法连接到MCP协调器: {str(e)}")
    
    def get_mcp_info(self):
        """获取MCP信息"""
        return {
            "mcp_id": self.mcp_id,
            "name": SMARTUI_MCP_CONFIG["name"],
            "version": SMARTUI_MCP_CONFIG["version"],
            "status": self.status,
            "capabilities": [
                "ui_management",
                "session_management",
                "component_coordination", 
                "user_interface_sync"
            ],
            "active_sessions": len(self.sessions),
            "ui_components": len(self.ui_components)
        }
    
    def create_session(self, session_data):
        """创建UI会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "user_data": session_data.get("user_data", {}),
            "ui_state": session_data.get("ui_state", {}),
            "active": True
        }
        
        logger.info(f"✅ 创建UI会话: {session_id}")
        return session_id
    
    def manage_ui_component(self, component_data):
        """管理UI组件"""
        component_id = component_data.get("component_id")
        component_type = component_data.get("type")
        
        self.ui_components[component_id] = {
            "id": component_id,
            "type": component_type,
            "config": component_data.get("config", {}),
            "status": "active",
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"✅ 管理UI组件: {component_id} ({component_type})")
        return component_id

# 创建Smart UI MCP实例
smartui_mcp = SmartUIMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "running",
        "name": SMARTUI_MCP_CONFIG["name"],
        "version": SMARTUI_MCP_CONFIG["version"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/info', methods=['GET'])
def get_info():
    """获取Smart UI MCP信息"""
    return jsonify(smartui_mcp.get_mcp_info())

@app.route('/session/create', methods=['POST'])
def create_session():
    """创建UI会话"""
    try:
        session_data = request.get_json() or {}
        session_id = smartui_mcp.create_session(session_data)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "UI会话创建成功"
        })
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话信息"""
    if session_id in smartui_mcp.sessions:
        return jsonify({
            "success": True,
            "session": smartui_mcp.sessions[session_id]
        })
    else:
        return jsonify({
            "success": False,
            "error": "会话不存在"
        }), 404

@app.route('/component/manage', methods=['POST'])
def manage_component():
    """管理UI组件"""
    try:
        component_data = request.get_json() or {}
        component_id = smartui_mcp.manage_ui_component(component_data)
        
        return jsonify({
            "success": True,
            "component_id": component_id,
            "message": "UI组件管理成功"
        })
    except Exception as e:
        logger.error(f"管理组件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/components', methods=['GET'])
def get_components():
    """获取所有UI组件"""
    return jsonify({
        "success": True,
        "components": smartui_mcp.ui_components,
        "total": len(smartui_mcp.ui_components)
    })

@app.route('/sync', methods=['POST'])
def sync_ui_state():
    """同步UI状态"""
    try:
        sync_data = request.get_json() or {}
        session_id = sync_data.get("session_id")
        ui_state = sync_data.get("ui_state", {})
        
        if session_id in smartui_mcp.sessions:
            smartui_mcp.sessions[session_id]["ui_state"] = ui_state
            smartui_mcp.sessions[session_id]["last_sync"] = datetime.now().isoformat()
            
            return jsonify({
                "success": True,
                "message": "UI状态同步成功"
            })
        else:
            return jsonify({
                "success": False,
                "error": "会话不存在"
            }), 404
            
    except Exception as e:
        logger.error(f"同步UI状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    return jsonify({
        "success": True,
        "stats": {
            "active_sessions": len([s for s in smartui_mcp.sessions.values() if s.get("active", False)]),
            "total_sessions": len(smartui_mcp.sessions),
            "ui_components": len(smartui_mcp.ui_components),
            "uptime": datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    logger.info(f"启动 {SMARTUI_MCP_CONFIG['name']} v{SMARTUI_MCP_CONFIG['version']}")
    logger.info(f"端口: {SMARTUI_MCP_CONFIG['port']}")
    
    app.run(
        host='0.0.0.0',
        port=SMARTUI_MCP_CONFIG['port'],
        debug=False
    )

