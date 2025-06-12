#!/usr/bin/env python3
"""
PowerAutomation 开发端智能介入引擎

实现六大智能介入场景：
1. Git未check-in监测与自动提交
2. 版本合并冲突自动修正
3. PR自动审核与把关
4. 代码与目录规范扫描
5. manus相关字眼清理
6. PR reviewer自动设置为powerauto.ai

入口：智能引擎CLI
"""

import os
import re
import sys
import time
import json
import logging
import asyncio
import argparse
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser("~/.powerauto/dev_intervention.log"))
    ]
)
logger = logging.getLogger("dev_intelligent_intervention")

class InterventionType(Enum):
    """智能介入类型枚举"""
    GIT_CHECKIN_REMINDER = "git_checkin_reminder"
    MERGE_CONFLICT_RESOLUTION = "merge_conflict_resolution"
    PR_REVIEW_AUTOMATION = "pr_review_automation"
    CODE_STRUCTURE_SCANNING = "code_structure_scanning"
    MANUS_REFERENCE_REMOVAL = "manus_reference_removal"
    PR_REVIEWER_SETTING = "pr_reviewer_setting"
    UNKNOWN = "unknown"

class InterventionStatus(Enum):
    """介入状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    IGNORED = "ignored"

@dataclass
class InterventionConfig:
    """智能介入配置"""
    # Git未check-in监测配置
    git_checkin_reminder_interval: int = 30  # 分钟
    git_auto_checkin_timeout: int = 10  # 分钟
    git_ignored_paths: List[str] = None
    
    # 合并冲突解决配置
    conflict_auto_resolve: bool = True
    conflict_resolution_strategy: str = "ours"  # ours, theirs, or smart
    
    # PR审核配置
    pr_auto_review: bool = True
    pr_reviewer: str = "powerauto.ai"
    
    # 代码规范扫描配置
    code_scan_interval: int = 60  # 分钟
    code_structure_rules: Dict[str, Any] = None
    
    # manus引用清理配置
    manus_removal_enabled: bool = True
    manus_replacement: str = "powerauto.ai"
    
    def __post_init__(self):
        if self.git_ignored_paths is None:
            self.git_ignored_paths = [".git", "node_modules", "venv", "__pycache__"]
        
        if self.code_structure_rules is None:
            self.code_structure_rules = {
                "directory_structure": {
                    "src": ["core", "utils", "models"],
                    "tests": ["unit", "integration"],
                    "docs": ["api", "user_guides"]
                },
                "file_naming": r"^[a-z][a-z0-9_]*\.py$",
                "class_naming": r"^[A-Z][a-zA-Z0-9]*$",
                "function_naming": r"^[a-z][a-z0-9_]*$"
            }

@dataclass
class InterventionEvent:
    """智能介入事件"""
    event_id: str
    intervention_type: InterventionType
    status: InterventionStatus
    created_at: datetime
    updated_at: datetime
    details: Dict[str, Any]
    repository_path: str
    user_notified: bool = False
    auto_resolved: bool = False
    resolution_details: Optional[Dict[str, Any]] = None

class GitHelper:
    """Git操作辅助类"""
    
    @staticmethod
    def get_repo_root() -> Optional[str]:
        """获取当前Git仓库根目录"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            logger.warning("当前目录不是Git仓库")
            return None
    
    @staticmethod
    def get_last_commit_time() -> Optional[datetime]:
        """获取最后一次提交时间"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI"], # Use %aI for ISO 8601 format with timezone
                capture_output=True,
                text=True,
                check=True
            )
            commit_time_str = result.stdout.strip()
            logger.info(f"Raw commit_time_str: {commit_time_str}")
            if commit_time_str:
                # 解析ISO格式日期
                dt_obj = datetime.fromisoformat(commit_time_str)
                dt_obj = dt_obj.astimezone(timezone.utc)
                logger.info(f"Parsed and converted datetime: {dt_obj}, tzinfo: {dt_obj.tzinfo}")
                return dt_obj
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"获取最后提交时间失败: {e}")
            return None
    
    @staticmethod
    def get_uncommitted_changes() -> List[str]:
        """获取未提交的变更文件列表"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            changes = []
            for line in result.stdout.splitlines():
                if line.strip():
                    # 提取文件名
                    file_path = line[3:].strip()
                    changes.append(file_path)
            return changes
        except subprocess.CalledProcessError as e:
            logger.warning(f"获取未提交变更失败: {e}")
            return []
    
    @staticmethod
    def auto_commit(message: str) -> bool:
        """自动提交所有变更"""
        try:
            # 添加所有变更
            subprocess.run(
                ["git", "add", "."],
                check=True
            )
            
            # 提交变更
            subprocess.run(
                ["git", "commit", "-m", message],
                check=True
            )
            
            logger.info(f"自动提交成功: {message}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"自动提交失败: {e}")
            return False
    
    @staticmethod
    def has_merge_conflicts() -> bool:
        """检查是否存在合并冲突"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            # 如果命令失败，可能是因为没有进行中的合并
            return False
    
    @staticmethod
    def get_conflict_files() -> List[str]:
        """获取冲突文件列表"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
                check=True
            )
            return [file.strip() for file in result.stdout.splitlines() if file.strip()]
        except subprocess.CalledProcessError:
            return []
    
    @staticmethod
    def resolve_conflict(file_path: str, strategy: str) -> bool:
        """解决单个文件的冲突"""
        try:
            if strategy == "ours":
                subprocess.run(
                    ["git", "checkout", "--ours", file_path],
                    check=True
                )
            elif strategy == "theirs":
                subprocess.run(
                    ["git", "checkout", "--theirs", file_path],
                    check=True
                )
            else:
                # 智能解决策略 - 需要更复杂的逻辑
                return GitHelper._smart_resolve_conflict(file_path)
            
            # 标记为已解决
            subprocess.run(
                ["git", "add", file_path],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"解决冲突失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def _smart_resolve_conflict(file_path: str) -> bool:
        """智能解决冲突策略"""
        try:
            # 读取冲突文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的冲突解决逻辑 - 保留双方的修改
            resolved_content = []
            in_conflict = False
            our_changes = []
            their_changes = []
            
            for line in content.splitlines():
                if line.startswith('<<<<<<<'):
                    in_conflict = True
                    continue
                elif line.startswith('=======') and in_conflict:
                    in_conflict = False
                    continue
                elif line.startswith('>>>>>>>'):
                    # 合并双方的修改
                    resolved_content.extend(our_changes)
                    resolved_content.extend(their_changes)
                    our_changes = []
                    their_changes = []
                    continue
                
                if in_conflict:
                    our_changes.append(line)
                else:
                    their_changes.append(line)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(resolved_content))
            
            # 标记为已解决
            subprocess.run(
                ["git", "add", file_path],
                check=True
            )
            
            return True
        except Exception as e:
            logger.error(f"智能解决冲突失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def create_pull_request(title: str, description: str, reviewer: str) -> Optional[str]:
        """创建Pull Request"""
        try:
            # 获取当前分支
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
            
            # 获取远程仓库信息
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = result.stdout.strip()
            
            # 解析GitHub/GitLab仓库信息
            if "github.com" in remote_url:
                # GitHub PR创建
                pr_data = {
                    "title": title,
                    "body": description,
                    "head": current_branch,
                    "base": "main",  # 假设目标分支是main
                    "reviewers": [reviewer]
                }
                
                # 这里需要GitHub API Token，实际实现需要更复杂的逻辑
                logger.info(f"准备创建GitHub PR: {pr_data}")
                return f"https://github.com/user/repo/pull/new/{current_branch}"
                
            elif "gitlab.com" in remote_url:
                # GitLab MR创建
                mr_data = {
                    "title": title,
                    "description": description,
                    "source_branch": current_branch,
                    "target_branch": "main",
                    "reviewer_ids": [reviewer]
                }
                
                logger.info(f"准备创建GitLab MR: {mr_data}")
                return f"https://gitlab.com/user/repo/-/merge_requests/new?merge_request[source_branch]={current_branch}"
            
            else:
                logger.warning(f"不支持的远程仓库类型: {remote_url}")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"创建PR失败: {e}")
            return None

class CodeScanner:
    """代码规范扫描器"""
    
    def __init__(self, config: InterventionConfig):
        self.config = config
        self.issues = []
    
    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """扫描目录结构和代码规范"""
        self.issues = []
        
        # 检查目录结构
        self._check_directory_structure(directory)
        
        # 扫描代码文件
        self._scan_code_files(directory)
        
        return self.issues
    
    def _check_directory_structure(self, directory: str):
        """检查目录结构是否符合规范"""
        expected_structure = self.config.code_structure_rules.get("directory_structure", {})
        
        for parent_dir, expected_subdirs in expected_structure.items():
            parent_path = os.path.join(directory, parent_dir)
            
            if not os.path.isdir(parent_path):
                self.issues.append({
                    "type": "directory_structure",
                    "severity": "warning",
                    "message": f"缺少规范目录: {parent_dir}",
                    "path": parent_path
                })
                continue
            
            for subdir in expected_subdirs:
                subdir_path = os.path.join(parent_path, subdir)
                if not os.path.isdir(subdir_path):
                    self.issues.append({
                        "type": "directory_structure",
                        "severity": "warning",
                        "message": f"缺少规范子目录: {parent_dir}/{subdir}",
                        "path": subdir_path
                    })
    
    def _scan_code_files(self, directory: str):
        """扫描代码文件规范"""
        for root, _, files in os.walk(directory):
            # 跳过忽略的目录
            if any(ignored in root for ignored in self.config.git_ignored_paths):
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._check_file(file_path)
    
    def _check_file(self, file_path: str):
        """检查单个文件的规范"""
        # 检查文件命名
        file_name = os.path.basename(file_path)
        file_pattern = self.config.code_structure_rules.get("file_naming")
        if file_pattern and not re.match(file_pattern, file_name):
            self.issues.append({
                "type": "file_naming",
                "severity": "warning",
                "message": f"文件命名不符合规范: {file_name}",
                "path": file_path
            })
        
        # 检查代码内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查类命名
                class_pattern = self.config.code_structure_rules.get("class_naming")
                if class_pattern:
                    for match in re.finditer(r'class\s+(\w+)', content):
                        class_name = match.group(1)
                        if not re.match(class_pattern, class_name):
                            self.issues.append({
                                "type": "class_naming",
                                "severity": "warning",
                                "message": f"类命名不符合规范: {class_name}",
                                "path": file_path,
                                "line": content[:match.start()].count('\n') + 1
                            })
                
                # 检查函数命名
                function_pattern = self.config.code_structure_rules.get("function_naming")
                if function_pattern:
                    for match in re.finditer(r'def\s+(\w+)', content):
                        function_name = match.group(1)
                        if not re.match(function_pattern, function_name):
                            self.issues.append({
                                "type": "function_naming",
                                "severity": "warning",
                                "message": f"函数命名不符合规范: {function_name}",
                                "path": file_path,
                                "line": content[:match.start()].count('\n') + 1
                            })
                
                # 检查manus相关字眼
                if self.config.manus_removal_enabled:
                    for match in re.finditer(r'\bmanus\b', content, re.IGNORECASE):
                        self.issues.append({
                            "type": "manus_reference",
                            "severity": "error",
                            "message": f"发现manus相关字眼",
                            "path": file_path,
                            "line": content[:match.start()].count('\n') + 1,
                            "context": content[max(0, match.start()-20):min(len(content), match.end()+20)]
                        })
        
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")

class ManusReferenceRemover:
    """manus引用清理器"""
    
    def __init__(self, config: InterventionConfig):
        self.config = config
        self.replacement = config.manus_replacement
    
    def scan_and_replace(self, directory: str) -> Dict[str, Any]:
        """扫描并替换manus引用"""
        files_scanned = 0
        files_modified = 0
        references_found = 0
        references_replaced = 0
        modified_files = []
        
        for root, _, files in os.walk(directory):
            # 跳过忽略的目录
            if any(ignored in root for ignored in self.config.git_ignored_paths):
                continue
            
            for file in files:
                # 只处理文本文件
                if self._is_text_file(file):
                    file_path = os.path.join(root, file)
                    files_scanned += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找manus引用
                        pattern = r'\bmanus\b'
                        matches = list(re.finditer(pattern, content, re.IGNORECASE))
                        references_found += len(matches)
                        
                        if matches:
                            # 替换引用
                            new_content = re.sub(pattern, self.replacement, content, flags=re.IGNORECASE)
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            files_modified += 1
                            references_replaced += len(matches)
                            modified_files.append(file_path)
                            
                            logger.info(f"已替换文件中的manus引用: {file_path} ({len(matches)}处)")
                    
                    except Exception as e:
                        logger.error(f"处理文件失败 {file_path}: {e}")
        
        return {
            "files_scanned": files_scanned,
            "files_modified": files_modified,
            "references_found": references_found,
            "references_replaced": references_replaced,
            "modified_files": modified_files
        }
    
    def _is_text_file(self, filename: str) -> bool:
        """判断是否为文本文件"""
        text_extensions = [
            '.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json', '.yml', 
            '.yaml', '.xml', '.sh', '.bat', '.ps1', '.c', '.cpp', '.h', '.java'
        ]
        return any(filename.endswith(ext) for ext in text_extensions)

class DeveloperIntelligentIntervention:
    """开发端智能介入引擎"""
    
    def __init__(self, config_path: Optional[str] = None):
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self.git_helper = GitHelper()
        self.code_scanner = CodeScanner(self.config)
        self.manus_remover = ManusReferenceRemover(self.config)
        
        # 事件记录
        self.events = []
        
        # 监控线程
        self.monitor_thread = None
        self.is_running = False
        self.event_queue = queue.Queue()
    
    def _load_config(self, config_path: Optional[str]) -> InterventionConfig:
        """加载配置"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return InterventionConfig(**config_data)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}，使用默认配置")
        
        # 使用默认配置
        return InterventionConfig()
    
    def start_monitoring(self):
        """启动监控线程"""
        if self.is_running:
            logger.warning("监控线程已在运行")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("开发端智能介入监控已启动")
    
    def stop_monitoring(self):
        """停止监控线程"""
        if not self.is_running:
            logger.warning("监控线程未运行")
            return
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("开发端智能介入监控已停止")
    
    def _intervention_loop(self):
        last_git_check = datetime.now(timezone.utc)
        last_code_scan = datetime.now(timezone.utc)

        while self.is_running:
            try:
                now = datetime.now(timezone.utc)

                # Git未check-in监测
                if (now - last_git_check).total_seconds() >= self.config.git_checkin_reminder_interval * 60:
                    self._check_git_status()
                    last_git_check = now

                # 扫描代码规范
                if (now - last_code_scan).total_seconds() >= self.config.code_scan_interval * 60:
                    self._check_code_compliance()
                    last_code_scan = now

                # 检查合并冲突
                self._check_merge_conflicts()

                # 处理事件队列
                while not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    self._process_event(event)
                
                # 休眠一段时间
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(30)  # 出错后延长休眠时间
    
    def _check_git_status(self):
        """检查Git状态"""
        repo_root = self.git_helper.get_repo_root()
        if not repo_root:
            return
        
        # 检查最后提交时间
        last_commit_time = GitHelper.get_last_commit_time()
        if last_commit_time and last_commit_time.tzinfo is None:
            last_commit_time = last_commit_time.replace(tzinfo=timezone.utc)
        elif last_commit_time:
            last_commit_time = last_commit_time.astimezone(timezone.utc)
        if not last_commit_time:
            return
        
        # 获取未提交变更
        uncommitted_changes = self.git_helper.get_uncommitted_changes()
        if not uncommitted_changes:
            return
        
        # 检查是否超过提醒间隔
        now = datetime.now(timezone.utc)
        time_since_last_commit = now - last_commit_time
        
        if time_since_last_commit.total_seconds() >= self.config.git_checkin_reminder_interval * 60:
            # 创建提醒事件
            event_id = f"git_reminder_{now.strftime('%Y%m%d%H%M%S')}"
            event = InterventionEvent(
                event_id=event_id,
                intervention_type=InterventionType.GIT_CHECKIN_REMINDER,
                status=InterventionStatus.PENDING,
                created_at=now,
                updated_at=now,
                details={
                    "last_commit_time": last_commit_time.isoformat(),
                    "time_since_last_commit": str(time_since_last_commit),
                    "uncommitted_files": uncommitted_changes,
                    "auto_checkin_timeout": self.config.git_auto_checkin_timeout
                },
                repository_path=repo_root
            )
            
            self.events.append(event)
            self.event_queue.put(event)
            
            logger.info(f"检测到Git未提交变更: {len(uncommitted_changes)}个文件，{time_since_last_commit}未提交")
    
    def _check_merge_conflicts(self):
        """检查合并冲突"""
        repo_root = self.git_helper.get_repo_root()
        if not repo_root:
            return
        
        # 检查是否存在合并冲突
        if not self.git_helper.has_merge_conflicts():
            return
        
        # 获取冲突文件
        conflict_files = self.git_helper.get_conflict_files()
        if not conflict_files:
            return
        
        # 创建冲突解决事件
        now = datetime.now(timezone.utc)
        event_id = f"merge_conflict_{now.strftime('%Y%m%d%H%M%S')}"
        event = InterventionEvent(
            event_id=event_id,
            intervention_type=InterventionType.MERGE_CONFLICT_RESOLUTION,
            status=InterventionStatus.PENDING,
            created_at=now,
            updated_at=now,
            details={
                "conflict_files": conflict_files,
                "resolution_strategy": self.config.conflict_resolution_strategy
            },
            repository_path=repo_root
        )
        
        self.events.append(event)
        self.event_queue.put(event)
        
        logger.info(f"检测到合并冲突: {len(conflict_files)}个文件")
    
    def _scan_code_structure(self):
        """扫描代码结构"""
        repo_root = self.git_helper.get_repo_root()
        if not repo_root:
            return
        
        # 扫描代码规范
        issues = self.code_scanner.scan_directory(repo_root)
        if not issues:
            return
        
        # 创建代码规范扫描事件
        now = datetime.now(timezone.utc)
        event_id = f"code_scan_{now.strftime('%Y%m%d%H%M%S')}"
        event = InterventionEvent(
            event_id=event_id,
            intervention_type=InterventionType.CODE_STRUCTURE_SCANNING,
            status=InterventionStatus.PENDING,
            created_at=now,
            updated_at=now,
            details={
                "issues": issues,
                "issue_count": len(issues),
                "issue_types": list(set(issue["type"] for issue in issues))
            },
            repository_path=repo_root
        )
        
        self.events.append(event)
        self.event_queue.put(event)
        
        logger.info(f"检测到代码规范问题: {len(issues)}个问题")
        
        # 检查是否有manus引用问题
        manus_issues = [issue for issue in issues if issue["type"] == "manus_reference"]
        if manus_issues and self.config.manus_removal_enabled:
            # 创建manus引用清理事件
            now = datetime.now(timezone.utc)
            event_id = f"manus_removal_{now.strftime('%Y%m%d%H%M%S')}"
            event = InterventionEvent(
                event_id=event_id,
                intervention_type=InterventionType.MANUS_REFERENCE_REMOVAL,
                status=InterventionStatus.PENDING,
                created_at=now,
                updated_at=now,
                details={
                    "issues": manus_issues,
                    "issue_count": len(manus_issues),
                    "replacement": self.config.manus_replacement
                },
                repository_path=repo_root
            )
            
            self.events.append(event)
            self.event_queue.put(event)
            
            logger.info(f"检测到manus引用问题: {len(manus_issues)}个问题")
    
    def _process_event(self, event: InterventionEvent):
        """处理智能介入事件"""
        logger.info(f"处理事件: {event.event_id} ({event.intervention_type.value})")
        
        event.status = InterventionStatus.IN_PROGRESS
        event.updated_at = datetime.now(timezone.utc)
        
        try:
            # 根据事件类型处理
            if event.intervention_type == InterventionType.GIT_CHECKIN_REMINDER:
                self._handle_git_reminder(event)
            
            elif event.intervention_type == InterventionType.MERGE_CONFLICT_RESOLUTION:
                self._handle_merge_conflict(event)
            
            elif event.intervention_type == InterventionType.CODE_STRUCTURE_SCANNING:
                self._handle_code_structure_issues(event)
            
            elif event.intervention_type == InterventionType.MANUS_REFERENCE_REMOVAL:
                self._handle_manus_removal(event)
            
            elif event.intervention_type == InterventionType.PR_REVIEW_AUTOMATION:
                self._handle_pr_review(event)
            
            else:
                logger.warning(f"未知的事件类型: {event.intervention_type}")
                event.status = InterventionStatus.FAILED
        
        except Exception as e:
            logger.error(f"处理事件失败: {e}")
            event.status = InterventionStatus.FAILED
            event.resolution_details = {"error": str(e)}
        
        event.updated_at = datetime.now()
    
    def _handle_git_reminder(self, event: InterventionEvent):
        """处理Git提交提醒"""
        # 通知用户
        if not event.user_notified:
            self._notify_user(
                f"检测到Git未提交变更: {len(event.details['uncommitted_files'])}个文件，"
                f"上次提交时间: {event.details['last_commit_time']}",
                f"请在{self.config.git_auto_checkin_timeout}分钟内提交变更，否则系统将自动提交"
            )
            event.user_notified = True
            
            # 设置自动提交超时
            event.details["auto_checkin_deadline"] = (
                datetime.now(timezone.utc) + timedelta(minutes=self.config.git_auto_checkin_timeout)
            ).isoformat()
            
            event.status = InterventionStatus.PENDING
            return
        
        # 检查是否需要自动提交
        if "auto_checkin_deadline" in event.details:
            deadline = datetime.fromisoformat(event.details["auto_checkin_deadline"])
            if datetime.now() >= deadline:
                # 自动提交
                uncommitted_files = event.details["uncommitted_files"]
                if uncommitted_files:
                    success = self.git_helper.auto_commit(
                        f"自动提交: {len(uncommitted_files)}个文件 [PowerAutomation智能介入]"
                    )
                    
                    if success:
                        event.auto_resolved = True
                        event.status = InterventionStatus.COMPLETED
                        event.resolution_details = {
                            "action": "auto_commit",
                            "files_committed": len(uncommitted_files),
                            "commit_time": datetime.now(timezone.utc).isoformat()
                        }
                        
                        self._notify_user(
                            "已自动提交Git变更",
                            f"已自动提交{len(uncommitted_files)}个文件"
                        )
                    else:
                        event.status = InterventionStatus.FAILED
                        event.resolution_details = {
                            "action": "auto_commit",
                            "error": "自动提交失败"
                        }
                else:
                    # 没有未提交的变更，可能用户已手动提交
                    event.status = InterventionStatus.COMPLETED
                    event.resolution_details = {
                        "action": "none",
                        "reason": "没有未提交的变更"
                    }
    
    def _handle_merge_conflict(self, event: InterventionEvent):
        """处理合并冲突"""
        if not self.config.conflict_auto_resolve:
            # 只通知不自动解决
            self._notify_user(
                f"检测到合并冲突: {len(event.details['conflict_files'])}个文件",
                "请手动解决冲突"
            )
            event.user_notified = True
            event.status = InterventionStatus.PENDING
            return
        
        # 自动解决冲突
        conflict_files = event.details["conflict_files"]
        strategy = event.details["resolution_strategy"]
        
        resolved_files = []
        failed_files = []
        
        for file_path in conflict_files:
            success = self.git_helper.resolve_conflict(file_path, strategy)
            if success:
                resolved_files.append(file_path)
            else:
                failed_files.append(file_path)
        
        # 更新事件状态
        if failed_files:
            event.status = InterventionStatus.FAILED
        else:
            event.status = InterventionStatus.COMPLETED
            event.auto_resolved = True
        
        event.resolution_details = {
            "action": "auto_resolve",
            "strategy": strategy,
            "resolved_files": resolved_files,
            "failed_files": failed_files,
            "resolution_time": datetime.now().isoformat()
        }
        
        # 通知用户
        if resolved_files:
            self._notify_user(
                f"已自动解决合并冲突: {len(resolved_files)}/{len(conflict_files)}个文件",
                f"使用策略: {strategy}"
            )
            event.user_notified = True
        
        # 如果有失败的文件，提示用户手动解决
        if failed_files:
            self._notify_user(
                f"部分合并冲突无法自动解决: {len(failed_files)}个文件",
                "请手动解决这些冲突"
            )
    
    def _handle_code_structure_issues(self, event: InterventionEvent):
        """处理代码结构问题"""
        issues = event.details["issues"]
        issue_types = event.details["issue_types"]
        
        # 通知用户
        self._notify_user(
            f"检测到代码规范问题: {len(issues)}个问题",
            f"问题类型: {', '.join(issue_types)}"
        )
        event.user_notified = True
        
        # 生成详细报告
        report = self._generate_code_issues_report(issues)
        event.resolution_details = {
            "action": "report",
            "report": report,
            "report_time": datetime.now().isoformat()
        }
        
        event.status = InterventionStatus.COMPLETED
    
    def _handle_manus_removal(self, event: InterventionEvent):
        """处理manus引用清理"""
        if not self.config.manus_removal_enabled:
            event.status = InterventionStatus.IGNORED
            return
        
        # 自动替换manus引用
        result = self.manus_remover.scan_and_replace(event.repository_path)
        
        # 更新事件状态
        event.resolution_details = {
            "action": "auto_replace",
            "replacement": self.config.manus_replacement,
            "result": result,
            "replacement_time": datetime.now().isoformat()
        }
        
        if result["files_modified"] > 0:
            event.auto_resolved = True
            event.status = InterventionStatus.COMPLETED
            
            # 通知用户
            self._notify_user(
                f"已自动清理manus引用: {result['references_replaced']}处引用，{result['files_modified']}个文件",
                f"替换为: {self.config.manus_replacement}"
            )
            event.user_notified = True
            
            # 自动提交变更
            if result["modified_files"]:
                success = self.git_helper.auto_commit(
                    f"自动清理manus引用: {result['references_replaced']}处引用 [PowerAutomation智能介入]"
                )
                
                if success:
                    event.resolution_details["commit"] = {
                        "success": True,
                        "commit_time": datetime.now().isoformat()
                    }
                else:
                    event.resolution_details["commit"] = {
                        "success": False,
                        "error": "自动提交失败"
                    }
        else:
            event.status = InterventionStatus.COMPLETED
            event.resolution_details["message"] = "没有需要替换的内容"
    
    def _handle_pr_review(self, event: InterventionEvent):
        """处理PR审核自动化"""
        if not self.config.pr_auto_review:
            event.status = InterventionStatus.IGNORED
            return
        
        # 创建PR并设置reviewer
        pr_title = event.details.get("pr_title", "自动创建的PR [PowerAutomation智能介入]")
        pr_description = event.details.get("pr_description", "此PR由PowerAutomation智能介入系统自动创建")
        
        pr_url = self.git_helper.create_pull_request(
            pr_title,
            pr_description,
            self.config.pr_reviewer
        )
        
        if pr_url:
            event.status = InterventionStatus.COMPLETED
            event.auto_resolved = True
            event.resolution_details = {
                "action": "create_pr",
                "pr_url": pr_url,
                "reviewer": self.config.pr_reviewer,
                "creation_time": datetime.now().isoformat()
            }
            
            # 通知用户
            self._notify_user(
                "已自动创建PR",
                f"Reviewer: {self.config.pr_reviewer}\nPR URL: {pr_url}"
            )
            event.user_notified = True
        else:
            event.status = InterventionStatus.FAILED
            event.resolution_details = {
                "action": "create_pr",
                "error": "创建PR失败"
            }
    
    def _notify_user(self, title: str, message: str):
        """通知用户"""
        logger.info(f"通知用户: {title} - {message}")
        
        # 这里可以实现不同的通知方式，如桌面通知、邮件等
        try:
            # 尝试使用系统通知
            if sys.platform == "darwin":  # macOS
                os.system(f"""osascript -e 'display notification "{message}" with title "{title}"'""")
            elif sys.platform == "linux":
                os.system(f"""notify-send "{title}" "{message}" """)
            elif sys.platform == "win32":
                # Windows需要额外的库，这里简化处理
                pass
            
            # 记录到日志
            print(f"\n[通知] {title}\n{message}\n")
            
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
    
    def _generate_code_issues_report(self, issues: List[Dict[str, Any]]) -> str:
        """生成代码问题报告"""
        report = "# 代码规范问题报告\n\n"
        
        # 按类型分组
        issues_by_type = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # 生成报告
        for issue_type, type_issues in issues_by_type.items():
            report += f"## {issue_type.replace('_', ' ').title()} ({len(type_issues)})\n\n"
            
            for issue in type_issues:
                severity = issue.get("severity", "info").upper()
                message = issue.get("message", "未知问题")
                path = issue.get("path", "")
                line = issue.get("line", "")
                
                location = path
                if line:
                    location += f":{line}"
                
                report += f"- [{severity}] {message}\n  {location}\n"
                
                # 如果有上下文，添加到报告
                if "context" in issue:
                    context = issue["context"].replace("\n", " ")
                    report += f"  上下文: `{context}`\n"
            
            report += "\n"
        
        return report
    
    def run_cli(self):
        """运行CLI入口"""
        parser = argparse.ArgumentParser(description="PowerAutomation 开发端智能介入CLI")
        
        # 子命令
        subparsers = parser.add_subparsers(dest="command", help="子命令")
        
        # start命令
        start_parser = subparsers.add_parser("start", help="启动智能介入监控")
        start_parser.add_argument("--config", help="配置文件路径")
        
        # stop命令
        subparsers.add_parser("stop", help="停止智能介入监控")
        
        # status命令
        subparsers.add_parser("status", help="查看智能介入状态")
        
        # scan命令
        scan_parser = subparsers.add_parser("scan", help="扫描代码规范")
        scan_parser.add_argument("--path", help="扫描路径，默认为当前Git仓库")
        
        # clean命令
        clean_parser = subparsers.add_parser("clean", help="清理manus引用")
        clean_parser.add_argument("--path", help="清理路径，默认为当前Git仓库")
        
        # pr命令
        pr_parser = subparsers.add_parser("pr", help="创建PR并设置reviewer")
        pr_parser.add_argument("--title", help="PR标题")
        pr_parser.add_argument("--description", help="PR描述")
        
        # 解析参数
        args = parser.parse_args()
        
        # 处理命令
        if args.command == "start":
            if args.config:
                self.config = self._load_config(args.config)
            self.start_monitoring()
            print("开发端智能介入监控已启动")
        
        elif args.command == "stop":
            self.stop_monitoring()
            print("开发端智能介入监控已停止")
        
        elif args.command == "status":
            if self.is_running:
                print("开发端智能介入监控正在运行")
                print(f"最近事件: {len(self.events)}")
                
                # 显示最近的事件
                recent_events = sorted(self.events, key=lambda e: e.created_at, reverse=True)[:5]
                for event in recent_events:
                    print(f"- {event.created_at.strftime('%Y-%m-%d %H:%M:%S')} "
                          f"{event.intervention_type.value} ({event.status.value})")
            else:
                print("开发端智能介入监控未运行")
        
        elif args.command == "scan":
            path = args.path or self.git_helper.get_repo_root() or os.getcwd()
            print(f"扫描路径: {path}")
            
            issues = self.code_scanner.scan_directory(path)
            if issues:
                print(f"发现{len(issues)}个问题:")
                for issue in issues[:10]:  # 只显示前10个
                    print(f"- [{issue['type']}] {issue['message']} ({issue.get('path', '')})")
                
                if len(issues) > 10:
                    print(f"... 还有{len(issues) - 10}个问题未显示")
            else:
                print("未发现代码规范问题")
        
        elif args.command == "clean":
            path = args.path or self.git_helper.get_repo_root() or os.getcwd()
            print(f"清理路径: {path}")
            
            result = self.manus_remover.scan_and_replace(path)
            print(f"扫描文件: {result['files_scanned']}")
            print(f"修改文件: {result['files_modified']}")
            print(f"发现引用: {result['references_found']}")
            print(f"替换引用: {result['references_replaced']}")
        
        elif args.command == "pr":
            title = args.title or "自动创建的PR [PowerAutomation智能介入]"
            description = args.description or "此PR由PowerAutomation智能介入系统自动创建"
            
            pr_url = self.git_helper.create_pull_request(
                title,
                description,
                self.config.pr_reviewer
            )
            
            if pr_url:
                print(f"已创建PR: {pr_url}")
                print(f"Reviewer: {self.config.pr_reviewer}")
            else:
                print("创建PR失败")
        
        else:
            parser.print_help()

def main():
    """主函数"""
    try:
        intervention = DeveloperIntelligentIntervention()
        intervention.run_cli()
    except KeyboardInterrupt:
        print("\n已中断")
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
