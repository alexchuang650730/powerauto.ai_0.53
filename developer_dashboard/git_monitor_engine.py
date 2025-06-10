#!/usr/bin/env python3
"""
PowerAutomation Git狀態監控引擎

專門負責深度監控Git倉庫狀態，提供詳細的Git操作分析和建議
"""

import os
import json
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class GitFileStatus:
    """單個文件的Git狀態"""
    path: str
    status: str  # 'modified', 'added', 'deleted', 'renamed', 'untracked'
    lines_added: int
    lines_deleted: int
    size_bytes: int
    last_modified: str

@dataclass
class GitBranchInfo:
    """分支信息"""
    name: str
    is_current: bool
    last_commit: str
    commits_ahead: int
    commits_behind: int
    tracking_branch: Optional[str]

@dataclass
class GitCommitInfo:
    """提交信息"""
    hash: str
    author: str
    date: str
    message: str
    files_changed: int
    insertions: int
    deletions: int

@dataclass
class GitRemoteInfo:
    """遠程倉庫信息"""
    name: str
    url: str
    fetch_url: str
    push_url: str
    last_fetch: Optional[str]
    last_push: Optional[str]

@dataclass
class DetailedGitStatus:
    """詳細的Git狀態"""
    repo_path: str
    repo_name: str
    current_branch: GitBranchInfo
    all_branches: List[GitBranchInfo]
    modified_files: List[GitFileStatus]
    staged_files: List[GitFileStatus]
    untracked_files: List[GitFileStatus]
    recent_commits: List[GitCommitInfo]
    remotes: List[GitRemoteInfo]
    stash_count: int
    conflicts: List[str]
    submodules: List[str]
    total_commits: int
    repo_size_mb: float
    last_scan_time: str

class GitMonitorEngine:
    """Git監控引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger("PowerAutomation.GitMonitor")
        self.monitored_repos: Dict[str, DetailedGitStatus] = {}
        self.scan_history: List[Dict[str, Any]] = []
        
    def scan_repository_detailed(self, repo_path: str) -> DetailedGitStatus:
        """深度掃描單個Git倉庫"""
        if not os.path.exists(repo_path) or not os.path.exists(os.path.join(repo_path, '.git')):
            raise ValueError(f"不是有效的Git倉庫: {repo_path}")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(repo_path)
            
            # 獲取基本信息
            repo_name = os.path.basename(repo_path)
            
            # 獲取分支信息
            current_branch = self._get_current_branch_info()
            all_branches = self._get_all_branches()
            
            # 獲取文件狀態
            modified_files = self._get_modified_files()
            staged_files = self._get_staged_files()
            untracked_files = self._get_untracked_files()
            
            # 獲取提交歷史
            recent_commits = self._get_recent_commits(limit=10)
            
            # 獲取遠程信息
            remotes = self._get_remotes_info()
            
            # 獲取其他信息
            stash_count = self._get_stash_count()
            conflicts = self._get_conflicts()
            submodules = self._get_submodules()
            total_commits = self._get_total_commits()
            repo_size_mb = self._get_repo_size()
            
            status = DetailedGitStatus(
                repo_path=repo_path,
                repo_name=repo_name,
                current_branch=current_branch,
                all_branches=all_branches,
                modified_files=modified_files,
                staged_files=staged_files,
                untracked_files=untracked_files,
                recent_commits=recent_commits,
                remotes=remotes,
                stash_count=stash_count,
                conflicts=conflicts,
                submodules=submodules,
                total_commits=total_commits,
                repo_size_mb=repo_size_mb,
                last_scan_time=datetime.now().isoformat()
            )
            
            self.monitored_repos[repo_path] = status
            return status
            
        finally:
            os.chdir(original_cwd)
    
    def _run_git_command(self, command: str, timeout: int = 30) -> str:
        """執行Git命令並返回結果"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                self.logger.warning(f"Git命令警告: {command}, stderr: {result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.error(f"Git命令超時: {command}")
            return ""
        except Exception as e:
            self.logger.error(f"Git命令執行失敗: {command}, 錯誤: {e}")
            return ""
    
    def _get_current_branch_info(self) -> GitBranchInfo:
        """獲取當前分支信息"""
        branch_name = self._run_git_command("git branch --show-current")
        if not branch_name:
            branch_name = "HEAD"
        
        last_commit = self._run_git_command("git log -1 --format=%H")
        
        # 獲取與遠程分支的差異
        tracking_branch = self._run_git_command(f"git config branch.{branch_name}.merge")
        if tracking_branch:
            tracking_branch = tracking_branch.replace('refs/heads/', '')
            
            # 計算ahead/behind
            try:
                ahead_behind = self._run_git_command(f"git rev-list --left-right --count HEAD...origin/{tracking_branch}")
                if ahead_behind:
                    parts = ahead_behind.split('\t')
                    commits_ahead = int(parts[0]) if len(parts) > 0 else 0
                    commits_behind = int(parts[1]) if len(parts) > 1 else 0
                else:
                    commits_ahead = commits_behind = 0
            except:
                commits_ahead = commits_behind = 0
        else:
            tracking_branch = None
            commits_ahead = commits_behind = 0
        
        return GitBranchInfo(
            name=branch_name,
            is_current=True,
            last_commit=last_commit,
            commits_ahead=commits_ahead,
            commits_behind=commits_behind,
            tracking_branch=tracking_branch
        )
    
    def _get_all_branches(self) -> List[GitBranchInfo]:
        """獲取所有分支信息"""
        branches = []
        current_branch = self._run_git_command("git branch --show-current")
        
        branch_output = self._run_git_command("git branch -a")
        for line in branch_output.split('\n'):
            line = line.strip()
            if not line or line.startswith('remotes/origin/HEAD'):
                continue
                
            is_current = line.startswith('*')
            branch_name = line.replace('*', '').strip()
            
            if branch_name.startswith('remotes/origin/'):
                branch_name = branch_name.replace('remotes/origin/', '')
            
            if branch_name == current_branch:
                continue  # 已經在current_branch中處理
            
            last_commit = self._run_git_command(f"git log -1 --format=%H {branch_name}")
            
            branches.append(GitBranchInfo(
                name=branch_name,
                is_current=is_current,
                last_commit=last_commit,
                commits_ahead=0,  # 簡化處理
                commits_behind=0,
                tracking_branch=None
            ))
        
        return branches
    
    def _get_modified_files(self) -> List[GitFileStatus]:
        """獲取修改的文件"""
        files = []
        status_output = self._run_git_command("git status --porcelain")
        
        for line in status_output.split('\n'):
            if not line.strip():
                continue
                
            status_code = line[:2]
            file_path = line[3:]
            
            if status_code.strip() and not status_code.startswith('??'):
                file_status = self._parse_status_code(status_code)
                file_info = self._get_file_details(file_path, file_status)
                if file_info:
                    files.append(file_info)
        
        return files
    
    def _get_staged_files(self) -> List[GitFileStatus]:
        """獲取暫存的文件"""
        files = []
        staged_output = self._run_git_command("git diff --cached --name-status")
        
        for line in staged_output.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split('\t')
            if len(parts) >= 2:
                status_code = parts[0]
                file_path = parts[1]
                
                file_status = self._parse_diff_status(status_code)
                file_info = self._get_file_details(file_path, file_status)
                if file_info:
                    files.append(file_info)
        
        return files
    
    def _get_untracked_files(self) -> List[GitFileStatus]:
        """獲取未跟蹤的文件"""
        files = []
        untracked_output = self._run_git_command("git ls-files --others --exclude-standard")
        
        for file_path in untracked_output.split('\n'):
            if file_path.strip():
                file_info = self._get_file_details(file_path, 'untracked')
                if file_info:
                    files.append(file_info)
        
        return files
    
    def _get_file_details(self, file_path: str, status: str) -> Optional[GitFileStatus]:
        """獲取文件詳細信息"""
        try:
            if not os.path.exists(file_path):
                return GitFileStatus(
                    path=file_path,
                    status=status,
                    lines_added=0,
                    lines_deleted=0,
                    size_bytes=0,
                    last_modified="文件不存在"
                )
            
            # 獲取文件大小
            size_bytes = os.path.getsize(file_path)
            
            # 獲取最後修改時間
            mtime = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(mtime).isoformat()
            
            # 獲取行數變化（如果不是untracked文件）
            lines_added = lines_deleted = 0
            if status != 'untracked':
                diff_output = self._run_git_command(f"git diff --numstat {file_path}")
                if diff_output:
                    parts = diff_output.split('\t')
                    if len(parts) >= 2:
                        try:
                            lines_added = int(parts[0]) if parts[0] != '-' else 0
                            lines_deleted = int(parts[1]) if parts[1] != '-' else 0
                        except ValueError:
                            pass
            
            return GitFileStatus(
                path=file_path,
                status=status,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
                size_bytes=size_bytes,
                last_modified=last_modified
            )
            
        except Exception as e:
            self.logger.error(f"獲取文件詳情失敗 {file_path}: {e}")
            return None
    
    def _parse_status_code(self, code: str) -> str:
        """解析Git狀態代碼"""
        code = code.strip()
        if code.startswith('M'):
            return 'modified'
        elif code.startswith('A'):
            return 'added'
        elif code.startswith('D'):
            return 'deleted'
        elif code.startswith('R'):
            return 'renamed'
        elif code.startswith('C'):
            return 'copied'
        elif code.startswith('U'):
            return 'unmerged'
        else:
            return 'unknown'
    
    def _parse_diff_status(self, code: str) -> str:
        """解析diff狀態代碼"""
        if code == 'M':
            return 'modified'
        elif code == 'A':
            return 'added'
        elif code == 'D':
            return 'deleted'
        elif code.startswith('R'):
            return 'renamed'
        elif code.startswith('C'):
            return 'copied'
        else:
            return 'unknown'
    
    def _get_recent_commits(self, limit: int = 10) -> List[GitCommitInfo]:
        """獲取最近的提交"""
        commits = []
        commit_output = self._run_git_command(f"git log -{limit} --format=%H|%an|%ai|%s --numstat")
        
        current_commit = None
        files_changed = insertions = deletions = 0
        
        for line in commit_output.split('\n'):
            if not line.strip():
                continue
                
            if '|' in line and len(line.split('|')) == 4:
                # 這是提交信息行
                if current_commit:
                    # 保存前一個提交
                    commits.append(GitCommitInfo(
                        hash=current_commit['hash'],
                        author=current_commit['author'],
                        date=current_commit['date'],
                        message=current_commit['message'],
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions
                    ))
                
                # 開始新的提交
                parts = line.split('|')
                current_commit = {
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'message': parts[3]
                }
                files_changed = insertions = deletions = 0
                
            else:
                # 這是文件統計行
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        add = int(parts[0]) if parts[0] != '-' else 0
                        delete = int(parts[1]) if parts[1] != '-' else 0
                        insertions += add
                        deletions += delete
                        files_changed += 1
                    except ValueError:
                        pass
        
        # 處理最後一個提交
        if current_commit:
            commits.append(GitCommitInfo(
                hash=current_commit['hash'],
                author=current_commit['author'],
                date=current_commit['date'],
                message=current_commit['message'],
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions
            ))
        
        return commits
    
    def _get_remotes_info(self) -> List[GitRemoteInfo]:
        """獲取遠程倉庫信息"""
        remotes = []
        remote_output = self._run_git_command("git remote -v")
        
        remote_dict = {}
        for line in remote_output.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0]
                url = parts[1]
                type_info = parts[2].strip('()')
                
                if name not in remote_dict:
                    remote_dict[name] = {'name': name}
                
                if type_info == 'fetch':
                    remote_dict[name]['fetch_url'] = url
                elif type_info == 'push':
                    remote_dict[name]['push_url'] = url
                
                remote_dict[name]['url'] = url  # 通用URL
        
        for remote_info in remote_dict.values():
            remotes.append(GitRemoteInfo(
                name=remote_info['name'],
                url=remote_info.get('url', ''),
                fetch_url=remote_info.get('fetch_url', ''),
                push_url=remote_info.get('push_url', ''),
                last_fetch=None,  # 需要額外的邏輯來獲取
                last_push=None
            ))
        
        return remotes
    
    def _get_stash_count(self) -> int:
        """獲取stash數量"""
        stash_output = self._run_git_command("git stash list")
        return len([line for line in stash_output.split('\n') if line.strip()])
    
    def _get_conflicts(self) -> List[str]:
        """獲取衝突文件"""
        conflicts = []
        status_output = self._run_git_command("git status --porcelain")
        
        for line in status_output.split('\n'):
            if line.startswith('UU') or line.startswith('AA') or line.startswith('DD'):
                conflicts.append(line[3:])
        
        return conflicts
    
    def _get_submodules(self) -> List[str]:
        """獲取子模組"""
        submodules = []
        submodule_output = self._run_git_command("git submodule status")
        
        for line in submodule_output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    submodules.append(parts[1])
        
        return submodules
    
    def _get_total_commits(self) -> int:
        """獲取總提交數"""
        count_output = self._run_git_command("git rev-list --count HEAD")
        try:
            return int(count_output) if count_output else 0
        except ValueError:
            return 0
    
    def _get_repo_size(self) -> float:
        """獲取倉庫大小（MB）"""
        try:
            git_dir = os.path.join(os.getcwd(), '.git')
            total_size = 0
            
            for dirpath, dirnames, filenames in os.walk(git_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            return total_size / (1024 * 1024)  # 轉換為MB
        except Exception:
            return 0.0
    
    def generate_recommendations(self, repo_path: str) -> List[str]:
        """生成Git操作建議"""
        if repo_path not in self.monitored_repos:
            return ["請先掃描倉庫狀態"]
        
        status = self.monitored_repos[repo_path]
        recommendations = []
        
        # 檢查未提交文件
        total_uncommitted = len(status.modified_files) + len(status.untracked_files)
        if total_uncommitted > 0:
            recommendations.append(f"🔴 發現 {total_uncommitted} 個未提交文件，建議立即提交")
        
        # 檢查暫存文件
        if status.staged_files:
            recommendations.append(f"🟡 有 {len(status.staged_files)} 個文件已暫存，可以提交")
        
        # 檢查分支同步
        if status.current_branch.commits_behind > 0:
            recommendations.append(f"🔵 當前分支落後 {status.current_branch.commits_behind} 個提交，建議拉取最新代碼")
        
        if status.current_branch.commits_ahead > 0:
            recommendations.append(f"🟢 當前分支領先 {status.current_branch.commits_ahead} 個提交，建議推送到遠程")
        
        # 檢查衝突
        if status.conflicts:
            recommendations.append(f"⚠️ 發現 {len(status.conflicts)} 個衝突文件，需要解決衝突")
        
        # 檢查stash
        if status.stash_count > 0:
            recommendations.append(f"📦 有 {status.stash_count} 個stash，考慮清理或應用")
        
        # 檢查倉庫大小
        if status.repo_size_mb > 100:
            recommendations.append(f"💾 倉庫大小 {status.repo_size_mb:.1f}MB，考慮清理大文件")
        
        if not recommendations:
            recommendations.append("✅ 倉庫狀態良好，無需特殊操作")
        
        return recommendations
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """獲取監控總結"""
        total_repos = len(self.monitored_repos)
        total_uncommitted = sum(
            len(status.modified_files) + len(status.untracked_files) 
            for status in self.monitored_repos.values()
        )
        total_conflicts = sum(
            len(status.conflicts) 
            for status in self.monitored_repos.values()
        )
        
        return {
            "total_repositories": total_repos,
            "total_uncommitted_files": total_uncommitted,
            "total_conflicts": total_conflicts,
            "repositories": {
                path: {
                    "name": status.repo_name,
                    "uncommitted_files": len(status.modified_files) + len(status.untracked_files),
                    "staged_files": len(status.staged_files),
                    "conflicts": len(status.conflicts),
                    "current_branch": status.current_branch.name,
                    "last_scan": status.last_scan_time
                }
                for path, status in self.monitored_repos.items()
            }
        }

if __name__ == "__main__":
    # 測試Git監控引擎
    print("🔍 PowerAutomation Git監控引擎測試")
    print("=" * 50)
    
    monitor = GitMonitorEngine()
    
    # 測試掃描倉庫
    test_repos = [
        "/home/ubuntu/Powerauto.ai",
        "/home/ubuntu/powerautomation_v0.53_unified"
    ]
    
    for repo_path in test_repos:
        if os.path.exists(repo_path):
            print(f"\n📊 掃描倉庫: {repo_path}")
            try:
                status = monitor.scan_repository_detailed(repo_path)
                print(f"✅ 掃描完成: {status.repo_name}")
                print(f"   當前分支: {status.current_branch.name}")
                print(f"   修改文件: {len(status.modified_files)}")
                print(f"   未跟蹤文件: {len(status.untracked_files)}")
                print(f"   暫存文件: {len(status.staged_files)}")
                print(f"   總提交數: {status.total_commits}")
                print(f"   倉庫大小: {status.repo_size_mb:.1f}MB")
                
                # 顯示建議
                recommendations = monitor.generate_recommendations(repo_path)
                print(f"\n💡 操作建議:")
                for rec in recommendations:
                    print(f"   {rec}")
                    
            except Exception as e:
                print(f"❌ 掃描失敗: {e}")
    
    # 顯示總結
    print(f"\n📈 監控總結:")
    summary = monitor.get_monitoring_summary()
    print(f"總倉庫數: {summary['total_repositories']}")
    print(f"總未提交文件: {summary['total_uncommitted_files']}")
    print(f"總衝突文件: {summary['total_conflicts']}")

