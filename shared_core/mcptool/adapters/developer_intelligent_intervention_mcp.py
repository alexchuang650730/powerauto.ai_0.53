#!/usr/bin/env python3
"""
PowerAutomation 开发端智能介入MCP适配器

提供对开发端智能介入引擎的MCP接口封装，实现六大智能介入场景：
1. Git未check-in监测与自动提交
2. 版本合并冲突自动修正
3. PR自动审核与把关
4. 代码与目录规范扫描
5. manus相关字眼清理
6. PR reviewer自动设置为powerauto.ai

入口：统一MCP CLI
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.append(str(project_root))

# 导入智能介入引擎
from shared_core.engines.developer_intelligent_intervention import (
    DeveloperIntelligentIntervention,
    InterventionConfig,
    InterventionType,
    InterventionStatus
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeveloperIntelligentInterventionMCP:
    """开发端智能介入MCP适配器"""
    
    def __init__(self):
        """初始化适配器"""
        self.name = "DeveloperIntelligentInterventionMCP"
        self.description = "PowerAutomation开发端智能介入适配器，提供Git监控、合并冲突解决、代码规范扫描等功能"
        self.category = "developer"
        self.version = "0.6.1"
        
        # 初始化智能介入引擎
        config_path = os.path.expanduser("~/.powerauto/dev_intervention_config.json")
        self.engine = DeveloperIntelligentIntervention(config_path)
        
        # 记录引擎状态
        self.is_monitoring = False
        
    def get_capabilities(self) -> List[str]:
        """获取适配器能力列表"""
        return [
            "git_checkin_reminder",
            "merge_conflict_resolution",
            "pr_review_automation",
            "code_structure_scanning",
            "manus_reference_removal",
            "pr_reviewer_setting"
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能介入引擎状态"""
        events_count = len(self.engine.events) if hasattr(self.engine, "events") else 0
        
        # 统计各类事件数量
        event_types = {}
        if hasattr(self.engine, "events"):
            for event in self.engine.events:
                event_type = event.intervention_type.value
                if event_type in event_types:
                    event_types[event_type] += 1
                else:
                    event_types[event_type] = 1
        
        return {
            "is_monitoring": self.is_monitoring,
            "events_count": events_count,
            "event_types": event_types,
            "last_check_time": datetime.now(timezone.utc).isoformat()
        }
    
    def start_monitoring(self) -> Dict[str, Any]:
        """启动智能介入监控"""
        if self.is_monitoring:
            return {
                "status": "warning",
                "message": "监控已在运行中"
            }
        
        try:
            self.engine.start_monitoring()
            self.is_monitoring = True
            return {
                "status": "success",
                "message": "智能介入监控已启动"
            }
        except Exception as e:
            logger.error(f"启动监控失败: {e}")
            return {
                "status": "error",
                "message": f"启动监控失败: {e}"
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止智能介入监控"""
        if not self.is_monitoring:
            return {
                "status": "warning",
                "message": "监控未在运行"
            }
        
        try:
            self.engine.stop_monitoring()
            self.is_monitoring = False
            return {
                "status": "success",
                "message": "智能介入监控已停止"
            }
        except Exception as e:
            logger.error(f"停止监控失败: {e}")
            return {
                "status": "error",
                "message": f"停止监控失败: {e}"
            }
    
    def get_events(self, limit: int = 10) -> Dict[str, Any]:
        """获取智能介入事件列表"""
        if not hasattr(self.engine, "events"):
            return {
                "status": "error",
                "message": "无法获取事件列表"
            }
        
        events = []
        for event in self.engine.events[-limit:]:
            events.append({
                "event_id": event.event_id,
                "type": event.intervention_type.value,
                "status": event.status.value,
                "created_at": event.created_at.isoformat(),
                "updated_at": event.updated_at.isoformat(),
                "auto_resolved": event.auto_resolved,
                "details": event.details
            })
        
        return {
            "status": "success",
            "events_count": len(self.engine.events),
            "events": events
        }
    
    def analyze_repo(self, repo_path: str) -> Dict[str, Any]:
        """分析Git仓库"""
        if not os.path.exists(repo_path):
            return {
                "status": "error",
                "message": f"仓库路径不存在: {repo_path}"
            }
        
        try:
            # 切换到仓库目录
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # 获取Git状态
            from shared_core.engines.developer_intelligent_intervention import GitHelper
            
            uncommitted_changes = GitHelper.get_uncommitted_changes()
            last_commit_time = GitHelper.get_last_commit_time()
            has_conflicts = GitHelper.has_merge_conflicts()
            conflict_files = GitHelper.get_conflict_files() if has_conflicts else []
            
            # 扫描代码规范
            issues = []
            if hasattr(self.engine, "code_scanner"):
                issues = self.engine.code_scanner.scan_directory(repo_path)
            
            # 恢复原目录
            os.chdir(original_dir)
            
            return {
                "status": "success",
                "repo_path": repo_path,
                "git_status": {
                    "uncommitted_changes": uncommitted_changes,
                    "uncommitted_count": len(uncommitted_changes),
                    "last_commit_time": last_commit_time.isoformat() if last_commit_time else None,
                    "has_conflicts": has_conflicts,
                    "conflict_files": conflict_files,
                    "conflict_count": len(conflict_files)
                },
                "code_issues": {
                    "issues_count": len(issues),
                    "issues": issues[:10]  # 只返回前10个问题
                }
            }
            
        except Exception as e:
            logger.error(f"分析仓库失败: {e}")
            return {
                "status": "error",
                "message": f"分析仓库失败: {e}"
            }
    
    def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新智能介入配置"""
        try:
            # 获取当前配置
            current_config = self.engine.config
            
            # 更新配置
            for key, value in config_data.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            
            # 保存配置到文件
            config_path = os.path.expanduser("~/.powerauto/dev_intervention_config.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "git_checkin_reminder_interval": current_config.git_checkin_reminder_interval,
                    "git_auto_checkin_timeout": current_config.git_auto_checkin_timeout,
                    "git_ignored_paths": current_config.git_ignored_paths,
                    "conflict_auto_resolve": current_config.conflict_auto_resolve,
                    "conflict_resolution_strategy": current_config.conflict_resolution_strategy,
                    "pr_auto_review": current_config.pr_auto_review,
                    "pr_reviewer": current_config.pr_reviewer,
                    "code_scan_interval": current_config.code_scan_interval,
                    "manus_removal_enabled": current_config.manus_removal_enabled,
                    "manus_replacement": current_config.manus_replacement
                }, f, indent=2)
            
            return {
                "status": "success",
                "message": "配置已更新",
                "config": {
                    "git_checkin_reminder_interval": current_config.git_checkin_reminder_interval,
                    "git_auto_checkin_timeout": current_config.git_auto_checkin_timeout,
                    "conflict_auto_resolve": current_config.conflict_auto_resolve,
                    "conflict_resolution_strategy": current_config.conflict_resolution_strategy,
                    "pr_auto_review": current_config.pr_auto_review,
                    "pr_reviewer": current_config.pr_reviewer,
                    "code_scan_interval": current_config.code_scan_interval,
                    "manus_removal_enabled": current_config.manus_removal_enabled,
                    "manus_replacement": current_config.manus_replacement
                }
            }
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return {
                "status": "error",
                "message": f"更新配置失败: {e}"
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        action = request.get("action", "")
        parameters = request.get("parameters", {})
        
        if action == "get_capabilities":
            return {
                "status": "success",
                "capabilities": self.get_capabilities()
            }
        
        elif action == "get_status":
            return self.get_status()
        
        elif action == "start_monitoring":
            return self.start_monitoring()
        
        elif action == "stop_monitoring":
            return self.stop_monitoring()
        
        elif action == "get_events":
            limit = parameters.get("limit", 10)
            return self.get_events(limit)
        
        elif action == "analyze_repo":
            repo_path = parameters.get("repo_path", "")
            if not repo_path:
                return {
                    "status": "error",
                    "message": "缺少仓库路径参数"
                }
            return self.analyze_repo(repo_path)
        
        elif action == "update_config":
            config_data = parameters.get("config", {})
            if not config_data:
                return {
                    "status": "error",
                    "message": "缺少配置参数"
                }
            return self.update_config(config_data)
        
        else:
            return {
                "status": "error",
                "message": f"未知操作: {action}"
            }

# 注册适配器
def register_adapter():
    """注册智能介入MCP适配器"""
    return {
        "id": "developer.intelligent_intervention",
        "name": "开发端智能介入适配器",
        "description": "PowerAutomation开发端智能介入适配器，提供Git监控、合并冲突解决、代码规范扫描等功能",
        "category": "developer",
        "version": "0.6.1",
        "class": DeveloperIntelligentInterventionMCP
    }
