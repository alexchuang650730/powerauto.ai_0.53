#!/usr/bin/env python3
"""
PowerAutomation 消費級架構實現

提供輕量級插件架構，包括瀏覽器插件、桌面應用等
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
from pathlib import Path

# 添加共享核心路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_core'))

from shared_core import get_shared_core, initialize_shared_core
from shared_core.config.unified_config import get_config_manager

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """用戶配置文件"""
    user_id: str
    name: str
    email: str
    preferences: Dict[str, Any]
    sync_enabled: bool = True
    offline_mode: bool = False
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class AutomationTask:
    """自動化任務"""
    task_id: str
    name: str
    description: str
    trigger_type: str  # manual, schedule, event
    actions: List[Dict[str, Any]]
    is_active: bool = True
    created_at: str = ""
    last_run: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class LocalDatabase:
    """本地SQLite數據庫"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化數據庫表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 用戶配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    preferences TEXT,
                    sync_enabled BOOLEAN DEFAULT 1,
                    offline_mode BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # 自動化任務表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automation_tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    trigger_type TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_run TEXT
                )
            """)
            
            # 執行歷史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    executed_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES automation_tasks (task_id)
                )
            """)
            
            conn.commit()
    
    def save_user_profile(self, profile: UserProfile):
        """保存用戶配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, name, email, preferences, sync_enabled, offline_mode, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.user_id,
                profile.name,
                profile.email,
                json.dumps(profile.preferences),
                profile.sync_enabled,
                profile.offline_mode,
                profile.created_at
            ))
            conn.commit()
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """獲取用戶配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, name, email, preferences, sync_enabled, offline_mode, created_at
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return UserProfile(
                    user_id=row[0],
                    name=row[1],
                    email=row[2],
                    preferences=json.loads(row[3]) if row[3] else {},
                    sync_enabled=bool(row[4]),
                    offline_mode=bool(row[5]),
                    created_at=row[6]
                )
        return None
    
    def save_automation_task(self, task: AutomationTask):
        """保存自動化任務"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO automation_tasks 
                (task_id, name, description, trigger_type, actions, is_active, created_at, last_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.name,
                task.description,
                task.trigger_type,
                json.dumps(task.actions),
                task.is_active,
                task.created_at,
                task.last_run
            ))
            conn.commit()
    
    def get_automation_tasks(self, active_only: bool = True) -> List[AutomationTask]:
        """獲取自動化任務列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM automation_tasks"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query)
            tasks = []
            
            for row in cursor.fetchall():
                task = AutomationTask(
                    task_id=row[0],
                    name=row[1],
                    description=row[2],
                    trigger_type=row[3],
                    actions=json.loads(row[4]),
                    is_active=bool(row[5]),
                    created_at=row[6],
                    last_run=row[7]
                )
                tasks.append(task)
            
            return tasks

class BrowserExtensionManager:
    """瀏覽器插件管理器"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成瀏覽器插件文件
        self._generate_extension_files()
    
    def _generate_extension_files(self):
        """生成瀏覽器插件文件"""
        # manifest.json
        manifest = {
            "manifest_version": 3,
            "name": "PowerAutomation Consumer",
            "version": "0.5.3",
            "description": "個人自動化助手",
            "permissions": [
                "activeTab",
                "storage",
                "scripting"
            ],
            "action": {
                "default_popup": "popup.html",
                "default_title": "PowerAutomation"
            },
            "content_scripts": [
                {
                    "matches": ["<all_urls>"],
                    "js": ["content_script.js"]
                }
            ],
            "background": {
                "service_worker": "background.js"
            }
        }
        
        with open(self.data_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # popup.html
        popup_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { width: 300px; padding: 10px; font-family: Arial, sans-serif; }
        .header { text-align: center; margin-bottom: 15px; }
        .task-list { max-height: 200px; overflow-y: auto; }
        .task-item { padding: 8px; border: 1px solid #ddd; margin: 5px 0; border-radius: 4px; }
        .task-item.active { background-color: #e8f5e8; }
        .btn { padding: 5px 10px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; }
        .btn-primary { background-color: #007bff; color: white; }
        .btn-success { background-color: #28a745; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h3>PowerAutomation</h3>
        <p>個人自動化助手</p>
    </div>
    
    <div class="task-list" id="taskList">
        <!-- 任務列表將通過JavaScript動態生成 -->
    </div>
    
    <div style="text-align: center; margin-top: 15px;">
        <button class="btn btn-primary" id="newTaskBtn">新建任務</button>
        <button class="btn btn-success" id="syncBtn">同步數據</button>
    </div>
    
    <script src="popup.js"></script>
</body>
</html>"""
        
        with open(self.data_dir / "popup.html", 'w', encoding='utf-8') as f:
            f.write(popup_html)
        
        # popup.js
        popup_js = """
// 瀏覽器插件彈窗腳本
document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
    
    document.getElementById('newTaskBtn').addEventListener('click', createNewTask);
    document.getElementById('syncBtn').addEventListener('click', syncData);
});

function loadTasks() {
    // 從本地存儲加載任務
    chrome.storage.local.get(['automationTasks'], function(result) {
        const tasks = result.automationTasks || [];
        displayTasks(tasks);
    });
}

function displayTasks(tasks) {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';
    
    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="text-align: center; color: #666;">暫無自動化任務</p>';
        return;
    }
    
    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item' + (task.is_active ? ' active' : '');
        taskItem.innerHTML = `
            <strong>${task.name}</strong>
            <p style="font-size: 12px; color: #666; margin: 5px 0;">${task.description}</p>
            <button class="btn btn-success" onclick="executeTask('${task.task_id}')">執行</button>
        `;
        taskList.appendChild(taskItem);
    });
}

function createNewTask() {
    // 打開新任務創建頁面
    chrome.tabs.create({
        url: chrome.runtime.getURL('task_editor.html')
    });
}

function syncData() {
    // 與雲端同步數據
    console.log('開始同步數據...');
    // 實際實現需要調用後端API
}

function executeTask(taskId) {
    // 執行指定任務
    console.log('執行任務:', taskId);
    // 實際實現需要調用內容腳本
}
"""
        
        with open(self.data_dir / "popup.js", 'w', encoding='utf-8') as f:
            f.write(popup_js)
        
        # content_script.js
        content_script_js = """
// 瀏覽器插件內容腳本
(function() {
    'use strict';
    
    console.log('PowerAutomation 內容腳本已加載');
    
    // 監聽來自插件的消息
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'executeTask') {
            executeAutomationTask(request.task);
        }
    });
    
    function executeAutomationTask(task) {
        console.log('執行自動化任務:', task);
        
        // 根據任務類型執行不同操作
        task.actions.forEach(action => {
            switch(action.type) {
                case 'click':
                    clickElement(action.selector);
                    break;
                case 'input':
                    inputText(action.selector, action.value);
                    break;
                case 'scroll':
                    scrollPage(action.direction, action.amount);
                    break;
                default:
                    console.log('未知操作類型:', action.type);
            }
        });
    }
    
    function clickElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.click();
            console.log('點擊元素:', selector);
        } else {
            console.log('未找到元素:', selector);
        }
    }
    
    function inputText(selector, text) {
        const element = document.querySelector(selector);
        if (element) {
            element.value = text;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('輸入文本:', selector, text);
        } else {
            console.log('未找到輸入框:', selector);
        }
    }
    
    function scrollPage(direction, amount) {
        const scrollAmount = amount || 300;
        if (direction === 'down') {
            window.scrollBy(0, scrollAmount);
        } else if (direction === 'up') {
            window.scrollBy(0, -scrollAmount);
        }
        console.log('滾動頁面:', direction, scrollAmount);
    }
})();
"""
        
        with open(self.data_dir / "content_script.js", 'w', encoding='utf-8') as f:
            f.write(content_script_js)
        
        # background.js
        background_js = """
// 瀏覽器插件後台腳本
chrome.runtime.onInstalled.addListener(function() {
    console.log('PowerAutomation 插件已安裝');
    
    // 初始化默認設置
    chrome.storage.local.set({
        'userProfile': {
            'user_id': 'consumer_user_' + Date.now(),
            'name': '用戶',
            'preferences': {
                'auto_sync': true,
                'notifications': true
            }
        }
    });
});

// 監聽標籤頁更新
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'complete' && tab.url) {
        // 檢查是否有適用的自動化任務
        checkAutomationTasks(tab.url);
    }
});

function checkAutomationTasks(url) {
    chrome.storage.local.get(['automationTasks'], function(result) {
        const tasks = result.automationTasks || [];
        
        // 查找適用於當前URL的任務
        const applicableTasks = tasks.filter(task => 
            task.trigger_type === 'url_match' && 
            task.is_active &&
            url.includes(task.url_pattern)
        );
        
        if (applicableTasks.length > 0) {
            console.log('發現適用任務:', applicableTasks.length);
            // 可以選擇自動執行或提示用戶
        }
    });
}
"""
        
        with open(self.data_dir / "background.js", 'w', encoding='utf-8') as f:
            f.write(background_js)

class ConsumerApplication:
    """消費級應用主類"""
    
    def __init__(self):
        # 獲取消費級配置
        config_manager = get_config_manager()
        self.config = config_manager.get_all_config("consumer")
        
        # 初始化組件
        self.database = LocalDatabase(
            os.path.join(self.config["base"].data_dir, "consumer.db")
        )
        self.extension_manager = BrowserExtensionManager(
            os.path.join(self.config["base"].data_dir, "browser_extension")
        )
        
        # 初始化共享核心
        self.shared_core = None
    
    async def start(self):
        """啟動消費級應用"""
        try:
            # 初始化共享核心
            self.shared_core = initialize_shared_core("consumer")
            await self.shared_core.start_all_components()
            
            # 創建示例用戶配置
            self._create_sample_data()
            
            logger.info("消費級應用啟動成功")
            
        except Exception as e:
            logger.error(f"消費級應用啟動失敗: {e}")
            raise
    
    def _create_sample_data(self):
        """創建示例數據"""
        # 創建示例用戶配置
        profile = UserProfile(
            user_id="consumer_user_001",
            name="個人用戶",
            email="user@example.com",
            preferences={
                "auto_sync": True,
                "notifications": True,
                "theme": "light"
            }
        )
        self.database.save_user_profile(profile)
        
        # 創建示例自動化任務
        task = AutomationTask(
            task_id="task_001",
            name="自動填寫表單",
            description="在特定網站自動填寫常用信息",
            trigger_type="manual",
            actions=[
                {"type": "input", "selector": "#name", "value": "個人用戶"},
                {"type": "input", "selector": "#email", "value": "user@example.com"},
                {"type": "click", "selector": "#submit"}
            ]
        )
        self.database.save_automation_task(task)
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """獲取用戶配置"""
        return self.database.get_user_profile(user_id)
    
    def get_automation_tasks(self) -> List[AutomationTask]:
        """獲取自動化任務"""
        return self.database.get_automation_tasks()
    
    def create_automation_task(self, task_data: Dict[str, Any]) -> str:
        """創建自動化任務"""
        task = AutomationTask(
            task_id=f"task_{datetime.now().timestamp()}",
            name=task_data["name"],
            description=task_data.get("description", ""),
            trigger_type=task_data["trigger_type"],
            actions=task_data["actions"]
        )
        
        self.database.save_automation_task(task)
        return task.task_id
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """執行自動化任務"""
        tasks = self.database.get_automation_tasks(active_only=False)
        task = next((t for t in tasks if t.task_id == task_id), None)
        
        if not task:
            return {"status": "error", "message": "任務不存在"}
        
        if not task.is_active:
            return {"status": "error", "message": "任務已禁用"}
        
        # 簡化的任務執行邏輯
        try:
            # 更新最後執行時間
            task.last_run = datetime.now().isoformat()
            self.database.save_automation_task(task)
            
            return {
                "status": "success",
                "message": "任務執行成功",
                "task_id": task_id,
                "executed_at": task.last_run
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"任務執行失敗: {str(e)}",
                "task_id": task_id
            }
    
    async def stop(self):
        """停止消費級應用"""
        if self.shared_core:
            await self.shared_core.stop_all_components()
        logger.info("消費級應用已停止")

async def main():
    """主函數"""
    print("🚀 PowerAutomation 消費級架構啟動")
    
    try:
        app = ConsumerApplication()
        await app.start()
        
        # 演示功能
        print("\n📋 用戶配置:")
        profile = app.get_user_profile("consumer_user_001")
        if profile:
            print(f"   用戶: {profile.name} ({profile.email})")
            print(f"   同步: {'啟用' if profile.sync_enabled else '禁用'}")
        
        print("\n📋 自動化任務:")
        tasks = app.get_automation_tasks()
        for task in tasks:
            print(f"   {task.name}: {task.description}")
            
            # 執行任務演示
            result = await app.execute_task(task.task_id)
            print(f"   執行結果: {result['status']}")
        
        print("\n✅ 消費級架構演示完成")
        
    except KeyboardInterrupt:
        print("\n⏹️ 應用停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())

