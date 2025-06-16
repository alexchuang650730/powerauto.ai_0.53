# InteractionLogManager数据传递方案设计

## 🎯 方案概述

设计MCP与MCPCoordinator之间的交互数据传递机制，确保高效、可靠、可扩展的数据收集和管理。

## 📋 方案对比

### **方案1: HTTP API + 异步队列 (推荐)**

#### **架构设计**
```
MCP → HTTP POST → MCPCoordinator API → 内存队列 → InteractionLogManager → 数据库
```

#### **优势**
- ✅ 简单易实现，标准HTTP协议
- ✅ 异步处理，不阻塞MCP业务逻辑
- ✅ 支持重试和错误处理
- ✅ 易于监控和调试
- ✅ 向后兼容，现有MCP可选择性接入

#### **实现细节**
```python
# MCP端实现
class MCPDataReporter:
    def __init__(self, coordinator_url, api_key):
        self.coordinator_url = coordinator_url
        self.api_key = api_key
        self.session = requests.Session()
    
    async def report_interaction(self, interaction_data):
        try:
            response = await self.session.post(
                f"{self.coordinator_url}/api/v2/interactions",
                json=interaction_data,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            # 失败时存储到本地队列，稍后重试
            self.store_for_retry(interaction_data)
            return False

# MCPCoordinator端实现
class InteractionAPI:
    def __init__(self, interaction_log_manager):
        self.log_manager = interaction_log_manager
        self.queue = asyncio.Queue(maxsize=10000)
        
    async def receive_interaction(self, request):
        # 快速接收，放入队列
        await self.queue.put(request.json)
        return {"status": "accepted"}
    
    async def process_queue(self):
        # 后台处理队列中的数据
        while True:
            data = await self.queue.get()
            await self.log_manager.store_interaction(data)
```

---

### **方案2: 消息队列 (Redis Streams)**

#### **架构设计**
```
MCP → Redis Stream → MCPCoordinator Consumer → InteractionLogManager → 数据库
```

#### **优势**
- ✅ 高性能，支持大量并发
- ✅ 自动持久化和重试
- ✅ 支持消费者组和负载均衡
- ✅ 内置消息确认机制

#### **实现细节**
```python
# MCP端实现
class RedisDataReporter:
    def __init__(self, redis_url, stream_name):
        self.redis = redis.Redis.from_url(redis_url)
        self.stream_name = stream_name
    
    async def report_interaction(self, interaction_data):
        try:
            message_id = await self.redis.xadd(
                self.stream_name,
                interaction_data,
                maxlen=100000  # 限制stream大小
            )
            return message_id
        except Exception as e:
            # 本地缓存，稍后重试
            return None

# MCPCoordinator端实现
class RedisInteractionConsumer:
    def __init__(self, redis_url, stream_name, consumer_group):
        self.redis = redis.Redis.from_url(redis_url)
        self.stream_name = stream_name
        self.consumer_group = consumer_group
        
    async def consume_interactions(self):
        while True:
            messages = await self.redis.xreadgroup(
                self.consumer_group,
                "coordinator-1",
                {self.stream_name: ">"},
                count=100,
                block=1000
            )
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    await self.process_interaction(fields)
                    await self.redis.xack(self.stream_name, self.consumer_group, msg_id)
```

---

### **方案3: 共享数据库 + 轮询**

#### **架构设计**
```
MCP → 直接写入数据库 → MCPCoordinator轮询 → InteractionLogManager处理
```

#### **优势**
- ✅ 实现简单，无需额外组件
- ✅ 数据一致性强
- ✅ 支持事务处理
- ✅ 易于查询和分析

#### **实现细节**
```python
# 共享数据表结构
CREATE TABLE interaction_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    mcp_id VARCHAR(100) NOT NULL,
    interaction_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSON NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    INDEX idx_mcp_timestamp (mcp_id, timestamp),
    INDEX idx_processed (processed)
);

# MCP端实现
class DatabaseReporter:
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def report_interaction(self, interaction_data):
        try:
            await self.db.execute(
                "INSERT INTO interaction_logs (mcp_id, interaction_id, data) VALUES (?, ?, ?)",
                (self.mcp_id, interaction_data['interaction_id'], json.dumps(interaction_data))
            )
            return True
        except Exception as e:
            return False

# MCPCoordinator端实现
class DatabasePoller:
    def __init__(self, db_connection, poll_interval=5):
        self.db = db_connection
        self.poll_interval = poll_interval
    
    async def poll_interactions(self):
        while True:
            rows = await self.db.fetch_all(
                "SELECT * FROM interaction_logs WHERE processed = FALSE ORDER BY timestamp LIMIT 1000"
            )
            
            for row in rows:
                await self.process_interaction(row)
                await self.db.execute(
                    "UPDATE interaction_logs SET processed = TRUE WHERE id = ?",
                    (row['id'],)
                )
            
            await asyncio.sleep(self.poll_interval)
```

---

### **方案4: gRPC双向流 (高级方案)**

#### **架构设计**
```
MCP ←→ gRPC双向流 ←→ MCPCoordinator ←→ InteractionLogManager
```

#### **优势**
- ✅ 低延迟，高性能
- ✅ 双向通信，支持实时反馈
- ✅ 强类型，自动序列化
- ✅ 支持流式处理

#### **实现细节**
```protobuf
// interaction.proto
service InteractionService {
    rpc StreamInteractions(stream InteractionData) returns (stream InteractionResponse);
}

message InteractionData {
    string mcp_id = 1;
    string interaction_id = 2;
    int64 timestamp = 3;
    google.protobuf.Any data = 4;
}

message InteractionResponse {
    string interaction_id = 1;
    bool success = 2;
    string message = 3;
}
```

```python
# MCP端实现
class GRPCReporter:
    def __init__(self, coordinator_address):
        self.channel = grpc.aio.insecure_channel(coordinator_address)
        self.stub = InteractionServiceStub(self.channel)
        
    async def start_streaming(self):
        async def request_generator():
            while True:
                interaction = await self.interaction_queue.get()
                yield InteractionData(**interaction)
        
        async for response in self.stub.StreamInteractions(request_generator()):
            if not response.success:
                # 处理失败情况
                await self.handle_failure(response)
```

---

## 📊 方案对比表

| 特性 | HTTP API | Redis Streams | 共享数据库 | gRPC双向流 |
|------|----------|---------------|------------|------------|
| **实现复杂度** | 简单 | 中等 | 简单 | 复杂 |
| **性能** | 中等 | 高 | 低 | 很高 |
| **可靠性** | 高 | 很高 | 很高 | 高 |
| **扩展性** | 好 | 很好 | 差 | 很好 |
| **运维复杂度** | 低 | 中等 | 低 | 高 |
| **实时性** | 中等 | 高 | 低 | 很高 |
| **向后兼容** | 很好 | 好 | 很好 | 中等 |

## 🎯 推荐方案

### **阶段1: HTTP API + 异步队列**
- 适合快速实现和部署
- 向后兼容性最好
- 运维成本最低

### **阶段2: Redis Streams (可选升级)**
- 当数据量增大时升级
- 保持API兼容性
- 提升性能和可靠性

### **阶段3: gRPC双向流 (未来考虑)**
- 当需要实时反馈时考虑
- 适合高性能场景
- 需要更多开发和运维投入

## 🔧 混合方案 (最佳实践)

```python
class HybridInteractionManager:
    def __init__(self):
        # 支持多种传输方式
        self.http_api = HTTPInteractionAPI()
        self.redis_streams = RedisInteractionStreams()
        self.database_fallback = DatabaseFallback()
    
    async def receive_interaction(self, data, transport_type="auto"):
        if transport_type == "auto":
            # 自动选择最佳传输方式
            if self.redis_streams.is_available():
                return await self.redis_streams.send(data)
            else:
                return await self.http_api.send(data)
        elif transport_type == "http":
            return await self.http_api.send(data)
        elif transport_type == "redis":
            return await self.redis_streams.send(data)
        else:
            # 降级到数据库
            return await self.database_fallback.send(data)
```

## 🤔 您的选择？

请告诉我您倾向于哪个方案，我将据此创建详细的实现文档：

1. **方案1 (HTTP API)** - 简单可靠，快速实现
2. **方案2 (Redis Streams)** - 高性能，适合大规模
3. **方案3 (共享数据库)** - 最简单，适合小规模
4. **方案4 (gRPC)** - 高性能，适合实时场景
5. **混合方案** - 支持多种方式，最大灵活性

