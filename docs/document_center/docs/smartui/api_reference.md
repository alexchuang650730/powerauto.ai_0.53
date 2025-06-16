# SmartUI MCP API 参考文档

## 🔌 API 概述

SmartUI MCP提供两套API接口：
- **主UI服务API** (端口5001): 用户界面相关接口
- **MCP组件API** (端口8090): MCP协议标准接口

## 🌐 主UI服务API (端口5001)

### 基础接口

#### GET /
获取主界面HTML页面
```bash
curl http://localhost:5001/
```

#### GET /api/status
获取主UI服务状态
```bash
curl http://localhost:5001/api/status
```

#### GET /api/mcp/status
获取MCP组件状态（代理接口）
```bash
curl http://localhost:5001/api/mcp/status
```

### 系统监控接口

#### GET /api/system/resources
获取系统资源使用情况
```bash
curl http://localhost:5001/api/system/resources
```

响应示例：
```json
{
  "cpu_usage": "15%",
  "memory_usage": "2.1GB",
  "disk_usage": "85%",
  "network_status": "正常"
}
```

#### GET /api/system/health
获取系统健康状态
```bash
curl http://localhost:5001/api/system/health
```

### 飞书集成接口

#### GET /api/feishu/status
获取飞书连接状态
```bash
curl http://localhost:5001/api/feishu/status
```

#### POST /api/feishu/notify
发送飞书通知
```bash
curl -X POST http://localhost:5001/api/feishu/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "测试通知", "type": "info"}'
```

### GitHub集成接口

#### GET /api/github/status
获取GitHub同步状态
```bash
curl http://localhost:5001/api/github/status
```

#### POST /api/github/sync
触发GitHub同步
```bash
curl -X POST http://localhost:5001/api/github/sync
```

## 🔧 MCP组件API (端口8090)

### 标准MCP接口

#### GET /api/status
获取MCP组件状态
```bash
curl http://localhost:8090/api/status
```

响应示例：
```json
{
  "success": true,
  "data": {
    "name": "Smart UI MCP",
    "version": "1.0.0",
    "status": "running",
    "port": 8090,
    "capabilities": ["ui_management", "session_management"]
  }
}
```

#### GET /api/capabilities
获取MCP组件能力列表
```bash
curl http://localhost:8090/api/capabilities
```

#### GET /api/health
获取MCP组件健康状态
```bash
curl http://localhost:8090/api/health
```

### UI管理接口

#### GET /api/ui/components
获取UI组件列表
```bash
curl http://localhost:8090/api/ui/components
```

#### POST /api/ui/render
渲染UI组件
```bash
curl -X POST http://localhost:8090/api/ui/render \
  -H "Content-Type: application/json" \
  -d '{"component": "dashboard", "params": {}}'
```

### 会话管理接口

#### GET /api/sessions
获取活跃会话列表
```bash
curl http://localhost:8090/api/sessions
```

#### POST /api/sessions
创建新会话
```bash
curl -X POST http://localhost:8090/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "session_type": "web"}'
```

#### DELETE /api/sessions/{session_id}
删除会话
```bash
curl -X DELETE http://localhost:8090/api/sessions/session123
```

## 🔐 认证与授权

### API密钥认证
某些接口需要API密钥认证：
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:5001/api/protected/endpoint
```

### 会话认证
Web界面使用会话认证：
```bash
curl -b "session_id=your_session_id" \
  http://localhost:5001/api/user/profile
```

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "timestamp": "2025-06-16T04:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  },
  "timestamp": "2025-06-16T04:30:00Z"
}
```

## 🚨 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| INTERNAL_ERROR | 500 | 内部服务器错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

## 📝 使用示例

### 获取完整系统状态
```bash
#!/bin/bash

echo "=== SmartUI系统状态检查 ==="

# 检查主UI服务
echo "1. 主UI服务状态:"
curl -s http://localhost:5001/api/status | jq .

# 检查MCP组件
echo "2. MCP组件状态:"
curl -s http://localhost:8090/api/status | jq .

# 检查系统资源
echo "3. 系统资源:"
curl -s http://localhost:5001/api/system/resources | jq .

# 检查MCP协调器
echo "4. MCP协调器状态:"
curl -s http://localhost:8089/api/mcp/status | jq .
```

### 发送测试通知
```bash
#!/bin/bash

# 发送飞书测试通知
curl -X POST http://localhost:5001/api/feishu/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SmartUI系统运行正常",
    "type": "success",
    "timestamp": "'$(date -Iseconds)'"
  }'
```

## 🔄 Webhook接口

### GitHub Webhook
接收GitHub事件通知：
```
POST /api/webhooks/github
Content-Type: application/json
X-GitHub-Event: push

{
  "ref": "refs/heads/main",
  "commits": [...],
  "repository": {...}
}
```

### 飞书Webhook
接收飞书事件通知：
```
POST /api/webhooks/feishu
Content-Type: application/json

{
  "type": "message",
  "data": {...}
}
```

## 📚 SDK和工具

### Python SDK示例
```python
import requests

class SmartUIClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def get_status(self):
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()
    
    def send_notification(self, message, type="info"):
        data = {"message": message, "type": type}
        response = requests.post(
            f"{self.base_url}/api/feishu/notify",
            json=data
        )
        return response.json()

# 使用示例
client = SmartUIClient()
status = client.get_status()
print(f"服务状态: {status}")
```

---

*API文档版本: v1.0.0*
*最后更新: 2025年6月16日*

