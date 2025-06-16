# MCPCoordinator交互数据管理架构

## 🎯 概述

本文档详细说明MCPCoordinator端的InteractionLogManager架构设计，包括HTTP API接口、异步队列处理、数据存储和分析等核心组件。

## 🏗️ 整体架构

```
HTTP API接口 → 异步队列 → InteractionLogManager → 数据存储 → 分析引擎
     ↓              ↓              ↓              ↓           ↓
  请求验证      快速响应      数据处理      持久化存储    智能分析
```

### **核心组件**

1. **InteractionAPI** - HTTP接口层
2. **AsyncQueue** - 异步队列处理
3. **InteractionLogManager** - 核心数据管理
4. **DataStorage** - 数据存储引擎
5. **AnalysisEngine** - 数据分析引擎

## 🔧 详细实现

### **1. InteractionAPI - HTTP接口层**

```python
# interaction_api.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import asyncio
import time
import logging
from datetime import datetime

# 数据模型
class InteractionStartData(BaseModel):
    action: str = Field(..., regex="^interaction_start$")
    interaction_id: str = Field(..., min_length=1)
    mcp_id: str = Field(..., min_length=1)
    timestamp: float = Field(..., gt=0)
    request_data: Dict = Field(default_factory=dict)

class InteractionProgressData(BaseModel):
    action: str = Field(..., regex="^interaction_progress$")
    interaction_id: str = Field(..., min_length=1)
    mcp_id: str = Field(..., min_length=1)
    timestamp: float = Field(..., gt=0)
    progress_data: Dict = Field(default_factory=dict)

class InteractionCompleteData(BaseModel):
    action: str = Field(..., regex="^interaction_complete$")
    interaction_id: str = Field(..., min_length=1)
    mcp_id: str = Field(..., min_length=1)
    timestamp: float = Field(..., gt=0)
    result_data: Dict = Field(default_factory=dict)

class InteractionErrorData(BaseModel):
    action: str = Field(..., regex="^interaction_error$")
    interaction_id: str = Field(..., min_length=1)
    mcp_id: str = Field(..., min_length=1)
    timestamp: float = Field(..., gt=0)
    error_data: Dict = Field(default_factory=dict)

class InteractionAPI:
    """交互数据API接口"""
    
    def __init__(self, interaction_log_manager, api_key_validator):
        self.log_manager = interaction_log_manager
        self.api_key_validator = api_key_validator
        self.logger = logging.getLogger("InteractionAPI")
        
        # 异步队列 (内存队列，生产环境可考虑Redis)
        self.interaction_queue = asyncio.Queue(maxsize=10000)
        
        # 启动后台处理任务
        self.processor_task = None
        
        # 统计信息
        self.stats = {
            "requests_received": 0,
            "requests_processed": 0,
            "requests_failed": 0,
            "queue_size": 0
        }
    
    async def start(self):
        """启动API服务"""
        self.processor_task = asyncio.create_task(self._process_queue())
        self.logger.info("InteractionAPI started")
    
    async def stop(self):
        """停止API服务"""
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("InteractionAPI stopped")
    
    async def validate_api_key(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """验证API密钥"""
        if not await self.api_key_validator.validate(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return credentials.credentials
    
    async def receive_interaction(self, 
                                data: Dict,
                                background_tasks: BackgroundTasks,
                                api_key: str = Depends(validate_api_key)):
        """接收交互数据的统一入口"""
        
        try:
            # 快速验证和入队
            self.stats["requests_received"] += 1
            
            # 添加接收时间戳
            data["received_at"] = time.time()
            data["api_key"] = api_key
            
            # 非阻塞入队
            try:
                self.interaction_queue.put_nowait(data)
                self.stats["queue_size"] = self.interaction_queue.qsize()
                
                return {
                    "status": "accepted",
                    "interaction_id": data.get("interaction_id"),
                    "queue_position": self.interaction_queue.qsize()
                }
                
            except asyncio.QueueFull:
                self.stats["requests_failed"] += 1
                self.logger.error("Interaction queue is full")
                raise HTTPException(status_code=503, detail="Service temporarily unavailable")
                
        except Exception as e:
            self.stats["requests_failed"] += 1
            self.logger.error(f"Error receiving interaction: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _process_queue(self):
        """后台任务：处理队列中的交互数据"""
        
        while True:
            try:
                # 批量处理以提高效率
                batch = []
                batch_size = 100
                timeout = 1.0  # 1秒超时
                
                # 收集一批数据
                start_time = time.time()
                while len(batch) < batch_size and (time.time() - start_time) < timeout:
                    try:
                        data = await asyncio.wait_for(self.interaction_queue.get(), timeout=0.1)
                        batch.append(data)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # 批量处理
                    await self._process_batch(batch)
                    self.stats["requests_processed"] += len(batch)
                    self.stats["queue_size"] = self.interaction_queue.qsize()
                
                # 短暂休息
                await asyncio.sleep(0.01)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing queue: {e}")
                await asyncio.sleep(1.0)  # 错误时等待更长时间
    
    async def _process_batch(self, batch: List[Dict]):
        """批量处理交互数据"""
        
        for data in batch:
            try:
                action = data.get("action")
                
                if action == "interaction_start":
                    await self.log_manager.handle_interaction_start(data)
                elif action == "interaction_progress":
                    await self.log_manager.handle_interaction_progress(data)
                elif action == "interaction_complete":
                    await self.log_manager.handle_interaction_complete(data)
                elif action == "interaction_error":
                    await self.log_manager.handle_interaction_error(data)
                else:
                    self.logger.warning(f"Unknown action: {action}")
                    
            except Exception as e:
                self.logger.error(f"Error processing interaction {data.get('interaction_id')}: {e}")
    
    async def get_stats(self, api_key: str = Depends(validate_api_key)):
        """获取API统计信息"""
        return {
            "stats": self.stats,
            "timestamp": time.time(),
            "queue_size": self.interaction_queue.qsize()
        }
    
    async def get_health(self):
        """健康检查"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "queue_size": self.interaction_queue.qsize(),
            "processor_running": self.processor_task and not self.processor_task.done()
        }

# FastAPI应用设置
def create_interaction_app(interaction_log_manager, api_key_validator) -> FastAPI:
    """创建交互数据API应用"""
    
    app = FastAPI(
        title="MCPCoordinator Interaction API",
        description="接收和处理MCP交互数据",
        version="2.0.0"
    )
    
    # 创建API实例
    api = InteractionAPI(interaction_log_manager, api_key_validator)
    
    # 注册路由
    @app.post("/api/v2/interactions")
    async def receive_interaction(
        data: Dict,
        background_tasks: BackgroundTasks,
        api_key: str = Depends(api.validate_api_key)
    ):
        return await api.receive_interaction(data, background_tasks, api_key)
    
    @app.get("/api/v2/interactions/stats")
    async def get_stats(api_key: str = Depends(api.validate_api_key)):
        return await api.get_stats(api_key)
    
    @app.get("/api/v2/health")
    async def get_health():
        return await api.get_health()
    
    # 启动和关闭事件
    @app.on_event("startup")
    async def startup_event():
        await api.start()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await api.stop()
    
    return app
```

### **2. InteractionLogManager - 核心数据管理**

```python
# interaction_log_manager.py
import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
import aiosqlite
from dataclasses import dataclass, asdict
from enum import Enum

class InteractionStatus(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class InteractionRecord:
    """交互记录数据结构"""
    interaction_id: str
    mcp_id: str
    status: InteractionStatus
    start_time: float
    end_time: Optional[float] = None
    request_data: Dict = None
    result_data: Dict = None
    error_data: Dict = None
    progress_updates: List[Dict] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.request_data is None:
            self.request_data = {}
        if self.result_data is None:
            self.result_data = {}
        if self.error_data is None:
            self.error_data = {}
        if self.progress_updates is None:
            self.progress_updates = []
        if self.metadata is None:
            self.metadata = {}

class InteractionLogManager:
    """交互日志管理器"""
    
    def __init__(self, 
                 database_path: str = "./data/interactions.db",
                 max_records: int = 1000000,
                 cleanup_interval: int = 3600):
        
        self.database_path = database_path
        self.max_records = max_records
        self.cleanup_interval = cleanup_interval
        
        # 内存缓存 (最近的交互记录)
        self.memory_cache: Dict[str, InteractionRecord] = {}
        self.cache_max_size = 10000
        
        # 统计信息
        self.stats = {
            "total_interactions": 0,
            "active_interactions": 0,
            "completed_interactions": 0,
            "failed_interactions": 0,
            "average_processing_time": 0.0
        }
        
        self.logger = logging.getLogger("InteractionLogManager")
        
        # 后台任务
        self.cleanup_task: Optional[asyncio.Task] = None
        self.stats_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动日志管理器"""
        # 初始化数据库
        await self._init_database()
        
        # 启动后台任务
        self.cleanup_task = asyncio.create_task(self._cleanup_old_records())
        self.stats_task = asyncio.create_task(self._update_stats())
        
        self.logger.info("InteractionLogManager started")
    
    async def stop(self):
        """停止日志管理器"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.stats_task:
            self.stats_task.cancel()
        
        # 等待任务完成
        for task in [self.cleanup_task, self.stats_task]:
            if task:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("InteractionLogManager stopped")
    
    async def _init_database(self):
        """初始化数据库"""
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id TEXT PRIMARY KEY,
                    mcp_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    request_data TEXT,
                    result_data TEXT,
                    error_data TEXT,
                    progress_updates TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            await db.execute("CREATE INDEX IF NOT EXISTS idx_mcp_id ON interactions(mcp_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_status ON interactions(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_start_time ON interactions(start_time)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON interactions(created_at)")
            
            await db.commit()
    
    async def handle_interaction_start(self, data: Dict):
        """处理交互开始事件"""
        
        interaction_id = data["interaction_id"]
        mcp_id = data["mcp_id"]
        
        # 创建交互记录
        record = InteractionRecord(
            interaction_id=interaction_id,
            mcp_id=mcp_id,
            status=InteractionStatus.STARTED,
            start_time=data["timestamp"],
            request_data=data.get("request_data", {}),
            metadata={
                "received_at": data.get("received_at"),
                "api_key_hash": hash(data.get("api_key", ""))
            }
        )
        
        # 存储到内存缓存
        self.memory_cache[interaction_id] = record
        self._trim_cache()
        
        # 异步存储到数据库
        await self._store_to_database(record)
        
        # 更新统计
        self.stats["total_interactions"] += 1
        self.stats["active_interactions"] += 1
        
        self.logger.debug(f"Started interaction: {interaction_id}")
    
    async def handle_interaction_progress(self, data: Dict):
        """处理交互进度事件"""
        
        interaction_id = data["interaction_id"]
        
        # 更新内存缓存
        if interaction_id in self.memory_cache:
            record = self.memory_cache[interaction_id]
            record.status = InteractionStatus.IN_PROGRESS
            record.progress_updates.append({
                "timestamp": data["timestamp"],
                "data": data.get("progress_data", {})
            })
            
            # 更新数据库
            await self._update_database_record(record)
            
            self.logger.debug(f"Updated progress for interaction: {interaction_id}")
        else:
            self.logger.warning(f"Progress update for unknown interaction: {interaction_id}")
    
    async def handle_interaction_complete(self, data: Dict):
        """处理交互完成事件"""
        
        interaction_id = data["interaction_id"]
        
        # 更新内存缓存
        if interaction_id in self.memory_cache:
            record = self.memory_cache[interaction_id]
            record.status = InteractionStatus.COMPLETED
            record.end_time = data["timestamp"]
            record.result_data = data.get("result_data", {})
            
            # 更新数据库
            await self._update_database_record(record)
            
            # 更新统计
            self.stats["active_interactions"] -= 1
            self.stats["completed_interactions"] += 1
            
            # 计算平均处理时间
            processing_time = record.end_time - record.start_time
            self._update_average_processing_time(processing_time)
            
            self.logger.debug(f"Completed interaction: {interaction_id}")
        else:
            self.logger.warning(f"Completion for unknown interaction: {interaction_id}")
    
    async def handle_interaction_error(self, data: Dict):
        """处理交互错误事件"""
        
        interaction_id = data["interaction_id"]
        
        # 更新内存缓存
        if interaction_id in self.memory_cache:
            record = self.memory_cache[interaction_id]
            record.status = InteractionStatus.FAILED
            record.end_time = data["timestamp"]
            record.error_data = data.get("error_data", {})
            
            # 更新数据库
            await self._update_database_record(record)
            
            # 更新统计
            self.stats["active_interactions"] -= 1
            self.stats["failed_interactions"] += 1
            
            self.logger.debug(f"Failed interaction: {interaction_id}")
        else:
            self.logger.warning(f"Error for unknown interaction: {interaction_id}")
    
    async def _store_to_database(self, record: InteractionRecord):
        """存储记录到数据库"""
        
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO interactions 
                (interaction_id, mcp_id, status, start_time, end_time, 
                 request_data, result_data, error_data, progress_updates, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.interaction_id,
                record.mcp_id,
                record.status.value,
                record.start_time,
                record.end_time,
                json.dumps(record.request_data),
                json.dumps(record.result_data),
                json.dumps(record.error_data),
                json.dumps(record.progress_updates),
                json.dumps(record.metadata)
            ))
            await db.commit()
    
    async def _update_database_record(self, record: InteractionRecord):
        """更新数据库记录"""
        
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("""
                UPDATE interactions 
                SET status = ?, end_time = ?, result_data = ?, error_data = ?, 
                    progress_updates = ?, updated_at = CURRENT_TIMESTAMP
                WHERE interaction_id = ?
            """, (
                record.status.value,
                record.end_time,
                json.dumps(record.result_data),
                json.dumps(record.error_data),
                json.dumps(record.progress_updates),
                record.interaction_id
            ))
            await db.commit()
    
    def _trim_cache(self):
        """修剪内存缓存"""
        if len(self.memory_cache) > self.cache_max_size:
            # 移除最旧的记录
            oldest_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].start_time
            )[:len(self.memory_cache) - self.cache_max_size]
            
            for key in oldest_keys:
                del self.memory_cache[key]
    
    def _update_average_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        current_avg = self.stats["average_processing_time"]
        completed_count = self.stats["completed_interactions"]
        
        if completed_count == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            # 计算移动平均
            self.stats["average_processing_time"] = (
                (current_avg * (completed_count - 1) + processing_time) / completed_count
            )
    
    async def _cleanup_old_records(self):
        """清理旧记录"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # 删除超过30天的记录
                cutoff_time = time.time() - (30 * 24 * 60 * 60)
                
                async with aiosqlite.connect(self.database_path) as db:
                    cursor = await db.execute(
                        "DELETE FROM interactions WHERE start_time < ?",
                        (cutoff_time,)
                    )
                    deleted_count = cursor.rowcount
                    await db.commit()
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old interaction records")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
    
    async def _update_stats(self):
        """更新统计信息"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟更新一次
                
                async with aiosqlite.connect(self.database_path) as db:
                    # 获取总数
                    cursor = await db.execute("SELECT COUNT(*) FROM interactions")
                    total = (await cursor.fetchone())[0]
                    
                    # 获取各状态数量
                    cursor = await db.execute(
                        "SELECT status, COUNT(*) FROM interactions GROUP BY status"
                    )
                    status_counts = dict(await cursor.fetchall())
                    
                    # 更新统计
                    self.stats.update({
                        "total_interactions": total,
                        "active_interactions": status_counts.get("started", 0) + status_counts.get("in_progress", 0),
                        "completed_interactions": status_counts.get("completed", 0),
                        "failed_interactions": status_counts.get("failed", 0)
                    })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error updating stats: {e}")
    
    async def get_interaction_history(self, 
                                    mcp_id: Optional[str] = None,
                                    limit: int = 100,
                                    offset: int = 0) -> List[Dict]:
        """获取交互历史"""
        
        query = "SELECT * FROM interactions"
        params = []
        
        if mcp_id:
            query += " WHERE mcp_id = ?"
            params.append(mcp_id)
        
        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(self.database_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    async def get_performance_metrics(self, 
                                    mcp_id: Optional[str] = None,
                                    time_range: str = "24h") -> Dict:
        """获取性能指标"""
        
        # 计算时间范围
        time_ranges = {
            "1h": 3600,
            "24h": 24 * 3600,
            "7d": 7 * 24 * 3600,
            "30d": 30 * 24 * 3600
        }
        
        seconds = time_ranges.get(time_range, 24 * 3600)
        start_time = time.time() - seconds
        
        query = """
            SELECT 
                COUNT(*) as total_count,
                AVG(end_time - start_time) as avg_processing_time,
                MIN(end_time - start_time) as min_processing_time,
                MAX(end_time - start_time) as max_processing_time,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as error_count
            FROM interactions 
            WHERE start_time >= ? AND end_time IS NOT NULL
        """
        
        params = [start_time]
        
        if mcp_id:
            query += " AND mcp_id = ?"
            params.append(mcp_id)
        
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            
            if row and row[0] > 0:  # total_count > 0
                return {
                    "time_range": time_range,
                    "total_interactions": row[0],
                    "success_rate": row[4] / row[0] if row[0] > 0 else 0,
                    "error_rate": row[5] / row[0] if row[0] > 0 else 0,
                    "avg_processing_time": row[1] or 0,
                    "min_processing_time": row[2] or 0,
                    "max_processing_time": row[3] or 0,
                    "timestamp": time.time()
                }
            else:
                return {
                    "time_range": time_range,
                    "total_interactions": 0,
                    "success_rate": 0,
                    "error_rate": 0,
                    "avg_processing_time": 0,
                    "min_processing_time": 0,
                    "max_processing_time": 0,
                    "timestamp": time.time()
                }
    
    def get_current_stats(self) -> Dict:
        """获取当前统计信息"""
        return {
            **self.stats,
            "cache_size": len(self.memory_cache),
            "timestamp": time.time()
        }
```

### **3. API密钥验证器**

```python
# api_key_validator.py
import hashlib
import hmac
import time
import logging
from typing import Dict, Optional, Set
import asyncio

class APIKeyValidator:
    """API密钥验证器"""
    
    def __init__(self, 
                 master_secret: str,
                 valid_keys: Optional[Dict[str, Dict]] = None,
                 cache_ttl: int = 300):
        
        self.master_secret = master_secret
        self.valid_keys = valid_keys or {}
        self.cache_ttl = cache_ttl
        
        # 验证缓存
        self.validation_cache: Dict[str, float] = {}
        
        self.logger = logging.getLogger("APIKeyValidator")
    
    async def validate(self, api_key: str) -> bool:
        """验证API密钥"""
        
        # 检查缓存
        if api_key in self.validation_cache:
            if time.time() - self.validation_cache[api_key] < self.cache_ttl:
                return True
            else:
                del self.validation_cache[api_key]
        
        # 验证密钥
        is_valid = await self._validate_key(api_key)
        
        if is_valid:
            self.validation_cache[api_key] = time.time()
        
        return is_valid
    
    async def _validate_key(self, api_key: str) -> bool:
        """实际验证逻辑"""
        
        # 方法1: 预定义密钥列表
        if api_key in self.valid_keys:
            key_info = self.valid_keys[api_key]
            
            # 检查是否过期
            if "expires_at" in key_info:
                if time.time() > key_info["expires_at"]:
                    return False
            
            # 检查是否被禁用
            if key_info.get("disabled", False):
                return False
            
            return True
        
        # 方法2: 基于主密钥的HMAC验证
        if api_key.startswith("sk-mcp-"):
            try:
                # 提取时间戳和签名
                parts = api_key[7:].split("-")
                if len(parts) >= 2:
                    timestamp_str = parts[0]
                    signature = "-".join(parts[1:])
                    
                    # 验证时间戳 (24小时内有效)
                    timestamp = int(timestamp_str, 16)
                    if time.time() - timestamp > 24 * 3600:
                        return False
                    
                    # 验证签名
                    expected_signature = hmac.new(
                        self.master_secret.encode(),
                        timestamp_str.encode(),
                        hashlib.sha256
                    ).hexdigest()[:16]
                    
                    return hmac.compare_digest(signature, expected_signature)
                    
            except (ValueError, IndexError):
                pass
        
        return False
    
    def generate_api_key(self, mcp_id: str, expires_in: int = 24 * 3600) -> str:
        """生成API密钥"""
        
        timestamp = int(time.time() + expires_in)
        timestamp_hex = format(timestamp, 'x')
        
        signature = hmac.new(
            self.master_secret.encode(),
            timestamp_hex.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return f"sk-mcp-{timestamp_hex}-{signature}"
    
    def add_static_key(self, api_key: str, mcp_id: str, expires_at: Optional[float] = None):
        """添加静态API密钥"""
        
        self.valid_keys[api_key] = {
            "mcp_id": mcp_id,
            "created_at": time.time(),
            "expires_at": expires_at,
            "disabled": False
        }
    
    def revoke_key(self, api_key: str):
        """撤销API密钥"""
        
        if api_key in self.valid_keys:
            self.valid_keys[api_key]["disabled"] = True
        
        if api_key in self.validation_cache:
            del self.validation_cache[api_key]
```

### **4. 配置和启动**

```python
# coordinator_extensions.py
import asyncio
import logging
from pathlib import Path
from interaction_api import create_interaction_app
from interaction_log_manager import InteractionLogManager
from api_key_validator import APIKeyValidator

class MCPCoordinatorExtensions:
    """MCPCoordinator扩展模块"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("MCPCoordinatorExtensions")
        
        # 核心组件
        self.interaction_log_manager = None
        self.api_key_validator = None
        self.interaction_app = None
        
        # 是否启用扩展功能
        self.extensions_enabled = config.get("extensions", {})
    
    async def start(self):
        """启动扩展功能"""
        
        if self.extensions_enabled.get("interaction_logging", False):
            await self._start_interaction_logging()
        
        self.logger.info("MCPCoordinator extensions started")
    
    async def stop(self):
        """停止扩展功能"""
        
        if self.interaction_log_manager:
            await self.interaction_log_manager.stop()
        
        self.logger.info("MCPCoordinator extensions stopped")
    
    async def _start_interaction_logging(self):
        """启动交互日志功能"""
        
        # 创建数据目录
        data_dir = Path(self.config.get("data_directory", "./data"))
        data_dir.mkdir(exist_ok=True)
        
        # 初始化API密钥验证器
        self.api_key_validator = APIKeyValidator(
            master_secret=self.config["master_secret"],
            valid_keys=self.config.get("static_api_keys", {}),
            cache_ttl=self.config.get("api_key_cache_ttl", 300)
        )
        
        # 初始化交互日志管理器
        self.interaction_log_manager = InteractionLogManager(
            database_path=str(data_dir / "interactions.db"),
            max_records=self.config.get("max_interaction_records", 1000000),
            cleanup_interval=self.config.get("cleanup_interval", 3600)
        )
        
        await self.interaction_log_manager.start()
        
        # 创建FastAPI应用
        self.interaction_app = create_interaction_app(
            self.interaction_log_manager,
            self.api_key_validator
        )
        
        self.logger.info("Interaction logging started")

# 配置示例
config = {
    "extensions": {
        "interaction_logging": True
    },
    "master_secret": "your-master-secret-key",
    "data_directory": "./data",
    "max_interaction_records": 1000000,
    "cleanup_interval": 3600,
    "api_key_cache_ttl": 300,
    "static_api_keys": {
        "sk-mcp-static-key-1": {
            "mcp_id": "ocr_workflow_mcp_001",
            "created_at": 1640995200,
            "expires_at": None,
            "disabled": False
        }
    }
}

# 启动示例
async def main():
    extensions = MCPCoordinatorExtensions(config)
    await extensions.start()
    
    # 运行FastAPI应用
    import uvicorn
    uvicorn.run(
        extensions.interaction_app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 监控和分析

### **性能监控仪表板**

```python
# monitoring_dashboard.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import time

def create_monitoring_dashboard(interaction_log_manager) -> FastAPI:
    """创建监控仪表板"""
    
    app = FastAPI(title="MCPCoordinator Monitoring Dashboard")
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCPCoordinator Monitoring</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .metric-card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
                .chart-container { width: 100%; height: 400px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>MCPCoordinator Monitoring Dashboard</h1>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Current Statistics</h3>
                    <div id="current-stats"></div>
                </div>
                
                <div class="metric-card">
                    <h3>Performance Metrics</h3>
                    <div id="performance-metrics"></div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="interactions-chart"></canvas>
            </div>
            
            <script>
                async function updateDashboard() {
                    try {
                        // 获取当前统计
                        const statsResponse = await fetch('/api/v2/interactions/stats');
                        const stats = await statsResponse.json();
                        document.getElementById('current-stats').innerHTML = `
                            <p>Total Interactions: ${stats.stats.total_interactions}</p>
                            <p>Active: ${stats.stats.active_interactions}</p>
                            <p>Completed: ${stats.stats.completed_interactions}</p>
                            <p>Failed: ${stats.stats.failed_interactions}</p>
                            <p>Queue Size: ${stats.queue_size}</p>
                        `;
                        
                        // 获取性能指标
                        const perfResponse = await fetch('/api/v2/performance/metrics?time_range=24h');
                        const perf = await perfResponse.json();
                        document.getElementById('performance-metrics').innerHTML = `
                            <p>Success Rate: ${(perf.success_rate * 100).toFixed(2)}%</p>
                            <p>Avg Processing Time: ${perf.avg_processing_time.toFixed(2)}s</p>
                            <p>Min Processing Time: ${perf.min_processing_time.toFixed(2)}s</p>
                            <p>Max Processing Time: ${perf.max_processing_time.toFixed(2)}s</p>
                        `;
                        
                    } catch (error) {
                        console.error('Error updating dashboard:', error);
                    }
                }
                
                // 初始化图表
                const ctx = document.getElementById('interactions-chart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Interactions per Hour',
                            data: [],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
                
                // 定期更新
                updateDashboard();
                setInterval(updateDashboard, 30000); // 每30秒更新
            </script>
        </body>
        </html>
        """
    
    @app.get("/api/v2/performance/metrics")
    async def get_performance_metrics(time_range: str = "24h", mcp_id: str = None):
        return await interaction_log_manager.get_performance_metrics(mcp_id, time_range)
    
    return app
```

## 🔧 部署和配置

### **Docker部署配置**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "coordinator_extensions.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-coordinator:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - CONFIG_PATH=/app/config/coordinator.toml
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### **配置文件模板**

```toml
# coordinator_extensions.toml
[extensions]
interaction_logging = true

[interaction_logging]
database_path = "./data/interactions.db"
max_records = 1000000
cleanup_interval = 3600
api_key_cache_ttl = 300

[security]
master_secret = "your-very-secure-master-secret-key"

[api]
host = "0.0.0.0"
port = 8080
workers = 4

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[static_api_keys]
"sk-mcp-ocr-workflow-001" = { mcp_id = "ocr_workflow_mcp_001", expires_at = null, disabled = false }
"sk-mcp-data-analysis-001" = { mcp_id = "data_analysis_workflow_001", expires_at = null, disabled = false }
```

## 📋 运维检查清单

### **部署前检查**
- [ ] 配置文件正确设置
- [ ] 数据目录权限正确
- [ ] API密钥安全生成
- [ ] 网络端口开放

### **运行时监控**
- [ ] API响应时间正常
- [ ] 队列大小在合理范围
- [ ] 数据库性能良好
- [ ] 内存使用率正常

### **定期维护**
- [ ] 清理旧的交互记录
- [ ] 备份重要数据
- [ ] 更新API密钥
- [ ] 检查系统日志

---

这个架构设计确保了MCPCoordinator能够高效、可靠地管理所有MCP的交互数据，同时保持系统的稳定性和可扩展性。

