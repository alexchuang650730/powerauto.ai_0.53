#!/usr/bin/env python3
"""
PowerAutomation 分布式测试协调器核心实现
集成v0.571现有基础设施的生产级协调器

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

# 导入数据模型 - 使用绝对导入
from shared_core.engines.distributed_coordinator.models.node import TestNode, NodeStatus
from shared_core.engines.distributed_coordinator.models.task import TestTask, TaskStatus, TaskPriority
from shared_core.engines.distributed_coordinator.models.result import TestResult, ExecutionMetrics
from shared_core.engines.utils.config import Config
from shared_core.engines.utils.database import DatabaseManager
from shared_core.engines.utils.message_queue import MessageQueue
from shared_core.engines.utils.metrics import MetricsCollector

# 导入现有PowerAutomation组件
try:
    from powerauto.ai_coordination_hub import AICoordinationHub
    from powerauto.smart_routing_system import SmartRoutingSystem
    from powerauto.dev_deploy_coordinator import DevDeployLoopCoordinator
except ImportError:
    # Mock classes for development
    class AICoordinationHub:
        async def orchestrate_collaboration(self, task): return {"status": "success"}
    class SmartRoutingSystem:
        def route_task(self, task): return {"location": "local", "cost": 0.1}
    class DevDeployLoopCoordinator:
        async def execute_loop(self, task): return {"status": "completed"}

logger = logging.getLogger("PowerAutomation.Coordinator")

class CoordinatorStatus(Enum):
    """协调器状态枚举"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class CoordinatorMetrics:
    """协调器性能指标"""
    total_nodes: int = 0
    active_nodes: int = 0
    total_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    throughput_per_minute: float = 0.0
    resource_utilization: float = 0.0

class NodeManager:
    """测试节点管理器 - 生产级实现"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager, message_queue: MessageQueue):
        self.config = config
        self.db = db_manager
        self.mq = message_queue
        self.nodes: Dict[str, TestNode] = {}
        self.node_capabilities: Dict[str, Set[str]] = {}
        self.performance_history: Dict[str, List[Dict]] = {}
        self.heartbeat_timeout = config.coordinator.heartbeat_timeout
        self._lock = threading.RLock()
        
    async def initialize(self):
        """初始化节点管理器"""
        logger.info("🔧 初始化节点管理器...")
        
        # 从数据库加载已注册的节点
        await self._load_nodes_from_db()
        
        # 启动心跳监控
        asyncio.create_task(self._heartbeat_monitor())
        
        logger.info(f"✅ 节点管理器初始化完成，已加载 {len(self.nodes)} 个节点")
    
    async def register_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """注册测试节点"""
        try:
            with self._lock:
                node = TestNode(
                    node_id=node_data["node_id"],
                    host=node_data["host"],
                    port=node_data["port"],
                    capabilities=set(node_data.get("capabilities", [])),
                    max_concurrent_tasks=node_data.get("max_concurrent_tasks", 5),
                    current_tasks=0,
                    status=NodeStatus.ACTIVE,
                    last_heartbeat=datetime.now(),
                    performance_metrics=node_data.get("performance_metrics", {}),
                    metadata=node_data.get("metadata", {})
                )
                
                # 保存到内存
                self.nodes[node.node_id] = node
                self.node_capabilities[node.node_id] = node.capabilities
                self.performance_history[node.node_id] = []
                
                # 保存到数据库
                await self.db.save_node(node)
                
                # 发送节点注册事件
                await self.mq.publish("node.registered", {
                    "node_id": node.node_id,
                    "capabilities": list(node.capabilities),
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"✅ 节点注册成功: {node.node_id} ({node.host}:{node.port})")
                return {"success": True, "node_id": node.node_id}
                
        except Exception as e:
            logger.error(f"❌ 节点注册失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def unregister_node(self, node_id: str) -> bool:
        """注销测试节点"""
        try:
            with self._lock:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    
                    # 标记节点为离线
                    node.status = NodeStatus.OFFLINE
                    await self.db.update_node_status(node_id, NodeStatus.OFFLINE)
                    
                    # 清理内存数据
                    del self.nodes[node_id]
                    if node_id in self.node_capabilities:
                        del self.node_capabilities[node_id]
                    if node_id in self.performance_history:
                        del self.performance_history[node_id]
                    
                    # 发送节点注销事件
                    await self.mq.publish("node.unregistered", {
                        "node_id": node_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.info(f"✅ 节点注销成功: {node_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ 节点注销失败: {e}")
            return False
    
    async def update_heartbeat(self, node_id: str, metrics: Dict[str, Any]) -> bool:
        """更新节点心跳"""
        try:
            with self._lock:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    node.last_heartbeat = datetime.now()
                    node.performance_metrics = metrics
                    
                    # 更新性能历史
                    self.performance_history[node_id].append({
                        "timestamp": datetime.now().isoformat(),
                        "metrics": metrics
                    })
                    
                    # 保持最近100条记录
                    if len(self.performance_history[node_id]) > 100:
                        self.performance_history[node_id] = self.performance_history[node_id][-100:]
                    
                    # 更新数据库
                    await self.db.update_node_heartbeat(node_id, metrics)
                    
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ 心跳更新失败: {e}")
            return False
    
    def get_available_nodes(self, requirements: Dict[str, Any]) -> List[TestNode]:
        """获取满足要求的可用节点"""
        available_nodes = []
        
        with self._lock:
            for node in self.nodes.values():
                if self._is_node_available(node, requirements):
                    available_nodes.append(node)
        
        # 按性能评分排序
        available_nodes.sort(key=self._calculate_node_score, reverse=True)
        return available_nodes
    
    def _is_node_available(self, node: TestNode, requirements: Dict[str, Any]) -> bool:
        """检查节点是否可用"""
        # 检查节点状态
        if node.status not in [NodeStatus.ACTIVE, NodeStatus.IDLE]:
            return False
        
        # 检查心跳超时
        if (datetime.now() - node.last_heartbeat).seconds > self.heartbeat_timeout:
            node.status = NodeStatus.OFFLINE
            return False
        
        # 检查并发任务限制
        if node.current_tasks >= node.max_concurrent_tasks:
            return False
        
        # 检查能力要求
        required_capabilities = set(requirements.get("capabilities", []))
        if not required_capabilities.issubset(node.capabilities):
            return False
        
        # 检查资源要求
        if not self._check_resource_requirements(node, requirements):
            return False
        
        return True
    
    def _check_resource_requirements(self, node: TestNode, requirements: Dict[str, Any]) -> bool:
        """检查节点资源要求"""
        resources = requirements.get("resources", {})
        metrics = node.performance_metrics
        
        # 检查CPU使用率
        if "max_cpu_usage" in resources:
            if metrics.get("cpu_usage", 100) > resources["max_cpu_usage"]:
                return False
        
        # 检查内存使用率
        if "max_memory_usage" in resources:
            if metrics.get("memory_usage", 100) > resources["max_memory_usage"]:
                return False
        
        # 检查最小可用内存
        if "min_available_memory_gb" in resources:
            available_memory = metrics.get("available_memory_gb", 0)
            if available_memory < resources["min_available_memory_gb"]:
                return False
        
        return True
    
    def _calculate_node_score(self, node: TestNode) -> float:
        """计算节点性能评分"""
        metrics = node.performance_metrics
        
        # 基础评分
        score = 100.0
        
        # CPU使用率评分 (使用率越低越好)
        cpu_usage = metrics.get("cpu_usage", 50)
        score -= cpu_usage * 0.5
        
        # 内存使用率评分 (使用率越低越好)
        memory_usage = metrics.get("memory_usage", 50)
        score -= memory_usage * 0.3
        
        # 当前任务负载评分
        load_ratio = node.current_tasks / node.max_concurrent_tasks
        score -= load_ratio * 20
        
        # 历史性能评分
        if node.node_id in self.performance_history:
            history = self.performance_history[node.node_id]
            if history:
                recent_history = history[-10:]  # 最近10条记录
                avg_response_time = sum(h["metrics"].get("avg_response_time", 1.0) for h in recent_history) / len(recent_history)
                score -= avg_response_time * 10
        
        return max(score, 0)
    
    async def _load_nodes_from_db(self):
        """从数据库加载节点"""
        try:
            nodes_data = await self.db.load_all_nodes()
            for node_data in nodes_data:
                node = TestNode.from_dict(node_data)
                self.nodes[node.node_id] = node
                self.node_capabilities[node.node_id] = node.capabilities
                self.performance_history[node.node_id] = []
                
        except Exception as e:
            logger.error(f"❌ 从数据库加载节点失败: {e}")
    
    async def _heartbeat_monitor(self):
        """心跳监控循环"""
        while True:
            try:
                current_time = datetime.now()
                offline_nodes = []
                
                with self._lock:
                    for node_id, node in self.nodes.items():
                        if (current_time - node.last_heartbeat).seconds > self.heartbeat_timeout:
                            if node.status != NodeStatus.OFFLINE:
                                node.status = NodeStatus.OFFLINE
                                offline_nodes.append(node_id)
                
                # 处理离线节点
                for node_id in offline_nodes:
                    await self.db.update_node_status(node_id, NodeStatus.OFFLINE)
                    await self.mq.publish("node.offline", {
                        "node_id": node_id,
                        "timestamp": current_time.isoformat()
                    })
                    logger.warning(f"⚠️ 节点离线: {node_id}")
                
                await asyncio.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                logger.error(f"❌ 心跳监控错误: {e}")
                await asyncio.sleep(30)

class TaskScheduler:
    """智能任务调度器 - 生产级实现"""
    
    def __init__(self, config: Config, node_manager: NodeManager, db_manager: DatabaseManager, message_queue: MessageQueue):
        self.config = config
        self.node_manager = node_manager
        self.db = db_manager
        self.mq = message_queue
        self.task_queue: List[TestTask] = []
        self.running_tasks: Dict[str, TestTask] = {}
        self.completed_tasks: Dict[str, TestTask] = {}
        self.scheduling_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=config.coordinator.max_scheduler_threads)
        
        # 集成现有PowerAutomation组件
        self.ai_hub = AICoordinationHub()
        self.smart_router = SmartRoutingSystem()
        self.dev_coordinator = DevDeployLoopCoordinator()
