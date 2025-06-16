#!/usr/bin/env python3
"""
Coding Workflow MCP - 编码工作流MCP
管理完整的编码流程，包括代码规范、审查、质量控制和发布管理
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import requests

logger = logging.getLogger(__name__)

class CodingPhase(Enum):
    """编码阶段"""
    PLANNING = "planning"           # 规划阶段
    DEVELOPMENT = "development"     # 开发阶段
    CODE_REVIEW = "code_review"     # 代码审查
    TESTING = "testing"             # 测试阶段
    INTEGRATION = "integration"     # 集成阶段
    DEPLOYMENT = "deployment"       # 部署阶段

class WorkflowStatus(Enum):
    """工作流状态"""
    IDLE = "idle"                   # 空闲
    RUNNING = "running"             # 运行中
    PAUSED = "paused"               # 暂停
    COMPLETED = "completed"         # 完成
    FAILED = "failed"               # 失败

@dataclass
class CodingTask:
    """编码任务"""
    task_id: str
    title: str
    description: str
    phase: CodingPhase
    status: WorkflowStatus
    assigned_mcp: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = None

class CodingWorkflowMCP:
    """编码工作流MCP - 统一管理编码流程"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.mcp_id = "coding_workflow_mcp"
        self.version = "1.0.0"
        self.status = WorkflowStatus.IDLE
        
        # 工作流配置
        self.workflow_config = {
            "max_concurrent_tasks": 5,
            "auto_progression": True,
            "quality_gates": True,
            "notification_enabled": True
        }
        
        # 注册的MCP组件
        self.registered_mcps = {}
        
        # 当前任务队列
        self.task_queue = []
        self.active_tasks = {}
        
        # 工作流统计
        self.workflow_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0,
            "quality_score": 0
        }
        
        # MCP Coordinator配置
        self.coordinator_url = "http://localhost:8089"
        
        logger.info(f"🔧 {self.mcp_id} 初始化完成")
    
    def get_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "mcp_id": self.mcp_id,
            "version": self.version,
            "status": self.status.value,
            "registered_mcps": len(self.registered_mcps),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "workflow_stats": self.workflow_stats,
            "capabilities": [
                "coding_process_management",
                "quality_control",
                "code_review_automation",
                "development_intervention",
                "workflow_orchestration"
            ]
        }
    
    async def register_component_mcp(self, mcp_id: str, mcp_config: Dict[str, Any]) -> Dict[str, Any]:
        """注册组件MCP到编码工作流"""
        try:
            # 验证MCP配置
            required_fields = ["url", "capabilities"]
            for field in required_fields:
                if field not in mcp_config:
                    raise ValueError(f"MCP配置缺少必需字段: {field}")
            
            # 测试MCP连接
            health_check = await self._health_check_mcp(mcp_config["url"])
            if not health_check["success"]:
                raise Exception(f"MCP健康检查失败: {health_check['error']}")
            
            # 注册MCP
            self.registered_mcps[mcp_id] = {
                **mcp_config,
                "registered_at": datetime.now().isoformat(),
                "status": "active",
                "last_health_check": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 组件MCP注册成功: {mcp_id}")
            
            return {
                "success": True,
                "mcp_id": mcp_id,
                "message": f"组件MCP {mcp_id} 已成功注册到编码工作流",
                "registered_count": len(self.registered_mcps)
            }
            
        except Exception as e:
            logger.error(f"❌ 组件MCP注册失败: {mcp_id} - {e}")
            return {
                "success": False,
                "mcp_id": mcp_id,
                "error": str(e)
            }
    
    async def _health_check_mcp(self, mcp_url: str) -> Dict[str, Any]:
        """检查MCP健康状态"""
        try:
            response = requests.get(f"{mcp_url}/health", timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_coding_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建编码任务"""
        try:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.task_queue)}"
            
            task = CodingTask(
                task_id=task_id,
                title=task_data.get("title", "未命名任务"),
                description=task_data.get("description", ""),
                phase=CodingPhase(task_data.get("phase", "planning")),
                status=WorkflowStatus.IDLE,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                metadata=task_data.get("metadata", {})
            )
            
            # 根据任务阶段分配合适的MCP
            assigned_mcp = self._assign_mcp_for_phase(task.phase)
            if assigned_mcp:
                task.assigned_mcp = assigned_mcp
            
            self.task_queue.append(task)
            self.workflow_stats["total_tasks"] += 1
            
            logger.info(f"📝 创建编码任务: {task_id} - {task.title}")
            
            return {
                "success": True,
                "task_id": task_id,
                "task": self._task_to_dict(task),
                "assigned_mcp": assigned_mcp
            }
            
        except Exception as e:
            logger.error(f"创建编码任务失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _assign_mcp_for_phase(self, phase: CodingPhase) -> Optional[str]:
        """为编码阶段分配合适的MCP"""
        phase_mcp_mapping = {
            CodingPhase.DEVELOPMENT: "development_intervention_mcp",
            CodingPhase.CODE_REVIEW: "development_intervention_mcp",
            CodingPhase.TESTING: "test_manager_mcp",
            CodingPhase.DEPLOYMENT: "release_manager_mcp"
        }
        
        suggested_mcp = phase_mcp_mapping.get(phase)
        
        # 检查建议的MCP是否已注册
        if suggested_mcp and suggested_mcp in self.registered_mcps:
            return suggested_mcp
        
        # 如果建议的MCP未注册，返回第一个可用的MCP
        if self.registered_mcps:
            return list(self.registered_mcps.keys())[0]
        
        return None
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行编码任务"""
        try:
            # 从队列中找到任务
            task = None
            for t in self.task_queue:
                if t.task_id == task_id:
                    task = t
                    break
            
            if not task:
                return {
                    "success": False,
                    "error": f"任务 {task_id} 不存在"
                }
            
            # 检查是否有分配的MCP
            if not task.assigned_mcp:
                return {
                    "success": False,
                    "error": f"任务 {task_id} 没有分配的MCP"
                }
            
            # 更新任务状态
            task.status = WorkflowStatus.RUNNING
            task.updated_at = datetime.now().isoformat()
            
            # 移动到活跃任务
            self.task_queue.remove(task)
            self.active_tasks[task_id] = task
            
            # 通过MCP Coordinator调用分配的MCP
            result = await self._call_mcp_via_coordinator(
                task.assigned_mcp,
                "process_coding_task",
                {
                    "task_id": task_id,
                    "phase": task.phase.value,
                    "title": task.title,
                    "description": task.description,
                    "metadata": task.metadata
                }
            )
            
            # 更新任务状态
            if result.get("success"):
                task.status = WorkflowStatus.COMPLETED
                self.workflow_stats["completed_tasks"] += 1
            else:
                task.status = WorkflowStatus.FAILED
                self.workflow_stats["failed_tasks"] += 1
            
            task.updated_at = datetime.now().isoformat()
            
            logger.info(f"🎯 任务执行完成: {task_id} - {task.status.value}")
            
            return {
                "success": True,
                "task_id": task_id,
                "task_status": task.status.value,
                "execution_result": result
            }
            
        except Exception as e:
            logger.error(f"执行编码任务失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _call_mcp_via_coordinator(self, mcp_id: str, action: str, params: Dict) -> Dict[str, Any]:
        """通过MCP Coordinator调用MCP"""
        try:
            response = requests.post(
                f"{self.coordinator_url}/coordinator/request/{mcp_id}",
                json={
                    "action": action,
                    "params": params
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"MCP调用失败: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"MCP调用异常: {str(e)}"
            }
    
    async def get_workflow_overview(self) -> Dict[str, Any]:
        """获取工作流概览"""
        try:
            # 统计各阶段任务数量
            phase_stats = {}
            for phase in CodingPhase:
                phase_stats[phase.value] = {
                    "queued": 0,
                    "active": 0,
                    "completed": 0,
                    "failed": 0
                }
            
            # 统计队列中的任务
            for task in self.task_queue:
                phase_stats[task.phase.value]["queued"] += 1
            
            # 统计活跃任务
            for task in self.active_tasks.values():
                if task.status == WorkflowStatus.RUNNING:
                    phase_stats[task.phase.value]["active"] += 1
                elif task.status == WorkflowStatus.COMPLETED:
                    phase_stats[task.phase.value]["completed"] += 1
                elif task.status == WorkflowStatus.FAILED:
                    phase_stats[task.phase.value]["failed"] += 1
            
            # 计算质量分数
            total_tasks = self.workflow_stats["completed_tasks"] + self.workflow_stats["failed_tasks"]
            quality_score = 0
            if total_tasks > 0:
                quality_score = (self.workflow_stats["completed_tasks"] / total_tasks) * 100
            
            self.workflow_stats["quality_score"] = round(quality_score, 2)
            
            return {
                "success": True,
                "workflow_status": self.status.value,
                "phase_statistics": phase_stats,
                "overall_stats": self.workflow_stats,
                "registered_mcps": list(self.registered_mcps.keys()),
                "active_tasks_count": len(self.active_tasks),
                "queued_tasks_count": len(self.task_queue)
            }
            
        except Exception as e:
            logger.error(f"获取工作流概览失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check_all_mcps(self) -> Dict[str, Any]:
        """检查所有注册MCP的健康状态"""
        results = {}
        
        for mcp_id, mcp_config in self.registered_mcps.items():
            health_result = await self._health_check_mcp(mcp_config["url"])
            results[mcp_id] = {
                "healthy": health_result["success"],
                "status": "healthy" if health_result["success"] else "unhealthy",
                "error": health_result.get("error"),
                "last_check": datetime.now().isoformat()
            }
            
            # 更新MCP状态
            self.registered_mcps[mcp_id]["status"] = results[mcp_id]["status"]
            self.registered_mcps[mcp_id]["last_health_check"] = results[mcp_id]["last_check"]
        
        healthy_count = sum(1 for r in results.values() if r["healthy"])
        
        return {
            "success": True,
            "total_mcps": len(results),
            "healthy_mcps": healthy_count,
            "unhealthy_mcps": len(results) - healthy_count,
            "details": results
        }
    
    def _task_to_dict(self, task: CodingTask) -> Dict[str, Any]:
        """将任务转换为字典"""
        return {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "phase": task.phase.value,
            "status": task.status.value,
            "assigned_mcp": task.assigned_mcp,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "metadata": task.metadata or {}
        }

# ============================================================================
# Flask MCP Server
# ============================================================================

def create_coding_workflow_mcp_server():
    """创建编码工作流MCP服务器"""
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    # 创建工作流MCP实例
    coding_mcp = CodingWorkflowMCP()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            "mcp_id": coding_mcp.mcp_id,
            "status": "healthy",
            "version": coding_mcp.version,
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/mcp/info', methods=['GET'])
    def mcp_info():
        """MCP基本信息"""
        return jsonify({
            "mcp_id": coding_mcp.mcp_id,
            "version": coding_mcp.version,
            "capabilities": [
                "coding_process_management",
                "quality_control",
                "code_review_automation",
                "development_intervention",
                "workflow_orchestration"
            ],
            "description": "Coding Workflow MCP - 编码工作流管理"
        })
    
    @app.route('/mcp/request', methods=['POST'])
    def mcp_request():
        """标准MCP请求处理"""
        try:
            data = request.get_json()
            action = data.get('action')
            params = data.get('params', {})
            
            if action == 'get_status':
                result = coding_mcp.get_status()
            elif action == 'register_component_mcp':
                mcp_id = params.get('mcp_id')
                mcp_config = params.get('mcp_config', {})
                result = asyncio.run(coding_mcp.register_component_mcp(mcp_id, mcp_config))
            elif action == 'create_coding_task':
                result = asyncio.run(coding_mcp.create_coding_task(params))
            elif action == 'execute_task':
                task_id = params.get('task_id')
                result = asyncio.run(coding_mcp.execute_task(task_id))
            elif action == 'get_workflow_overview':
                result = asyncio.run(coding_mcp.get_workflow_overview())
            elif action == 'health_check_all_mcps':
                result = asyncio.run(coding_mcp.health_check_all_mcps())
            else:
                result = {
                    "success": False,
                    "error": f"未知操作: {action}"
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"MCP请求处理失败: {e}")
            return jsonify({
                "success": False,
                "error": f"MCP请求处理失败: {e}"
            }), 500
    
    return app

if __name__ == '__main__':
    # 创建并启动编码工作流MCP服务器
    app = create_coding_workflow_mcp_server()
    
    print(f"🚀 启动编码工作流MCP服务器...")
    print(f"🔧 MCP ID: coding_workflow_mcp")
    print(f"📡 端口: 8093")
    print(f"🎯 功能: 编码流程管理、质量控制、工作流编排")
    
    app.run(host='0.0.0.0', port=8093, debug=False)

