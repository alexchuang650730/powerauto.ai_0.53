# PowerAutomation 组件文档模板

## 🎯 **[组件名称] MCP**

### **基本信息**
- **组件名称**: [组件名称] MCP
- **版本**: v1.0.0
- **类型**: [Adapter/Engine/Workflow]
- **端口**: [端口号]
- **位置**: `mcp/[类型]/[组件名称]_mcp/`

## 📋 **功能概述**

[详细描述组件的核心功能、作用和在整个系统中的位置]

## 🏗️ **架构设计**

### **组件结构**
```
[组件名称]_mcp/
├── [组件名称]_mcp.py          # 主要实现文件
├── config/                    # 配置文件目录
│   ├── settings.yaml
│   └── routes.yaml
├── utils/                     # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── tests/                     # 测试文件
│   ├── test_[组件名称].py
│   └── test_integration.py
├── docs/                      # 组件文档
│   ├── README.md
│   ├── api_reference.md
│   └── quick_start.md
└── requirements.txt           # 依赖包列表
```

### **核心模块**
- **[模块1]**: [功能描述]
- **[模块2]**: [功能描述]
- **[模块3]**: [功能描述]

## 🔧 **配置说明**

### **环境变量**
```bash
export [组件名称]_PORT=[端口号]
export [组件名称]_CONFIG_PATH=./config/settings.yaml
```

### **配置文件 (settings.yaml)**
```yaml
component:
  name: "[组件名称]_mcp"
  version: "1.0.0"
  port: [端口号]
  
settings:
  debug: false
  log_level: "INFO"
  max_connections: 100
  
features:
  feature1: true
  feature2: false
```

## 🚀 **快速开始**

### **1. 环境准备**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### **2. 配置设置**
```bash
# 复制配置模板
cp config/settings.yaml.template config/settings.yaml

# 编辑配置文件
nano config/settings.yaml
```

### **3. 启动服务**
```bash
# 开发模式
python [组件名称]_mcp.py --dev

# 生产模式
python [组件名称]_mcp.py --prod
```

### **4. 验证运行**
```bash
# 健康检查
curl http://localhost:[端口号]/health

# 功能测试
curl -X POST http://localhost:[端口号]/[功能端点] \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
```

## 📖 **API参考**

### **基础端点**

#### **健康检查**
- **URL**: `GET /health`
- **描述**: 检查组件运行状态
- **响应**:
```json
{
  "status": "running",
  "name": "[组件名称] MCP",
  "version": "1.0.0",
  "timestamp": "2025-06-16T10:00:00Z"
}
```

#### **组件信息**
- **URL**: `GET /info`
- **描述**: 获取组件详细信息
- **响应**:
```json
{
  "name": "[组件名称] MCP",
  "version": "1.0.0",
  "description": "[组件描述]",
  "capabilities": ["capability1", "capability2"],
  "endpoints": ["/health", "/info", "/[功能端点]"]
}
```

### **功能端点**

#### **[主要功能1]**
- **URL**: `POST /[功能端点1]`
- **描述**: [功能描述]
- **请求体**:
```json
{
  "input": "[输入数据]",
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```
- **响应**:
```json
{
  "success": true,
  "result": "[处理结果]",
  "metadata": {
    "processing_time": 0.05,
    "timestamp": "2025-06-16T10:00:00Z"
  }
}
```

#### **[主要功能2]**
- **URL**: `POST /[功能端点2]`
- **描述**: [功能描述]
- **请求体**: [请求格式]
- **响应**: [响应格式]

## 🔍 **使用示例**

### **Python客户端**
```python
import requests
import json

class [组件名称]Client:
    def __init__(self, base_url="http://localhost:[端口号]"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def [功能方法](self, input_data, options=None):
        payload = {
            "input": input_data,
            "options": options or {}
        }
        response = requests.post(
            f"{self.base_url}/[功能端点]",
            json=payload
        )
        return response.json()

# 使用示例
client = [组件名称]Client()
result = client.[功能方法]("测试数据")
print(result)
```

### **cURL示例**
```bash
# 基本功能调用
curl -X POST http://localhost:[端口号]/[功能端点] \
     -H "Content-Type: application/json" \
     -d '{
       "input": "测试数据",
       "options": {
         "option1": "value1"
       }
     }'
```

## 🧪 **测试**

### **运行测试**
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_[组件名称].py

# 运行集成测试
python -m pytest tests/test_integration.py -v
```

### **测试覆盖率**
```bash
# 生成覆盖率报告
python -m pytest --cov=[组件名称]_mcp tests/
```

## 🛠️ **故障排除**

### **常见问题**

#### **问题1: 服务启动失败**
- **症状**: [错误描述]
- **原因**: [可能原因]
- **解决方案**: 
  1. [解决步骤1]
  2. [解决步骤2]

#### **问题2: API响应错误**
- **症状**: [错误描述]
- **原因**: [可能原因]
- **解决方案**: [解决步骤]

### **日志分析**
```bash
# 查看实时日志
tail -f logs/[组件名称]_mcp.log

# 搜索错误日志
grep "ERROR" logs/[组件名称]_mcp.log
```

## 📊 **性能指标**

### **基准测试结果**
- **响应时间**: 平均 [时间]ms
- **吞吐量**: [数量] 请求/秒
- **内存使用**: 平均 [大小]MB
- **CPU使用**: 平均 [百分比]%

### **性能优化建议**
1. **[优化建议1]**: [具体说明]
2. **[优化建议2]**: [具体说明]

## 🔗 **集成指南**

### **与其他MCP组件集成**
- **MCP Coordinator**: [集成说明]
- **[相关组件1]**: [集成说明]
- **[相关组件2]**: [集成说明]

### **外部系统集成**
- **数据库**: [集成方法]
- **消息队列**: [集成方法]
- **监控系统**: [集成方法]

## 📈 **版本历史**

### **v1.0.0** (2025-06-16)
- ✅ 初始版本发布
- ✅ 核心功能实现
- ✅ API接口完成
- ✅ 文档编写完成

## 🔗 **相关文档**

- [MCP架构设计文档](../architecture/)
- [工作流集成指南](../workflows/)
- [部署运维手册](../operations/)

---

**[组件名称] MCP v1.0.0** - PowerAutomation 组件  
*最后更新: 2025-06-16*

