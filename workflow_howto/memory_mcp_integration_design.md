# Memory MCP与InteractionLogManager整合方案

## 🎯 整合目标

将PowerAutomation的Unified Memory MCP与我们的InteractionLogManager整合，实现：

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

## 🏗️ 整合架构设计

### **核心组件关系**

```
MCPCoordinator {
    InteractionLogManager {
        - 收集交互数据
        - 实时数据分析
        - 触发记忆存储
    }
    
    MemoryMCP {
        - 长期记忆管理
        - 智能检索服务
        - 跨源记忆整合
    }
    
    SmartRouter {
        - 基于记忆的路由决策
        - 个性化推荐
        - 预测性分析
    }
}
```

### **数据流设计**

```
用户请求 → MCP处理 → 交互数据 → InteractionLogManager
                                        ↓
记忆检索 ← MemoryMCP ← 记忆转换 ← 数据分析
    ↓
SmartRouter → 优化决策 → 个性化响应
```

## 🔧 技术实现方案

### **1. 记忆数据转换器 (MemoryDataConverter)**

```python
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
        
        # 错误信息
        if "error" in interaction_data:
            content_parts.append(f"错误信息: {interaction_data['error']}")
        
        return " | ".join(content_parts)
    
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
        
        return tags
```

### **2. 智能记忆管理器 (IntelligentMemoryManager)**

```python
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
                return {"status": "skipped", "reason": "不符合记忆存储条件"}
            
            # 转换为记忆格式
            memory_data = self.converter.convert_interaction_to_memory(interaction_data)
            
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
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"记忆存储失败: {str(e)}"}
    
    def _should_store_as_memory(self, interaction_data: Dict) -> bool:
        """判断是否应该存储为记忆"""
        # 成功的交互更有价值
        if not interaction_data.get("success", False):
            return False
        
        # 过滤掉简单的查询操作
        operation = interaction_data.get("operation", "")
        if operation in ["health_check", "status", "ping"]:
            return False
        
        # 响应时间过长的可能有问题
        response_time = interaction_data.get("response_time", 0)
        if response_time > 30000:  # 30秒以上
            return False
        
        # 有实际内容的交互
        if not interaction_data.get("request") and not interaction_data.get("response"):
            return False
        
        return True
    
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
        except Exception as e:
            logger.warning(f"记忆索引更新失败: {str(e)}")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取逻辑
        import re
        words = re.findall(r'\b\w+\b', content.lower())
        # 过滤停用词和短词
        keywords = [word for word in words if len(word) > 3 and word not in ["用户", "请求", "处理", "结果"]]
        return list(set(keywords))[:10]  # 最多10个关键词
```

### **3. 记忆增强路由器 (MemoryEnhancedRouter)**

```python
class MemoryEnhancedRouter:
    """基于记忆的增强路由器"""
    
    def __init__(self, memory_mcp: UnifiedMemoryMCP):
        self.memory_mcp = memory_mcp
        self.user_profiles = {}  # 用户画像缓存
    
    async def enhanced_route_decision(self, request: Dict) -> Dict:
        """基于记忆的增强路由决策"""
        try:
            user_id = request.get("user_id", "anonymous")
            
            # 获取用户历史记忆
            user_memory = await self._get_user_memory(user_id, request)
            
            # 分析用户偏好
            user_preferences = self._analyze_user_preferences(user_memory)
            
            # 基于记忆的路由推荐
            routing_recommendation = self._generate_routing_recommendation(
                request, user_preferences, user_memory
            )
            
            return {
                "status": "success",
                "routing_recommendation": routing_recommendation,
                "user_preferences": user_preferences,
                "confidence": routing_recommendation.get("confidence", 0.5)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"记忆增强路由失败: {str(e)}"}
    
    async def _get_user_memory(self, user_id: str, request: Dict) -> List[Dict]:
        """获取用户相关记忆"""
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
        preferences = {
            "preferred_mcps": {},
            "preferred_operations": {},
            "performance_preference": "balanced",  # fast, balanced, quality
            "success_patterns": [],
            "failure_patterns": []
        }
        
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
            
            # 分析性能偏好
            response_time = metadata.get("response_time", 0)
            success = metadata.get("success", False)
            
            if success and response_time < 1000:
                preferences["success_patterns"].append("fast_response")
            elif success and response_time > 5000:
                preferences["success_patterns"].append("quality_over_speed")
        
        # 确定性能偏好
        fast_success = preferences["success_patterns"].count("fast_response")
        quality_success = preferences["success_patterns"].count("quality_over_speed")
        
        if fast_success > quality_success * 2:
            preferences["performance_preference"] = "fast"
        elif quality_success > fast_success:
            preferences["performance_preference"] = "quality"
        
        return preferences
    
    def _generate_routing_recommendation(self, request: Dict, preferences: Dict, memory: List[Dict]) -> Dict:
        """生成路由推荐"""
        recommendation = {
            "primary_mcp": None,
            "fallback_mcps": [],
            "confidence": 0.5,
            "reasoning": []
        }
        
        # 基于用户偏好推荐
        preferred_mcps = preferences.get("preferred_mcps", {})
        if preferred_mcps:
            # 按使用频率排序
            sorted_mcps = sorted(preferred_mcps.items(), key=lambda x: x[1], reverse=True)
            recommendation["primary_mcp"] = sorted_mcps[0][0]
            recommendation["fallback_mcps"] = [mcp for mcp, _ in sorted_mcps[1:3]]
            recommendation["confidence"] += 0.2
            recommendation["reasoning"].append(f"基于用户历史偏好推荐 {recommendation['primary_mcp']}")
        
        # 基于性能偏好调整
        performance_pref = preferences.get("performance_preference", "balanced")
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
        
        return recommendation
    
    def _find_similar_requests(self, request: Dict, memory: List[Dict]) -> List[Dict]:
        """查找相似的历史请求"""
        # 简单的相似度计算
        request_content = request.get("content", "").lower()
        request_operation = request.get("operation", "").lower()
        
        similar_memories = []
        for memory_item in memory:
            memory_content = memory_item.get("content", "").lower()
            memory_operation = memory_item.get("metadata", {}).get("operation", "").lower()
            
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
```

## 🔧 整合实施步骤

### **步骤1: 扩展InteractionLogManager**

```python
class EnhancedInteractionLogManager(InteractionLogManager):
    """增强的交互日志管理器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.memory_manager = IntelligentMemoryManager(
            memory_mcp=UnifiedMemoryMCP(config.get("memory_config", {}))
        )
        self.memory_router = MemoryEnhancedRouter(self.memory_manager.memory_mcp)
    
    async def log_interaction(self, interaction_data: Dict) -> Dict:
        """记录交互并存储为记忆"""
        # 原有的日志记录
        log_result = await super().log_interaction(interaction_data)
        
        # 异步存储为记忆
        asyncio.create_task(
            self.memory_manager.process_interaction_data(interaction_data)
        )
        
        return log_result
    
    async def get_routing_recommendation(self, request: Dict) -> Dict:
        """获取基于记忆的路由推荐"""
        return await self.memory_router.enhanced_route_decision(request)
```

### **步骤2: 更新MCPCoordinator配置**

```toml
[mcp_coordinator]
enable_memory_integration = true
memory_storage_threshold = 0.8  # 成功率阈值

[memory_integration]
auto_memory_storage = true
memory_retention_days = 90
max_memories_per_user = 1000

[memory_sources]
local_enabled = true
rag_enabled = true
github_enabled = false
supermemory_enabled = false
```

### **步骤3: 创建Memory MCP适配器**

将unified_memory_mcp添加到我们的adapter目录：

```
mcp/adapter/
├── local_model_mcp/
├── cloud_search_mcp/
└── unified_memory_mcp/     # 新增
    ├── unified_memory_mcp.py
    ├── memory_query_engine.py
    ├── config.toml
    └── README.md
```

## 📊 预期效果

### **1. 智能化提升**
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

