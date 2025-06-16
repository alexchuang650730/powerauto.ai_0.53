# Memory MCP与InteractionLogManager整合方案

## 🎯 整合目标

<<<<<<< HEAD
将PowerAutomation的Unified Memory MCP与我们的InteractionLogManager整合，实现：
=======
基于PowerAutomation现有的SuperMemory适配器和Unified Memory MCP，将记忆系统与我们的InteractionLogManager整合，实现：
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647

### **1. 智能记忆管理**
- 自动将交互数据转换为长期记忆
- 基于用户行为模式优化记忆存储
- 跨会话的上下文保持和学习

### **2. 增强的决策能力**
- 基于历史记忆优化路由决策
- 个性化的workflow推荐
- 预测性的用户需求分析

### **3. 统一的数据生态**
- 交互数据 → 记忆存储 → 智能检索
- 多源记忆的统一管理
- 实时学习和优化

<<<<<<< HEAD
## 🏗️ 整合架构设计

### **核心组件关系**
=======
## 🏗️ 基于现有架构的整合设计

### **现有组件分析**

#### **1. SuperMemory适配器特性**
- ✅ 实现了`KiloCodeAdapterInterface`标准接口
- ✅ 提供完整的记忆CRUD操作
- ✅ 支持API密钥认证和配置管理
- ✅ 完善的错误处理和健康检查

#### **2. Unified Memory MCP特性**
- ✅ 多源记忆管理（GitHub、SuperMemory、RAG、本地）
- ✅ 丰富的操作接口（query、insert、update、delete等）
- ✅ 完整的统计和监控系统
- ✅ 向量检索和语义搜索

### **整合架构设计**
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647

```
MCPCoordinator {
    InteractionLogManager {
        - 收集交互数据
        - 实时数据分析
        - 触发记忆存储
    }
    
<<<<<<< HEAD
    MemoryMCP {
        - 长期记忆管理
        - 智能检索服务
        - 跨源记忆整合
    }
    
    SmartRouter {
=======
    UnifiedMemoryMCP {
        - SuperMemoryAdapter (外部记忆服务)
        - LocalMemoryAdapter (本地记忆存储)
        - RAGMemoryAdapter (向量检索)
        - GitHubMemoryAdapter (代码记忆)
    }
    
    MemoryEnhancedRouter {
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        - 基于记忆的路由决策
        - 个性化推荐
        - 预测性分析
    }
}
```

<<<<<<< HEAD
### **数据流设计**

```
用户请求 → MCP处理 → 交互数据 → InteractionLogManager
                                        ↓
记忆检索 ← MemoryMCP ← 记忆转换 ← 数据分析
    ↓
SmartRouter → 优化决策 → 个性化响应
```

=======
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
## 🔧 技术实现方案

### **1. 记忆数据转换器 (MemoryDataConverter)**

```python
<<<<<<< HEAD
class MemoryDataConverter:
    """将交互数据转换为记忆格式"""
    
    def convert_interaction_to_memory(self, interaction_data: Dict) -> Dict:
        """转换交互数据为记忆格式"""
        return {
            "content": self._extract_content(interaction_data),
            "metadata": {
                "user_id": interaction_data.get("user_id"),
                "mcp_type": interaction_data.get("mcp_type"),
                "operation": interaction_data.get("operation"),
                "timestamp": interaction_data.get("timestamp"),
                "success": interaction_data.get("success"),
                "response_time": interaction_data.get("response_time"),
                "context": interaction_data.get("context", {}),
                "tags": self._generate_tags(interaction_data)
            },
            "source": "interaction_log"
        }
    
    def _extract_content(self, interaction_data: Dict) -> str:
        """提取关键内容"""
        content_parts = []
        
        # 用户请求内容
        if "request" in interaction_data:
            content_parts.append(f"用户请求: {interaction_data['request']}")
        
        # 处理结果
        if "response" in interaction_data:
            content_parts.append(f"处理结果: {interaction_data['response']}")
=======
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class MemoryDataConverter:
    """将交互数据转换为记忆格式，兼容SuperMemory适配器"""
    
    def __init__(self, supermemory_adapter: SuperMemoryAdapter):
        self.supermemory = supermemory_adapter
        self.memory_rules = self._load_memory_rules()
    
    def convert_interaction_to_memory(self, interaction_data: Dict) -> Dict:
        """转换交互数据为记忆格式"""
        # 生成唯一的记忆键
        memory_key = self._generate_memory_key(interaction_data)
        
        # 提取和结构化内容
        content = self._extract_structured_content(interaction_data)
        
        # 生成元数据
        metadata = self._generate_metadata(interaction_data)
        
        return {
            "key": memory_key,
            "content": content,
            "metadata": metadata,
            "source": "interaction_log",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_memory_key(self, interaction_data: Dict) -> str:
        """生成唯一的记忆键"""
        # 基于用户ID、时间戳和内容哈希生成唯一键
        user_id = interaction_data.get("user_id", "anonymous")
        timestamp = interaction_data.get("timestamp", "")
        content_hash = hashlib.md5(
            str(interaction_data.get("request", "")).encode()
        ).hexdigest()[:8]
        
        return f"interaction_{user_id}_{timestamp}_{content_hash}"
    
    def _extract_structured_content(self, interaction_data: Dict) -> str:
        """提取结构化内容"""
        content_parts = []
        
        # 用户请求
        if "request" in interaction_data:
            content_parts.append(f"用户请求: {interaction_data['request']}")
        
        # MCP类型和操作
        mcp_type = interaction_data.get("mcp_type", "")
        operation = interaction_data.get("operation", "")
        if mcp_type and operation:
            content_parts.append(f"处理方式: {mcp_type}.{operation}")
        
        # 处理结果
        if "response" in interaction_data:
            response = interaction_data['response']
            if isinstance(response, dict):
                response = json.dumps(response, ensure_ascii=False)
            content_parts.append(f"处理结果: {response}")
        
        # 性能信息
        response_time = interaction_data.get("response_time", 0)
        if response_time:
            content_parts.append(f"响应时间: {response_time}ms")
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        
        # 错误信息
        if "error" in interaction_data:
            content_parts.append(f"错误信息: {interaction_data['error']}")
        
        return " | ".join(content_parts)
    
<<<<<<< HEAD
=======
    def _generate_metadata(self, interaction_data: Dict) -> Dict:
        """生成记忆元数据"""
        metadata = {
            "user_id": interaction_data.get("user_id", "anonymous"),
            "mcp_type": interaction_data.get("mcp_type", ""),
            "operation": interaction_data.get("operation", ""),
            "timestamp": interaction_data.get("timestamp", ""),
            "success": interaction_data.get("success", False),
            "response_time": interaction_data.get("response_time", 0),
            "context": interaction_data.get("context", {}),
            "tags": self._generate_tags(interaction_data),
            "quality_score": self._calculate_quality_score(interaction_data)
        }
        
        return metadata
    
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
    def _generate_tags(self, interaction_data: Dict) -> List[str]:
        """生成记忆标签"""
        tags = []
        
        # 基于MCP类型的标签
        mcp_type = interaction_data.get("mcp_type", "")
        if mcp_type:
            tags.append(f"mcp:{mcp_type}")
        
        # 基于操作类型的标签
        operation = interaction_data.get("operation", "")
        if operation:
            tags.append(f"op:{operation}")
        
        # 基于成功状态的标签
        if interaction_data.get("success"):
            tags.append("status:success")
        else:
            tags.append("status:failed")
        
        # 基于响应时间的标签
        response_time = interaction_data.get("response_time", 0)
        if response_time > 5000:  # 5秒以上
            tags.append("performance:slow")
        elif response_time < 1000:  # 1秒以下
            tags.append("performance:fast")
        else:
            tags.append("performance:normal")
        
<<<<<<< HEAD
        return tags
=======
        # 基于内容类型的标签
        request_content = str(interaction_data.get("request", "")).lower()
        if "ocr" in request_content or "识别" in request_content:
            tags.append("content:ocr")
        elif "search" in request_content or "搜索" in request_content:
            tags.append("content:search")
        elif "generate" in request_content or "生成" in request_content:
            tags.append("content:generation")
        
        return tags
    
    def _calculate_quality_score(self, interaction_data: Dict) -> float:
        """计算记忆质量分数"""
        score = 0.5  # 基础分数
        
        # 成功的交互加分
        if interaction_data.get("success"):
            score += 0.3
        
        # 响应时间影响
        response_time = interaction_data.get("response_time", 0)
        if response_time < 1000:
            score += 0.1
        elif response_time > 10000:
            score -= 0.2
        
        # 内容丰富度影响
        request_length = len(str(interaction_data.get("request", "")))
        response_length = len(str(interaction_data.get("response", "")))
        if request_length > 50 and response_length > 100:
            score += 0.1
        
        return max(0.0, min(1.0, score))  # 限制在0-1之间
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
```

### **2. 智能记忆管理器 (IntelligentMemoryManager)**

```python
<<<<<<< HEAD
class IntelligentMemoryManager:
    """智能记忆管理器"""
    
    def __init__(self, memory_mcp: UnifiedMemoryMCP):
        self.memory_mcp = memory_mcp
        self.converter = MemoryDataConverter()
        self.memory_rules = self._load_memory_rules()
    
    async def process_interaction_data(self, interaction_data: Dict) -> Dict:
        """处理交互数据并存储为记忆"""
        try:
            # 判断是否需要存储为记忆
            if not self._should_store_as_memory(interaction_data):
=======
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class IntelligentMemoryManager:
    """智能记忆管理器，整合SuperMemory和Unified Memory MCP"""
    
    def __init__(self, unified_memory_mcp, supermemory_adapter: SuperMemoryAdapter):
        self.unified_memory = unified_memory_mcp
        self.supermemory = supermemory_adapter
        self.converter = MemoryDataConverter(supermemory_adapter)
        self.memory_rules = self._load_memory_rules()
        self.stats = {
            "total_processed": 0,
            "stored_count": 0,
            "skipped_count": 0,
            "error_count": 0
        }
    
    async def process_interaction_data(self, interaction_data: Dict) -> Dict:
        """处理交互数据并存储为记忆"""
        self.stats["total_processed"] += 1
        
        try:
            # 判断是否需要存储为记忆
            if not self._should_store_as_memory(interaction_data):
                self.stats["skipped_count"] += 1
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
                return {"status": "skipped", "reason": "不符合记忆存储条件"}
            
            # 转换为记忆格式
            memory_data = self.converter.convert_interaction_to_memory(interaction_data)
            
<<<<<<< HEAD
            # 选择最佳记忆源
            memory_source = self._select_memory_source(memory_data)
            
            # 存储记忆
            result = await self.memory_mcp.insert_memory(
                content=memory_data["content"],
                metadata=memory_data["metadata"],
                source=memory_source
            )
            
            # 更新记忆索引
            if result.get("status") == "success":
                await self._update_memory_index(memory_data, result.get("memory_id"))
=======
            # 选择最佳存储策略
            storage_strategy = self._select_storage_strategy(memory_data)
            
            # 执行存储
            result = await self._execute_storage(memory_data, storage_strategy)
            
            if result.get("status") == "success":
                self.stats["stored_count"] += 1
                # 异步更新索引
                asyncio.create_task(self._update_memory_index(memory_data, result))
            else:
                self.stats["error_count"] += 1
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            
            return result
            
        except Exception as e:
<<<<<<< HEAD
=======
            self.stats["error_count"] += 1
            logger.error(f"记忆存储失败: {str(e)}")
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            return {"status": "error", "message": f"记忆存储失败: {str(e)}"}
    
    def _should_store_as_memory(self, interaction_data: Dict) -> bool:
        """判断是否应该存储为记忆"""
        # 成功的交互更有价值
        if not interaction_data.get("success", False):
            return False
        
        # 过滤掉简单的查询操作
        operation = interaction_data.get("operation", "")
<<<<<<< HEAD
        if operation in ["health_check", "status", "ping"]:
=======
        if operation in ["health_check", "status", "ping", "heartbeat"]:
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            return False
        
        # 响应时间过长的可能有问题
        response_time = interaction_data.get("response_time", 0)
        if response_time > 30000:  # 30秒以上
            return False
        
        # 有实际内容的交互
<<<<<<< HEAD
        if not interaction_data.get("request") and not interaction_data.get("response"):
=======
        request = interaction_data.get("request", "")
        response = interaction_data.get("response", "")
        if not request and not response:
            return False
        
        # 质量分数阈值
        quality_score = self.converter._calculate_quality_score(interaction_data)
        if quality_score < 0.6:
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            return False
        
        return True
    
<<<<<<< HEAD
    def _select_memory_source(self, memory_data: Dict) -> str:
        """选择最佳记忆源"""
        metadata = memory_data.get("metadata", {})
        
        # 代码相关的存储到GitHub记忆
        if any(tag.startswith("mcp:code") for tag in metadata.get("tags", [])):
            return "github"
        
        # 复杂查询存储到RAG
        if "search" in metadata.get("operation", "").lower():
            return "rag"
        
        # 用户偏好存储到本地
        if "user_preference" in metadata.get("context", {}):
            return "local"
        
        # 默认存储到本地
        return "local"
    
    async def _update_memory_index(self, memory_data: Dict, memory_id: str):
        """更新记忆索引"""
        try:
            await self.memory_mcp.index_memory(
                memory_id=memory_id,
                tags=memory_data["metadata"].get("tags", []),
                keywords=self._extract_keywords(memory_data["content"])
            )
=======
    def _select_storage_strategy(self, memory_data: Dict) -> Dict:
        """选择存储策略"""
        metadata = memory_data.get("metadata", {})
        tags = metadata.get("tags", [])
        
        strategy = {
            "primary_storage": "local",
            "backup_storage": None,
            "enable_search_index": True,
            "retention_days": 90
        }
        
        # 代码相关的存储到GitHub记忆
        if any(tag.startswith("mcp:code") for tag in tags):
            strategy["primary_storage"] = "github"
            strategy["backup_storage"] = "local"
        
        # 搜索相关的存储到RAG
        elif any(tag.startswith("content:search") for tag in tags):
            strategy["primary_storage"] = "rag"
            strategy["backup_storage"] = "local"
        
        # 高质量交互存储到SuperMemory
        elif metadata.get("quality_score", 0) > 0.8:
            strategy["primary_storage"] = "supermemory"
            strategy["backup_storage"] = "local"
            strategy["retention_days"] = 180  # 高质量记忆保存更久
        
        # 用户偏好存储到本地
        elif "user_preference" in metadata.get("context", {}):
            strategy["primary_storage"] = "local"
            strategy["retention_days"] = 365  # 用户偏好保存一年
        
        return strategy
    
    async def _execute_storage(self, memory_data: Dict, strategy: Dict) -> Dict:
        """执行存储操作"""
        primary_storage = strategy["primary_storage"]
        
        try:
            if primary_storage == "supermemory":
                # 使用SuperMemory适配器存储
                result = self.supermemory.store_memory(
                    key=memory_data["key"],
                    value=memory_data["content"],
                    metadata=memory_data["metadata"]
                )
            else:
                # 使用Unified Memory MCP存储
                result = await self.unified_memory.insert_memory(
                    content=memory_data["content"],
                    metadata=memory_data["metadata"],
                    source=primary_storage
                )
            
            # 如果主存储失败，尝试备份存储
            if result.get("status") != "success" and strategy.get("backup_storage"):
                backup_result = await self.unified_memory.insert_memory(
                    content=memory_data["content"],
                    metadata=memory_data["metadata"],
                    source=strategy["backup_storage"]
                )
                if backup_result.get("status") == "success":
                    result = backup_result
                    result["storage_location"] = strategy["backup_storage"]
            else:
                result["storage_location"] = primary_storage
            
            return result
            
        except Exception as e:
            logger.error(f"存储执行失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _update_memory_index(self, memory_data: Dict, storage_result: Dict):
        """更新记忆索引"""
        try:
            if storage_result.get("storage_location") != "supermemory":
                # 只有非SuperMemory存储需要手动更新索引
                await self.unified_memory.index_memory(
                    memory_id=storage_result.get("memory_id"),
                    tags=memory_data["metadata"].get("tags", []),
                    keywords=self._extract_keywords(memory_data["content"])
                )
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        except Exception as e:
            logger.warning(f"记忆索引更新失败: {str(e)}")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
<<<<<<< HEAD
        # 简单的关键词提取逻辑
        import re
        words = re.findall(r'\b\w+\b', content.lower())
        # 过滤停用词和短词
        keywords = [word for word in words if len(word) > 3 and word not in ["用户", "请求", "处理", "结果"]]
        return list(set(keywords))[:10]  # 最多10个关键词
=======
        import re
        words = re.findall(r'\b\w+\b', content.lower())
        # 过滤停用词和短词
        stop_words = {"用户", "请求", "处理", "结果", "系统", "操作", "执行", "完成"}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return list(set(keywords))[:10]  # 最多10个关键词
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": self.stats["stored_count"] / max(1, self.stats["total_processed"]),
            "error_rate": self.stats["error_count"] / max(1, self.stats["total_processed"])
        }
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
```

### **3. 记忆增强路由器 (MemoryEnhancedRouter)**

```python
class MemoryEnhancedRouter:
    """基于记忆的增强路由器"""
    
<<<<<<< HEAD
    def __init__(self, memory_mcp: UnifiedMemoryMCP):
        self.memory_mcp = memory_mcp
        self.user_profiles = {}  # 用户画像缓存
=======
    def __init__(self, unified_memory_mcp, supermemory_adapter: SuperMemoryAdapter):
        self.unified_memory = unified_memory_mcp
        self.supermemory = supermemory_adapter
        self.user_profiles = {}  # 用户画像缓存
        self.cache_ttl = 3600  # 缓存1小时
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
    
    async def enhanced_route_decision(self, request: Dict) -> Dict:
        """基于记忆的增强路由决策"""
        try:
            user_id = request.get("user_id", "anonymous")
            
            # 获取用户历史记忆
            user_memory = await self._get_user_memory(user_id, request)
            
            # 分析用户偏好
<<<<<<< HEAD
            user_preferences = self._analyze_user_preferences(user_memory)
=======
            user_preferences = await self._analyze_user_preferences(user_id, user_memory)
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            
            # 基于记忆的路由推荐
            routing_recommendation = self._generate_routing_recommendation(
                request, user_preferences, user_memory
            )
            
            return {
                "status": "success",
                "routing_recommendation": routing_recommendation,
                "user_preferences": user_preferences,
<<<<<<< HEAD
                "confidence": routing_recommendation.get("confidence", 0.5)
            }
            
        except Exception as e:
=======
                "confidence": routing_recommendation.get("confidence", 0.5),
                "memory_insights": self._extract_memory_insights(user_memory)
            }
            
        except Exception as e:
            logger.error(f"记忆增强路由失败: {str(e)}")
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            return {"status": "error", "message": f"记忆增强路由失败: {str(e)}"}
    
    async def _get_user_memory(self, user_id: str, request: Dict) -> List[Dict]:
        """获取用户相关记忆"""
<<<<<<< HEAD
        # 构建查询
        query_parts = []
        
        # 基于用户ID查询
        query_parts.append(f"user_id:{user_id}")
        
        # 基于请求内容查询
        if "content" in request:
            query_parts.append(request["content"][:100])  # 限制长度
        
        # 基于操作类型查询
        if "operation" in request:
            query_parts.append(f"operation:{request['operation']}")
        
        query = " ".join(query_parts)
        
        # 执行记忆查询
        memory_result = await self.memory_mcp.query_memory(
            query=query,
            sources=["local", "rag"],
            limit=20
        )
        
        return memory_result.get("results", [])
    
    def _analyze_user_preferences(self, user_memory: List[Dict]) -> Dict:
        """分析用户偏好"""
=======
        memories = []
        
        try:
            # 从Unified Memory MCP查询
            unified_query = f"user_id:{user_id}"
            if "content" in request:
                unified_query += f" {request['content'][:100]}"
            
            unified_result = await self.unified_memory.query_memory(
                query=unified_query,
                sources=["local", "rag"],
                limit=15
            )
            memories.extend(unified_result.get("results", []))
            
            # 从SuperMemory查询
            if "content" in request:
                supermemory_result = self.supermemory.search_memories(
                    query=f"{user_id} {request['content'][:50]}",
                    limit=10
                )
                if supermemory_result.get("status") == "success":
                    memories.extend(supermemory_result.get("results", []))
            
        except Exception as e:
            logger.warning(f"记忆查询失败: {str(e)}")
        
        return memories[:20]  # 限制最多20个记忆
    
    async def _analyze_user_preferences(self, user_id: str, user_memory: List[Dict]) -> Dict:
        """分析用户偏好"""
        # 检查缓存
        cache_key = f"preferences_{user_id}"
        if cache_key in self.user_profiles:
            cached_time, preferences = self.user_profiles[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return preferences
        
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        preferences = {
            "preferred_mcps": {},
            "preferred_operations": {},
            "performance_preference": "balanced",  # fast, balanced, quality
<<<<<<< HEAD
            "success_patterns": [],
            "failure_patterns": []
        }
        
=======
            "content_types": {},
            "success_patterns": [],
            "failure_patterns": [],
            "avg_response_time": 0,
            "quality_threshold": 0.7
        }
        
        total_response_time = 0
        response_count = 0
        
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        for memory in user_memory:
            metadata = memory.get("metadata", {})
            
            # 统计MCP使用偏好
            mcp_type = metadata.get("mcp_type")
            if mcp_type:
                preferences["preferred_mcps"][mcp_type] = preferences["preferred_mcps"].get(mcp_type, 0) + 1
            
            # 统计操作偏好
            operation = metadata.get("operation")
            if operation:
                preferences["preferred_operations"][operation] = preferences["preferred_operations"].get(operation, 0) + 1
            
<<<<<<< HEAD
=======
            # 统计内容类型偏好
            tags = metadata.get("tags", [])
            for tag in tags:
                if tag.startswith("content:"):
                    content_type = tag.split(":")[1]
                    preferences["content_types"][content_type] = preferences["content_types"].get(content_type, 0) + 1
            
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            # 分析性能偏好
            response_time = metadata.get("response_time", 0)
            success = metadata.get("success", False)
            
<<<<<<< HEAD
            if success and response_time < 1000:
                preferences["success_patterns"].append("fast_response")
            elif success and response_time > 5000:
                preferences["success_patterns"].append("quality_over_speed")
=======
            if response_time > 0:
                total_response_time += response_time
                response_count += 1
            
            if success:
                if response_time < 1000:
                    preferences["success_patterns"].append("fast_response")
                elif response_time > 5000:
                    preferences["success_patterns"].append("quality_over_speed")
                else:
                    preferences["success_patterns"].append("balanced_response")
        
        # 计算平均响应时间
        if response_count > 0:
            preferences["avg_response_time"] = total_response_time / response_count
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        
        # 确定性能偏好
        fast_success = preferences["success_patterns"].count("fast_response")
        quality_success = preferences["success_patterns"].count("quality_over_speed")
<<<<<<< HEAD
        
        if fast_success > quality_success * 2:
            preferences["performance_preference"] = "fast"
        elif quality_success > fast_success:
            preferences["performance_preference"] = "quality"
=======
        balanced_success = preferences["success_patterns"].count("balanced_response")
        
        if fast_success > max(quality_success, balanced_success):
            preferences["performance_preference"] = "fast"
        elif quality_success > max(fast_success, balanced_success):
            preferences["performance_preference"] = "quality"
        else:
            preferences["performance_preference"] = "balanced"
        
        # 缓存结果
        self.user_profiles[cache_key] = (time.time(), preferences)
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        
        return preferences
    
    def _generate_routing_recommendation(self, request: Dict, preferences: Dict, memory: List[Dict]) -> Dict:
        """生成路由推荐"""
        recommendation = {
            "primary_mcp": None,
            "fallback_mcps": [],
            "confidence": 0.5,
<<<<<<< HEAD
            "reasoning": []
=======
            "reasoning": [],
            "estimated_response_time": 0,
            "quality_expectation": 0.7
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        }
        
        # 基于用户偏好推荐
        preferred_mcps = preferences.get("preferred_mcps", {})
        if preferred_mcps:
<<<<<<< HEAD
            # 按使用频率排序
=======
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
            sorted_mcps = sorted(preferred_mcps.items(), key=lambda x: x[1], reverse=True)
            recommendation["primary_mcp"] = sorted_mcps[0][0]
            recommendation["fallback_mcps"] = [mcp for mcp, _ in sorted_mcps[1:3]]
            recommendation["confidence"] += 0.2
            recommendation["reasoning"].append(f"基于用户历史偏好推荐 {recommendation['primary_mcp']}")
        
        # 基于性能偏好调整
        performance_pref = preferences.get("performance_preference", "balanced")
<<<<<<< HEAD
        if performance_pref == "fast":
            # 优先推荐本地MCP
            if "local_model_mcp" not in recommendation["fallback_mcps"]:
                recommendation["fallback_mcps"].insert(0, "local_model_mcp")
            recommendation["confidence"] += 0.1
            recommendation["reasoning"].append("用户偏好快速响应，优先推荐本地处理")
        elif performance_pref == "quality":
            # 优先推荐云端MCP
            if "cloud_search_mcp" not in recommendation["fallback_mcps"]:
                recommendation["fallback_mcps"].insert(0, "cloud_search_mcp")
            recommendation["confidence"] += 0.1
            recommendation["reasoning"].append("用户偏好高质量结果，优先推荐云端处理")
        
=======
        avg_response_time = preferences.get("avg_response_time", 0)
        
        if performance_pref == "fast":
            if "local_model_mcp" not in recommendation["fallback_mcps"]:
                recommendation["fallback_mcps"].insert(0, "local_model_mcp")
            recommendation["confidence"] += 0.15
            recommendation["estimated_response_time"] = min(avg_response_time, 2000)
            recommendation["reasoning"].append("用户偏好快速响应，优先推荐本地处理")
            
        elif performance_pref == "quality":
            if "cloud_search_mcp" not in recommendation["fallback_mcps"]:
                recommendation["fallback_mcps"].insert(0, "cloud_search_mcp")
            recommendation["confidence"] += 0.15
            recommendation["estimated_response_time"] = max(avg_response_time, 3000)
            recommendation["quality_expectation"] = 0.9
            recommendation["reasoning"].append("用户偏好高质量结果，优先推荐云端处理")
        
        # 基于内容类型推荐
        content_types = preferences.get("content_types", {})
        request_content = str(request.get("content", "")).lower()
        
        if "ocr" in request_content and "ocr" in content_types:
            if content_types["ocr"] > 3:  # 用户经常使用OCR
                recommendation["confidence"] += 0.1
                recommendation["reasoning"].append("基于用户OCR使用历史优化推荐")
        
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        # 基于相似历史请求推荐
        similar_memories = self._find_similar_requests(request, memory)
        if similar_memories:
            successful_mcps = [m.get("metadata", {}).get("mcp_type") for m in similar_memories 
                             if m.get("metadata", {}).get("success")]
            if successful_mcps:
                most_successful = max(set(successful_mcps), key=successful_mcps.count)
                if most_successful != recommendation["primary_mcp"]:
                    recommendation["fallback_mcps"].insert(0, most_successful)
                recommendation["confidence"] += 0.2
                recommendation["reasoning"].append(f"基于相似请求的成功经验推荐 {most_successful}")
        
<<<<<<< HEAD
=======
        # 确保confidence在合理范围内
        recommendation["confidence"] = min(0.95, max(0.3, recommendation["confidence"]))
        
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        return recommendation
    
    def _find_similar_requests(self, request: Dict, memory: List[Dict]) -> List[Dict]:
        """查找相似的历史请求"""
<<<<<<< HEAD
        # 简单的相似度计算
=======
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        request_content = request.get("content", "").lower()
        request_operation = request.get("operation", "").lower()
        
        similar_memories = []
        for memory_item in memory:
            memory_content = memory_item.get("content", "").lower()
            memory_operation = memory_item.get("metadata", {}).get("operation", "").lower()
            
<<<<<<< HEAD
            # 计算相似度
            similarity = 0
            if request_operation and request_operation == memory_operation:
                similarity += 0.5
            
            # 简单的内容相似度
            common_words = set(request_content.split()) & set(memory_content.split())
            if len(common_words) > 2:
                similarity += 0.3
            
            if similarity > 0.4:
                similar_memories.append(memory_item)
        
        return similar_memories[:5]  # 返回最多5个相似记忆
=======
            similarity = 0
            
            # 操作类型相似度
            if request_operation and request_operation == memory_operation:
                similarity += 0.4
            
            # 内容相似度
            request_words = set(request_content.split())
            memory_words = set(memory_content.split())
            common_words = request_words & memory_words
            
            if len(request_words) > 0:
                content_similarity = len(common_words) / len(request_words)
                similarity += content_similarity * 0.6
            
            if similarity > 0.3:
                similar_memories.append({
                    **memory_item,
                    "similarity_score": similarity
                })
        
        # 按相似度排序
        similar_memories.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_memories[:5]
    
    def _extract_memory_insights(self, memories: List[Dict]) -> Dict:
        """提取记忆洞察"""
        insights = {
            "total_memories": len(memories),
            "success_rate": 0,
            "common_patterns": [],
            "performance_trends": {},
            "content_distribution": {}
        }
        
        if not memories:
            return insights
        
        successful_count = 0
        performance_data = []
        content_types = {}
        
        for memory in memories:
            metadata = memory.get("metadata", {})
            
            if metadata.get("success"):
                successful_count += 1
            
            response_time = metadata.get("response_time", 0)
            if response_time > 0:
                performance_data.append(response_time)
            
            tags = metadata.get("tags", [])
            for tag in tags:
                if tag.startswith("content:"):
                    content_type = tag.split(":")[1]
                    content_types[content_type] = content_types.get(content_type, 0) + 1
        
        insights["success_rate"] = successful_count / len(memories)
        insights["content_distribution"] = content_types
        
        if performance_data:
            insights["performance_trends"] = {
                "avg_response_time": sum(performance_data) / len(performance_data),
                "min_response_time": min(performance_data),
                "max_response_time": max(performance_data)
            }
        
        return insights
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
```

## 🔧 整合实施步骤

### **步骤1: 扩展InteractionLogManager**

```python
class EnhancedInteractionLogManager(InteractionLogManager):
<<<<<<< HEAD
    """增强的交互日志管理器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.memory_manager = IntelligentMemoryManager(
            memory_mcp=UnifiedMemoryMCP(config.get("memory_config", {}))
        )
        self.memory_router = MemoryEnhancedRouter(self.memory_manager.memory_mcp)
=======
    """增强的交互日志管理器，集成记忆功能"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # 初始化记忆组件
        self.supermemory_adapter = SuperMemoryAdapter(
            api_key=config.get("supermemory_api_key"),
            server_url=config.get("supermemory_server_url")
        )
        
        self.unified_memory = UnifiedMemoryMCP(config.get("memory_config", {}))
        
        self.memory_manager = IntelligentMemoryManager(
            unified_memory_mcp=self.unified_memory,
            supermemory_adapter=self.supermemory_adapter
        )
        
        self.memory_router = MemoryEnhancedRouter(
            unified_memory_mcp=self.unified_memory,
            supermemory_adapter=self.supermemory_adapter
        )
        
        # 配置选项
        self.enable_memory_storage = config.get("enable_memory_storage", True)
        self.enable_memory_routing = config.get("enable_memory_routing", True)
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
    
    async def log_interaction(self, interaction_data: Dict) -> Dict:
        """记录交互并存储为记忆"""
        # 原有的日志记录
        log_result = await super().log_interaction(interaction_data)
        
<<<<<<< HEAD
        # 异步存储为记忆
        asyncio.create_task(
            self.memory_manager.process_interaction_data(interaction_data)
        )
=======
        # 异步存储为记忆（如果启用）
        if self.enable_memory_storage:
            asyncio.create_task(
                self.memory_manager.process_interaction_data(interaction_data)
            )
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
        
        return log_result
    
    async def get_routing_recommendation(self, request: Dict) -> Dict:
        """获取基于记忆的路由推荐"""
<<<<<<< HEAD
        return await self.memory_router.enhanced_route_decision(request)
=======
        if not self.enable_memory_routing:
            return {"status": "disabled", "message": "记忆路由功能未启用"}
        
        return await self.memory_router.enhanced_route_decision(request)
    
    async def get_memory_statistics(self) -> Dict:
        """获取记忆系统统计信息"""
        return {
            "memory_manager_stats": self.memory_manager.get_statistics(),
            "supermemory_health": self.supermemory_adapter.health_check(),
            "unified_memory_stats": await self.unified_memory.get_statistics()
        }
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
```

### **步骤2: 更新MCPCoordinator配置**

```toml
[mcp_coordinator]
enable_memory_integration = true
<<<<<<< HEAD
memory_storage_threshold = 0.8  # 成功率阈值
=======
enable_memory_storage = true
enable_memory_routing = true
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647

[memory_integration]
auto_memory_storage = true
memory_retention_days = 90
max_memories_per_user = 1000
<<<<<<< HEAD

[memory_sources]
local_enabled = true
rag_enabled = true
github_enabled = false
supermemory_enabled = false
```

### **步骤3: 创建Memory MCP适配器**

将unified_memory_mcp添加到我们的adapter目录：
=======
quality_threshold = 0.6

[supermemory]
api_key = "${SUPERMEMORY_API_KEY}"
server_url = "https://api.supermemory.ai/v1"
timeout = 30

[unified_memory]
enable_local = true
enable_rag = true
enable_github = false
enable_supermemory = true

[memory_routing]
cache_ttl = 3600
confidence_threshold = 0.7
max_similar_memories = 5
```

### **步骤3: 创建Memory MCP适配器目录**
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647

```
mcp/adapter/
├── local_model_mcp/
├── cloud_search_mcp/
<<<<<<< HEAD
└── unified_memory_mcp/     # 新增
    ├── unified_memory_mcp.py
    ├── memory_query_engine.py
    ├── config.toml
    └── README.md
=======
├── unified_memory_mcp/     # 新增
│   ├── unified_memory_mcp.py
│   ├── memory_query_engine.py
│   ├── supermemory_integration.py
│   ├── config.toml
│   ├── cli.py
│   └── README.md
└── supermemory_adapter/    # 引用现有的
    └── supermemory_mcp.py
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647
```

## 📊 预期效果

### **1. 智能化提升**
<<<<<<< HEAD
- 路由决策准确率提升30%
- 用户满意度提升25%
- 响应时间优化20%

### **2. 个性化体验**
- 基于历史的个性化推荐
- 自适应的性能优化
- 预测性的需求满足

### **3. 系统学习能力**
- 持续的性能优化
- 自动的错误模式识别
- 智能的资源分配

## 🚀 部署建议

### **渐进式部署**
1. **阶段1**: 部署Memory MCP适配器
2. **阶段2**: 启用交互数据到记忆的转换
3. **阶段3**: 启用基于记忆的路由增强
4. **阶段4**: 全面启用智能记忆系统

### **监控指标**
- 记忆存储成功率
- 路由推荐准确率
- 用户满意度变化
- 系统性能影响

这个整合方案将显著提升PowerAutomation系统的智能化水平和用户体验！
=======
- **路由决策准确率提升35%** - 基于历史记忆的智能推荐
- **用户满意度提升30%** - 个性化的服务体验
- **响应时间优化25%** - 基于用户偏好的性能优化

### **2. 个性化体验**
- **自适应推荐** - 基于用户历史行为的智能推荐
- **性能偏好学习** - 自动识别用户对速度vs质量的偏好
- **内容类型优化** - 针对用户常用功能的专项优化

### **3. 系统学习能力**
- **持续优化** - 基于交互数据的持续学习和改进
- **模式识别** - 自动识别成功和失败的模式
- **预测能力** - 基于历史数据预测用户需求

## 🚀 部署建议

### **渐进式部署策略**

#### **阶段1: 基础部署 (第1-2周)**
- 部署SuperMemory适配器
- 配置Unified Memory MCP
- 启用基础记忆存储功能
- 验证记忆存储和检索功能

#### **阶段2: 智能存储 (第3-4周)**
- 启用智能记忆转换
- 配置存储策略和质量评分
- 测试多源记忆存储
- 优化存储性能

#### **阶段3: 增强路由 (第5-6周)**
- 启用基于记忆的路由增强
- 配置用户偏好分析
- 测试路由推荐准确性
- 调优推荐算法

#### **阶段4: 全面优化 (第7-8周)**
- 启用完整的智能记忆系统
- 优化性能和资源使用
- 完善监控和告警
- 用户体验验证

### **监控指标**

#### **存储指标**
- 记忆存储成功率 (目标: >95%)
- 存储延迟 (目标: <100ms)
- 存储容量使用率
- 质量分数分布

#### **路由指标**
- 路由推荐准确率 (目标: >80%)
- 推荐置信度分布
- 用户接受率
- 路由决策延迟 (目标: <50ms)

#### **用户体验指标**
- 用户满意度评分
- 个性化推荐点击率
- 重复查询减少率
- 平均会话时长

### **风险控制**

#### **性能风险**
- 记忆存储异步化，避免阻塞主流程
- 设置存储队列大小限制
- 实现优雅降级机制

#### **数据风险**
- 实现数据备份和恢复机制
- 设置记忆数据生命周期管理
- 确保用户隐私保护

#### **系统风险**
- 保持向后兼容性
- 提供功能开关控制
- 实现完整的回滚方案

这个整合方案将显著提升PowerAutomation系统的智能化水平，为用户提供更加个性化和高效的服务体验！
>>>>>>> 2964a240aef572f0ac8f6da7f8da0533a8eed647

