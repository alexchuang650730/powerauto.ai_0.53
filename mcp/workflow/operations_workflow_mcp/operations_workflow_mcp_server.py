#!/usr/bin/env python3
"""
Operations Workflow MCP Server
标准MCP服务实现 - 运行在8090端口
"""

import sys
import asyncio
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging

# 添加项目根目录到Python路径
repo_root = Path("/home/ubuntu/kilocode_integrated_repo")
sys.path.insert(0, str(repo_root))

from mcp.workflow.operations_workflow_mcp.src.file_placement_manager import FilePlacementManager
from mcp.workflow.operations_workflow_mcp.src.mcp_registry_manager import MCPRegistryManager
from mcp.workflow.operations_workflow_mcp.src.smart_intervention_coordinator import SmartInterventionCoordinator
from mcp.workflow.operations_workflow_mcp.src.directory_structure_manager import DirectoryStructureManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class OperationsWorkflowMCPServer:
    """Operations Workflow MCP 标准服务"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.mcp_id = "operations_workflow_mcp"
        self.version = "1.0.0"
        self.status = "initializing"
        
        # 初始化组件
        try:
            self.file_manager = FilePlacementManager(repo_root)
            self.registry_manager = MCPRegistryManager(repo_root)
            self.intervention_coordinator = SmartInterventionCoordinator(repo_root)
            self.directory_manager = DirectoryStructureManager(repo_root)
            self.status = "ready"
            logger.info(f"✅ {self.mcp_id} 初始化完成")
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ {self.mcp_id} 初始化失败: {e}")
    
    def get_mcp_info(self):
        """获取MCP基本信息"""
        return {
            "mcp_id": self.mcp_id,
            "version": self.version,
            "status": self.status,
            "capabilities": [
                "file_placement",
                "mcp_registry_management", 
                "smart_intervention",
                "directory_structure_management"
            ],
            "endpoints": [
                "/mcp/status",
                "/mcp/file-placement/analyze",
                "/mcp/file-placement/execute",
                "/mcp/registry/status",
                "/mcp/interventions/status",
                "/mcp/directory/check"
            ]
        }
    
    def process_request(self, action: str, params: dict = None):
        """处理MCP请求"""
        try:
            if action == "get_status":
                return self._get_status()
            elif action == "file_placement_analyze":
                return self._file_placement_analyze()
            elif action == "file_placement_execute":
                return self._file_placement_execute()
            elif action == "registry_status":
                return self._registry_status()
            elif action == "interventions_status":
                return self._interventions_status()
            elif action == "directory_check":
                return self._directory_check()
            else:
                return {
                    "success": False,
                    "error": f"未知操作: {action}",
                    "available_actions": [
                        "get_status", "file_placement_analyze", "file_placement_execute",
                        "registry_status", "interventions_status", "directory_check"
                    ]
                }
        except Exception as e:
            logger.error(f"处理请求失败 {action}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_status(self):
        """获取MCP状态"""
        return {
            "success": True,
            "data": {
                "mcp_info": self.get_mcp_info(),
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "file_manager": "ready",
                    "registry_manager": "ready", 
                    "intervention_coordinator": "ready",
                    "directory_manager": "ready"
                }
            }
        }
    
    def _file_placement_analyze(self):
        """分析文件放置"""
        analysis = self.file_manager.analyze_upload_files()
        return {
            "success": True,
            "data": {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _file_placement_execute(self):
        """执行文件放置"""
        analysis = self.file_manager.analyze_upload_files()
        if not analysis['placement_plan']:
            return {
                "success": True,
                "data": {
                    "message": "没有文件需要放置",
                    "results": {"successful": 0, "failed": 0}
                }
            }
        
        results = self.file_manager.execute_placement_plan(analysis['placement_plan'])
        return {
            "success": True,
            "data": {
                "message": f"文件放置完成: 成功 {results['successful']}, 失败 {results['failed']}",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _registry_status(self):
        """获取MCP注册表状态"""
        status = self.registry_manager.get_registry_status()
        return {
            "success": True,
            "data": status
        }
    
    def _interventions_status(self):
        """获取介入状态"""
        status = self.intervention_coordinator.get_coordinator_status()
        return {
            "success": True,
            "data": status
        }
    
    def _directory_check(self):
        """检查目录结构"""
        # 简单的目录结构检查
        violations = []
        
        # 检查基本目录结构
        required_dirs = ["mcp", "mcp/adapter", "mcp/workflow", "scripts", "workflow_howto"]
        for dir_path in required_dirs:
            if not (self.repo_root / dir_path).exists():
                violations.append(f"缺少必需目录: {dir_path}")
        
        return {
            "success": True,
            "data": {
                "violations": violations,
                "compliant": len(violations) == 0,
                "timestamp": datetime.now().isoformat()
            }
        }

# 全局MCP服务实例
mcp_server = OperationsWorkflowMCPServer()

# ============================================================================
# Flask API 端点
# ============================================================================

@app.route('/mcp/info', methods=['GET'])
def get_mcp_info():
    """获取MCP基本信息"""
    return jsonify(mcp_server.get_mcp_info())

@app.route('/mcp/request', methods=['POST'])
def handle_mcp_request():
    """处理MCP请求 - 标准MCP协议端点"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        if not action:
            return jsonify({
                "success": False,
                "error": "缺少action参数"
            }), 400
        
        result = mcp_server.process_request(action, params)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理MCP请求失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/mcp/status', methods=['GET'])
def get_status():
    """获取MCP状态"""
    result = mcp_server.process_request("get_status")
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "mcp_id": mcp_server.mcp_id,
        "version": mcp_server.version,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动 Operations Workflow MCP Server")
    print("=" * 60)
    print(f"MCP ID: {mcp_server.mcp_id}")
    print(f"版本: {mcp_server.version}")
    print(f"状态: {mcp_server.status}")
    print("=" * 60)
    print("标准MCP端点:")
    print("  - GET  /mcp/info     - MCP基本信息")
    print("  - POST /mcp/request  - MCP请求处理")
    print("  - GET  /mcp/status   - MCP状态")
    print("  - GET  /health       - 健康检查")
    print("=" * 60)
    print("运行在端口: 8090")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8090, debug=False)

