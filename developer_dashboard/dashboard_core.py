#!/usr/bin/env python3
"""
PowerAutomation 開發者Dashboard系統架構設計

這個系統的核心目標：永遠不再丟失代碼！

設計理念：
1. 實時監控 - 每分鐘掃描所有Git倉庫狀態
2. 主動提醒 - 自動發現風險並及時通知
3. 一鍵操作 - 簡化複雜的Git操作
4. 團隊協作 - 統一的代碼管理流程
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import logging

@dataclass
class GitRepoStatus:
    """Git倉庫狀態數據結構"""
    path: str
    name: str
    branch: str
    uncommitted_files: int
    untracked_files: int
    unpushed_commits: int
    last_commit_time: str
    last_commit_message: str
    remote_url: str
    status: str  # 'clean', 'dirty', 'behind', 'ahead', 'diverged'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    
@dataclass
class CodeHealthMetrics:
    """代碼健康度指標"""
    repo_path: str
    total_files: int
    python_files: int
    test_coverage: float
    code_quality_score: float
    security_issues: int
    performance_issues: int
    documentation_coverage: float
    last_updated: str

@dataclass
class DashboardConfig:
    """Dashboard配置"""
    scan_interval: int = 300  # 5分鐘掃描一次
    monitored_paths: List[str] = None
    notification_enabled: bool = True
    auto_backup_enabled: bool = True
    risk_thresholds: Dict[str, int] = None
    
    def __post_init__(self):
        if self.monitored_paths is None:
            self.monitored_paths = [
                "/home/ubuntu/Powerauto.ai",
                "/home/ubuntu/powerautomation_v0.53_unified",
                "/home/ubuntu/upload"
            ]
        if self.risk_thresholds is None:
            self.risk_thresholds = {
                "uncommitted_files_medium": 5,
                "uncommitted_files_high": 15,
                "uncommitted_files_critical": 30,
                "hours_without_commit_medium": 2,
                "hours_without_commit_high": 6,
                "hours_without_commit_critical": 24
            }

class DashboardCore:
    """Dashboard核心控制器"""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.logger = self._setup_logging()
        self.repo_statuses: Dict[str, GitRepoStatus] = {}
        self.health_metrics: Dict[str, CodeHealthMetrics] = {}
        self.is_running = False
        self.monitor_thread = None
        
    def _setup_logging(self) -> logging.Logger:
        """設置日誌系統"""
        logger = logging.getLogger("PowerAutomation.Dashboard")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def start_monitoring(self):
        """開始監控"""
        if self.is_running:
            self.logger.warning("監控已經在運行中")
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Dashboard監控系統已啟動")
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Dashboard監控系統已停止")
    
    def _monitor_loop(self):
        """監控主循環"""
        while self.is_running:
            try:
                self.scan_all_repositories()
                self.check_risks()
                time.sleep(self.config.scan_interval)
            except Exception as e:
                self.logger.error(f"監控循環出錯: {e}")
                time.sleep(60)  # 出錯後等待1分鐘再重試
    
    def scan_all_repositories(self) -> Dict[str, GitRepoStatus]:
        """掃描所有Git倉庫"""
        self.logger.info("開始掃描所有Git倉庫...")
        
        for path in self.config.monitored_paths:
            if os.path.exists(path) and self._is_git_repo(path):
                try:
                    status = self._get_repo_status(path)
                    self.repo_statuses[path] = status
                    self.logger.debug(f"掃描完成: {path} - {status.status}")
                except Exception as e:
                    self.logger.error(f"掃描倉庫失敗 {path}: {e}")
        
        self.logger.info(f"掃描完成，共監控 {len(self.repo_statuses)} 個倉庫")
        return self.repo_statuses
    
    def _is_git_repo(self, path: str) -> bool:
        """檢查是否為Git倉庫"""
        return os.path.exists(os.path.join(path, '.git'))
    
    def _get_repo_status(self, repo_path: str) -> GitRepoStatus:
        """獲取單個倉庫的詳細狀態"""
        os.chdir(repo_path)
        
        # 獲取基本信息
        name = os.path.basename(repo_path)
        branch = self._run_git_command("git branch --show-current").strip()
        
        # 獲取未提交文件數量
        status_output = self._run_git_command("git status --porcelain")
        uncommitted_files = len([line for line in status_output.split('\n') if line.strip() and not line.startswith('??')])
        untracked_files = len([line for line in status_output.split('\n') if line.strip().startswith('??')])
        
        # 獲取未推送提交數量
        try:
            unpushed_output = self._run_git_command("git log @{u}..HEAD --oneline")
            unpushed_commits = len([line for line in unpushed_output.split('\n') if line.strip()])
        except:
            unpushed_commits = 0
        
        # 獲取最後提交信息
        try:
            last_commit_time = self._run_git_command("git log -1 --format=%ci").strip()
            last_commit_message = self._run_git_command("git log -1 --format=%s").strip()
        except:
            last_commit_time = "未知"
            last_commit_message = "無提交記錄"
        
        # 獲取遠程URL
        try:
            remote_url = self._run_git_command("git remote get-url origin").strip()
        except:
            remote_url = "無遠程倉庫"
        
        # 判斷狀態
        if uncommitted_files == 0 and untracked_files == 0 and unpushed_commits == 0:
            status = "clean"
        elif uncommitted_files > 0 or untracked_files > 0:
            status = "dirty"
        elif unpushed_commits > 0:
            status = "ahead"
        else:
            status = "unknown"
        
        # 計算風險等級
        risk_level = self._calculate_risk_level(uncommitted_files, untracked_files, last_commit_time)
        
        return GitRepoStatus(
            path=repo_path,
            name=name,
            branch=branch,
            uncommitted_files=uncommitted_files,
            untracked_files=untracked_files,
            unpushed_commits=unpushed_commits,
            last_commit_time=last_commit_time,
            last_commit_message=last_commit_message,
            remote_url=remote_url,
            status=status,
            risk_level=risk_level
        )
    
    def _run_git_command(self, command: str) -> str:
        """執行Git命令"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise Exception(f"Git命令超時: {command}")
        except Exception as e:
            raise Exception(f"Git命令執行失敗: {command}, 錯誤: {e}")
    
    def _calculate_risk_level(self, uncommitted: int, untracked: int, last_commit_time: str) -> str:
        """計算風險等級"""
        total_files = uncommitted + untracked
        
        # 計算距離上次提交的時間
        try:
            if last_commit_time != "未知":
                last_commit = datetime.fromisoformat(last_commit_time.replace(' +0800', ''))
                hours_since_commit = (datetime.now() - last_commit).total_seconds() / 3600
            else:
                hours_since_commit = 999  # 很大的數字表示很久沒提交
        except:
            hours_since_commit = 999
        
        # 根據閾值判斷風險等級
        thresholds = self.config.risk_thresholds
        
        if (total_files >= thresholds["uncommitted_files_critical"] or 
            hours_since_commit >= thresholds["hours_without_commit_critical"]):
            return "critical"
        elif (total_files >= thresholds["uncommitted_files_high"] or 
              hours_since_commit >= thresholds["hours_without_commit_high"]):
            return "high"
        elif (total_files >= thresholds["uncommitted_files_medium"] or 
              hours_since_commit >= thresholds["hours_without_commit_medium"]):
            return "medium"
        else:
            return "low"
    
    def check_risks(self):
        """檢查風險並發送通知"""
        high_risk_repos = []
        critical_risk_repos = []
        
        for repo_path, status in self.repo_statuses.items():
            if status.risk_level == "critical":
                critical_risk_repos.append(status)
            elif status.risk_level == "high":
                high_risk_repos.append(status)
        
        if critical_risk_repos:
            self._send_critical_alert(critical_risk_repos)
        elif high_risk_repos:
            self._send_high_risk_alert(high_risk_repos)
    
    def _send_critical_alert(self, repos: List[GitRepoStatus]):
        """發送緊急警報"""
        message = "🚨 緊急警報：發現代碼丟失風險！\n\n"
        for repo in repos:
            message += f"📁 {repo.name}: {repo.uncommitted_files + repo.untracked_files} 個未保存文件\n"
        
        self.logger.critical(message)
        # 這裡可以添加桌面通知、郵件通知等
    
    def _send_high_risk_alert(self, repos: List[GitRepoStatus]):
        """發送高風險警報"""
        message = "⚠️ 高風險警告：建議立即提交代碼\n\n"
        for repo in repos:
            message += f"📁 {repo.name}: {repo.uncommitted_files + repo.untracked_files} 個未保存文件\n"
        
        self.logger.warning(message)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """獲取Dashboard數據"""
        return {
            "timestamp": datetime.now().isoformat(),
            "repositories": {path: asdict(status) for path, status in self.repo_statuses.items()},
            "summary": self._get_summary(),
            "alerts": self._get_current_alerts()
        }
    
    def _get_summary(self) -> Dict[str, Any]:
        """獲取總結信息"""
        total_repos = len(self.repo_statuses)
        clean_repos = len([s for s in self.repo_statuses.values() if s.status == "clean"])
        dirty_repos = len([s for s in self.repo_statuses.values() if s.status == "dirty"])
        total_uncommitted = sum(s.uncommitted_files + s.untracked_files for s in self.repo_statuses.values())
        
        risk_counts = {
            "low": len([s for s in self.repo_statuses.values() if s.risk_level == "low"]),
            "medium": len([s for s in self.repo_statuses.values() if s.risk_level == "medium"]),
            "high": len([s for s in self.repo_statuses.values() if s.risk_level == "high"]),
            "critical": len([s for s in self.repo_statuses.values() if s.risk_level == "critical"])
        }
        
        return {
            "total_repositories": total_repos,
            "clean_repositories": clean_repos,
            "dirty_repositories": dirty_repos,
            "total_uncommitted_files": total_uncommitted,
            "risk_distribution": risk_counts,
            "overall_health": "critical" if risk_counts["critical"] > 0 else 
                            "high" if risk_counts["high"] > 0 else
                            "medium" if risk_counts["medium"] > 0 else "good"
        }
    
    def _get_current_alerts(self) -> List[Dict[str, Any]]:
        """獲取當前警報"""
        alerts = []
        
        for repo_path, status in self.repo_statuses.items():
            if status.risk_level in ["high", "critical"]:
                alerts.append({
                    "type": status.risk_level,
                    "repository": status.name,
                    "message": f"{status.uncommitted_files + status.untracked_files} 個未保存文件",
                    "action_required": "立即提交代碼",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts

if __name__ == "__main__":
    # 測試Dashboard核心功能
    print("🚀 PowerAutomation 開發者Dashboard系統")
    print("=" * 50)
    
    dashboard = DashboardCore()
    
    # 執行一次掃描
    print("📊 掃描Git倉庫狀態...")
    dashboard.scan_all_repositories()
    
    # 顯示結果
    data = dashboard.get_dashboard_data()
    print(f"\n📈 掃描結果:")
    print(f"總倉庫數: {data['summary']['total_repositories']}")
    print(f"乾淨倉庫: {data['summary']['clean_repositories']}")
    print(f"有修改倉庫: {data['summary']['dirty_repositories']}")
    print(f"未提交文件總數: {data['summary']['total_uncommitted_files']}")
    print(f"整體健康度: {data['summary']['overall_health']}")
    
    # 顯示風險分布
    print(f"\n⚠️ 風險分布:")
    for level, count in data['summary']['risk_distribution'].items():
        if count > 0:
            print(f"{level.upper()}: {count} 個倉庫")
    
    # 顯示警報
    if data['alerts']:
        print(f"\n🚨 當前警報:")
        for alert in data['alerts']:
            print(f"[{alert['type'].upper()}] {alert['repository']}: {alert['message']}")
    else:
        print(f"\n✅ 無警報，所有代碼都很安全！")

