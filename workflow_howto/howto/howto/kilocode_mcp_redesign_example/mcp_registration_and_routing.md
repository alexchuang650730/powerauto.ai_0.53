# KiloCode MCP 注册与智能路由机制

## 🎯 核心问题解答

### 1. 统一注册时是跟谁注册？

#### **注册对象：MCP Coordinator (协调器)**
```
所有MCP → 注册到 → MCP Coordinator
```

#### **注册流程**
```python
# 1. MCP启动时自动注册
class KiloCodeMCP:
    def __init__(self, coordinator_client=None):
        self.coordinator = coordinator_client
        # 启动时向coordinator注册自己
        await self._register_to_coordinator()
    
    async def _register_to_coordinator(self):
        registration_info = {
            "mcp_id": "kilocode_mcp",
            "mcp_type": "fallback_creator",
            "capabilities": self._get_capabilities(),
            "priority": "fallback",  # 兜底优先级
            "status": "active"
        }
        await self.coordinator.register_mcp(registration_info)
```

#### **Coordinator的作用**
- **中央注册表**：维护所有MCP的注册信息
- **路由决策**：根据请求选择合适的MCP
- **负载均衡**：分配请求到不同MCP
- **健康检查**：监控MCP状态

### 2. kilocode_mcp注册了什么？

#### **注册信息结构**
```json
{
  "mcp_id": "kilocode_mcp",
  "mcp_name": "KiloCode兜底创建引擎",
  "mcp_type": "fallback_creator",
  "version": "2.0.0",
  "capabilities": {
    "supported_workflows": [
      "requirements_analysis",
      "architecture_design", 
      "coding_implementation",
      "testing_verification",
      "deployment_release",
      "monitoring_operations"
    ],
    "supported_creation_types": [
      "document",
      "code", 
      "prototype",
      "tool"
    ],
    "supported_languages": [
      "python",
      "javascript",
      "html",
      "css",
      "bash"
    ],
    "special_abilities": [
      "snake_game_generation",
      "ppt_creation",
      "fallback_solution"
    ]
  },
  "priority_level": "fallback",
  "routing_conditions": {
    "trigger_when": "all_other_mcps_failed",
    "workflow_support": "universal",
    "creation_focus": "code_and_document"
  },
  "performance_metrics": {
    "avg_response_time": "2-5秒",
    "success_rate": "95%",
    "complexity_handling": "medium_to_high"
  },
  "endpoint": "http://localhost:8080/mcp/kilocode",
  "health_check": "http://localhost:8080/mcp/kilocode/health",
  "status": "active",
  "last_heartbeat": "2025-06-15T08:50:00Z"
}
```

#### **关键注册字段说明**

##### **mcp_type: "fallback_creator"**
- 标识这是一个兜底创建器
- Coordinator知道这是最后调用的MCP

##### **priority_level: "fallback"**
- 优先级设为兜底级别
- 只有在其他MCP都失败时才调用

##### **routing_conditions**
- **trigger_when**: "all_other_mcps_failed" - 触发条件
- **workflow_support**: "universal" - 支持所有工作流
- **creation_focus**: "code_and_document" - 专注代码和文档创建

##### **capabilities**
- 详细列出支持的工作流、创建类型、编程语言
- Coordinator用于匹配请求需求

### 3. 智能路由选取kilocode_mcp的逻辑

#### **路由决策流程**
```
用户请求 → Coordinator → 路由算法 → MCP选择
```

#### **详细路由逻辑**

##### **第一阶段：工作流路由**
```python
class MCPCoordinator:
    async def route_request(self, request):
        workflow_type = self._detect_workflow(request)
        
        # 1. 优先选择专用工作流MCP
        primary_mcp = self._get_workflow_mcp(workflow_type)
        if primary_mcp and primary_mcp.is_available():
            result = await primary_mcp.process(request)
            if result.success:
                return result
        
        # 2. 尝试工作流内的专用工具
        tools = self._get_workflow_tools(workflow_type)
        for tool in tools:
            if tool.can_handle(request):
                result = await tool.process(request)
                if result.success:
                    return result
        
        # 3. 调用smart_tool_engine_mcp创建工具
        smart_engine = self._get_mcp("smart_tool_engine_mcp")
        if smart_engine:
            result = await smart_engine.create_tool(request)
            if result.success:
                return result
        
        # 4. 最后兜底：kilocode_mcp
        return await self._fallback_to_kilocode(request)
```

##### **第二阶段：kilocode_mcp选择逻辑**
```python
async def _fallback_to_kilocode(self, request):
    """兜底到kilocode_mcp的逻辑"""
    
    # 1. 检查kilocode_mcp是否可用
    kilocode = self._get_mcp("kilocode_mcp")
    if not kilocode or not kilocode.is_healthy():
        return self._create_error_response("所有MCP都不可用")
    
    # 2. 检查kilocode_mcp是否支持该工作流
    workflow_type = request.get("workflow_type")
    if workflow_type not in kilocode.capabilities["supported_workflows"]:
        return self._create_error_response(f"不支持的工作流: {workflow_type}")
    
    # 3. 添加兜底上下文
    request["context"]["is_fallback"] = True
    request["context"]["failed_mcps"] = self._get_failed_mcps_list()
    request["context"]["fallback_reason"] = "所有专用MCP都无法处理该请求"
    
    # 4. 调用kilocode_mcp
    return await kilocode.process_request(request)
```

#### **智能路由的判断条件**

##### **条件1：专用MCP失败**
```python
# 示例：PPT生成请求
request = "为华为终端业务创建年终汇报PPT"

# 路由尝试顺序：
# 1. requirements_analysis_mcp → 失败
# 2. ppt_generator_tool → 不存在
# 3. smart_tool_engine_mcp → 创建失败
# 4. kilocode_mcp → 兜底创建PPT
```

##### **条件2：复杂创建需求**
```python
# 示例：贪吃蛇游戏请求
request = "开发一个完整的贪吃蛇游戏"

# 路由尝试顺序：
# 1. coding_implementation_mcp → 无游戏开发能力
# 2. game_dev_tool → 不存在
# 3. smart_tool_engine_mcp → 无法创建游戏工具
# 4. kilocode_mcp → 兜底生成完整游戏代码
```

##### **条件3：跨工作流需求**
```python
# 示例：既要PPT又要代码的复合需求
request = "创建项目展示PPT并生成演示代码"

# 路由逻辑：
# 1. 检测到跨工作流需求
# 2. 单个专用MCP无法完全处理
# 3. 直接路由到kilocode_mcp
# 4. kilocode_mcp根据工作流上下文分别创建
```

#### **路由权重算法**
```python
def calculate_mcp_score(mcp, request):
    """计算MCP处理请求的适合度分数"""
    score = 0
    
    # 1. 工作流匹配度 (40%)
    if request.workflow_type in mcp.supported_workflows:
        score += 40
    
    # 2. 创建类型匹配度 (30%)
    if request.creation_type in mcp.supported_creation_types:
        score += 30
    
    # 3. 历史成功率 (20%)
    score += mcp.success_rate * 0.2
    
    # 4. 当前负载 (10%)
    score += (1 - mcp.current_load) * 10
    
    # 5. 特殊能力加分
    if hasattr(mcp, 'special_abilities'):
        for ability in mcp.special_abilities:
            if ability in request.content.lower():
                score += 15
    
    return score

# kilocode_mcp的特殊处理
if mcp.mcp_type == "fallback_creator":
    # 兜底MCP只有在其他都失败时才获得高分
    if all_other_mcps_failed:
        score = 100  # 最高分，确保被选中
    else:
        score = 0    # 最低分，避免被优先选择
```

### 4. 注册表管理

#### **Coordinator维护的注册表**
```python
class MCPRegistry:
    def __init__(self):
        self.mcps = {
            "requirements_analysis_mcp": {
                "type": "workflow_primary",
                "priority": "high",
                "workflows": ["requirements_analysis"]
            },
            "coding_implementation_mcp": {
                "type": "workflow_primary", 
                "priority": "high",
                "workflows": ["coding_implementation"]
            },
            "kilocode_mcp": {
                "type": "fallback_creator",
                "priority": "fallback",
                "workflows": ["*"]  # 支持所有工作流
            },
            "gemini_mcp": {
                "type": "ai_assistant",
                "priority": "medium",
                "workflows": ["*"]
            }
        }
    
    def get_routing_order(self, workflow_type):
        """获取路由顺序"""
        return [
            # 1. 专用工作流MCP
            self._get_workflow_primary(workflow_type),
            # 2. AI助手MCP
            self._get_ai_assistants(),
            # 3. 智能工具引擎
            self._get_tool_engines(),
            # 4. 兜底创建器
            self._get_fallback_creators()
        ]
```

### 5. 健康检查与故障转移

#### **健康检查机制**
```python
class MCPHealthChecker:
    async def check_mcp_health(self, mcp_id):
        """检查MCP健康状态"""
        mcp = self.registry.get_mcp(mcp_id)
        
        try:
            # 1. 心跳检查
            response = await mcp.ping()
            if not response.ok:
                return False
            
            # 2. 功能检查
            test_request = self._create_test_request()
            result = await mcp.process_request(test_request)
            
            # 3. 更新状态
            mcp.last_health_check = datetime.now()
            mcp.health_status = "healthy" if result.success else "degraded"
            
            return result.success
            
        except Exception as e:
            mcp.health_status = "unhealthy"
            return False
```

#### **故障转移逻辑**
```python
async def handle_mcp_failure(self, failed_mcp_id, request):
    """处理MCP失败的故障转移"""
    
    # 1. 标记失败的MCP
    self.registry.mark_failed(failed_mcp_id)
    
    # 2. 获取备选MCP列表
    alternatives = self.registry.get_alternatives(failed_mcp_id)
    
    # 3. 尝试备选方案
    for alt_mcp in alternatives:
        if alt_mcp.is_healthy():
            try:
                return await alt_mcp.process_request(request)
            except Exception:
                continue
    
    # 4. 最后兜底到kilocode_mcp
    kilocode = self.registry.get_mcp("kilocode_mcp")
    if kilocode and kilocode.is_healthy():
        request["context"]["fallback_reason"] = f"主要MCP {failed_mcp_id} 失败"
        return await kilocode.process_request(request)
    
    # 5. 所有MCP都失败
    return self._create_system_error_response()
```

## 🎯 总结

### **注册机制**
- **注册对象**：MCP Coordinator
- **注册内容**：能力、优先级、路由条件、健康状态
- **注册时机**：MCP启动时自动注册

### **kilocode_mcp的特殊地位**
- **类型**：fallback_creator (兜底创建器)
- **优先级**：fallback (最低，只在其他失败时调用)
- **能力**：universal (支持所有工作流的创建需求)

### **智能路由逻辑**
1. **专用MCP优先**：先尝试工作流专用MCP
2. **工具搜索**：寻找专用工具
3. **智能创建**：smart_tool_engine_mcp创建工具
4. **兜底创建**：kilocode_mcp最后兜底

### **选择kilocode_mcp的条件**
- 所有专用MCP都失败
- 需要跨工作流创建能力
- 需要复杂的代码生成
- 需要文档和代码混合创建

这样的设计确保了kilocode_mcp真正发挥"兜底"作用，在系统的最后一道防线提供创建能力。

