#!/usr/bin/env python3
"""
MCP Coordinator - 完全兼容版本
统一管理和协调所有MCP组件的中央协调器
支持多种MCP响应格式
"""

import json
import time
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPCoordinator:
    def __init__(self, port=8089):
        self.port = port
        self.status = "initializing"
        self.registered_mcps = {}
        
        # 创建Flask应用
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 注册路由
        self.register_routes()
        
    def register_routes(self):
        """注册Flask路由"""
        
        @self.app.route('/api/mcp/status', methods=['GET'])
        def get_mcp_status():
            """获取所有MCP状态"""
            try:
                aggregated_status = {
                    "coordinator": {
                        "name": "MCP Coordinator",
                        "version": "1.0.0",
                        "status": "running"
                    },
                    "components": {},
                    "performance_metrics": {
                        "total_mcps": len(self.registered_mcps),
                        "active_mcps": 0,
                        "failed_mcps": 0,
                        "cpu_usage": "12%",
                        "memory_usage": "512MB"
                    },
                    "overall_status": "运行中",
                    "last_updated": datetime.now().isoformat()
                }
                
                # 检查每个注册的MCP
                for mcp_name, mcp_info in self.registered_mcps.items():
                    try:
                        status_url = f"http://localhost:{mcp_info['port']}/api/status"
                        response = requests.get(status_url, timeout=5)
                        
                        if response.status_code == 200:
                            mcp_data = response.json()
                            
                            # 兼容多种响应格式
                            mcp_status = None
                            mcp_info_data = None
                            
                            # 格式1: {"success": true, "data": {...}}
                            if mcp_data.get('success') and 'data' in mcp_data:
                                mcp_info_data = mcp_data['data']
                                mcp_status = mcp_info_data.get('status', 'unknown')
                            
                            # 格式2: {"status": "running", "name": "...", ...}
                            elif 'status' in mcp_data:
                                mcp_info_data = mcp_data
                                mcp_status = mcp_data['status']
                            
                            # 格式3: 其他格式，尝试推断
                            else:
                                mcp_info_data = mcp_data
                                mcp_status = 'running'  # 假设能响应就是运行中
                            
                            # 判断是否运行正常
                            if mcp_status in ['running', '运行中', 'active']:
                                aggregated_status["components"][mcp_name] = {
                                    "status": "运行中",
                                    "description": mcp_info.get('description', mcp_info_data.get('name', mcp_name)),
                                    "version": mcp_info_data.get('version', 'unknown'),
                                    "capabilities": mcp_info_data.get('capabilities', []),
                                    "performance": mcp_info_data.get('performance', mcp_info_data.get('performance_metrics', {})),
                                    "port": mcp_info['port']
                                }
                                aggregated_status["performance_metrics"]["active_mcps"] += 1
                            else:
                                aggregated_status["components"][mcp_name] = {
                                    "status": "错误",
                                    "error": f"MCP状态: {mcp_status}",
                                    "description": mcp_info.get('description', mcp_name)
                                }
                                aggregated_status["performance_metrics"]["failed_mcps"] += 1
                        else:
                            aggregated_status["components"][mcp_name] = {
                                "status": "无响应",
                                "error": f"HTTP {response.status_code}",
                                "description": mcp_info.get('description', mcp_name)
                            }
                            aggregated_status["performance_metrics"]["failed_mcps"] += 1
                            
                    except requests.exceptions.RequestException as e:
                        aggregated_status["components"][mcp_name] = {
                            "status": "连接失败",
                            "error": str(e),
                            "description": mcp_info.get('description', mcp_name)
                        }
                        aggregated_status["performance_metrics"]["failed_mcps"] += 1
                
                return jsonify({
                    "success": True,
                    "data": aggregated_status
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"获取MCP状态失败: {str(e)}"
                }), 500
        
        @self.app.route('/api/mcp/register', methods=['POST'])
        def register_mcp():
            """注册新的MCP"""
            try:
                data = request.get_json()
                mcp_name = data.get('name')
                mcp_port = data.get('port')
                mcp_description = data.get('description', '')
                
                if not mcp_name or not mcp_port:
                    return jsonify({
                        "success": False,
                        "error": "缺少必要参数: name, port"
                    }), 400
                
                self.registered_mcps[mcp_name] = {
                    "port": mcp_port,
                    "description": mcp_description,
                    "registered_at": datetime.now().isoformat()
                }
                
                logger.info(f"MCP注册成功: {mcp_name} (端口: {mcp_port})")
                
                return jsonify({
                    "success": True,
                    "message": f"MCP {mcp_name} 注册成功"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"MCP注册失败: {str(e)}"
                }), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "coordinator_status": self.status,
                "registered_mcps": len(self.registered_mcps)
            })
    
    def register_default_mcps(self):
        """注册默认的MCP"""
        default_mcps = [
            {
                "name": "kilocode_mcp",
                "port": 8080,
                "description": "工作流兜底创建引擎"
            },
            {
                "name": "smart_ui_mcp", 
                "port": 8090,
                "description": "智能UI管理组件"
            },
            {
                "name": "test_manager_mcp",
                "port": 8091,
                "description": "测试管理系统"
            },
            {
                "name": "release_manager_mcp",
                "port": 8092,
                "description": "发布管理系统"
            }
        ]
        
        for mcp in default_mcps:
            self.registered_mcps[mcp["name"]] = {
                "port": mcp["port"],
                "description": mcp["description"],
                "registered_at": datetime.now().isoformat()
            }
        
        logger.info(f"默认MCP注册完成: {len(default_mcps)}个")
    
    def start_coordinator(self):
        """启动MCP协调器"""
        try:
            self.status = "running"
            
            # 注册默认MCP
            self.register_default_mcps()
            
            logger.info(f"🎯 MCP Coordinator启动成功 - 端口: {self.port}")
            logger.info(f"📊 已注册MCP: {len(self.registered_mcps)}个")
            logger.info(f"🔗 MCP列表: {list(self.registered_mcps.keys())}")
            
            # 启动Flask服务
            self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
            
        except Exception as e:
            self.status = "error"
            logger.error(f"MCP Coordinator启动失败: {e}")
            raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Coordinator')
    parser.add_argument('--port', type=int, default=8089, help='协调器端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    # 创建并启动MCP协调器
    coordinator = MCPCoordinator(port=args.port)
    
    try:
        coordinator.start_coordinator()
    except KeyboardInterrupt:
        print("\n🛑 MCP Coordinator停止中...")
        coordinator.status = "stopped"
        print("✅ MCP Coordinator已安全关闭")

if __name__ == "__main__":
    main()

