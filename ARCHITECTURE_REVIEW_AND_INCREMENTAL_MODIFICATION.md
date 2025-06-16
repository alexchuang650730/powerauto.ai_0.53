# 架构Review和增量修改方案

## 🔍 **当前架构状态分析**

### **运行中的服务**
- ✅ **kilocode_mcp_server.py** (PID: 19512) - 运行177小时
- ✅ **mcp_deployment_monitor.py** (PID: 20860) - 运行中
- ❌ **MCP Coordinator** - 未在8089端口运行
- ❌ **Operations Workflow MCP** - 已停止服务

### **端口使用情况**
- **5001**: 被某个python3进程占用 (PID: 39059)
- **8089**: 空闲，MCP Coordinator未运行

### **架构问题识别**
1. **违反MCP通信规范**: Web API直接调用Operations Workflow MCP组件
2. **缺少中央协调器**: MCP Coordinator (8089) 未运行
3. **直接导入问题**: 绕过了标准MCP协议

## 🎯 **正确的MCP通信架构设计**

### **目标架构**
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Operations         │    │   MCP Coordinator   │    │     SmartUI         │
│  Workflow MCP       │◄──►│     (8089)          │◄──►│     (5001)          │
│  (端口: 8090)       │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### **通信流程**
1. **SmartUI (5001)** → **MCP Coordinator (8089)** → **Operations Workflow MCP (8090)**
2. 所有MCP调用通过标准MCP协议进行
3. MCP Coordinator统一管理交互数据
4. 各MCP专注业务逻辑，不直接通信

## 📋 **增量修改计划**

### **Phase 1: 启动MCP Coordinator**
- 启动MCP Coordinator服务在8089端口
- 确保中央协调器正常运行

### **Phase 2: 修改Operations Workflow MCP**
- 将Operations Workflow MCP改为标准MCP服务
- 运行在8090端口
- 实现标准MCP协议接口

### **Phase 3: 修改Web API通信方式**
- 移除直接导入Operations Workflow MCP组件
- 通过HTTP请求调用MCP Coordinator (8089)
- MCP Coordinator转发请求到Operations Workflow MCP (8090)

### **Phase 4: 标准化MCP协议**
- 定义统一的MCP通信协议
- 实现请求/响应格式标准化
- 添加错误处理和重试机制

## 🔧 **技术实现要点**

### **MCP Coordinator (8089)**
- 作为中央协调器，管理所有MCP通信
- 维护MCP注册表和路由规则
- 统一交互数据管理

### **Operations Workflow MCP (8090)**
- 实现标准MCP服务接口
- 提供文件处理、监控、介入协调功能
- 通过MCP协议与Coordinator通信

### **SmartUI (5001)**
- 通过MCP Coordinator访问所有MCP功能
- 不直接调用任何MCP组件
- 统一的API调用接口

## ✅ **预期收益**

1. **架构合规**: 符合MCP通信最佳实践
2. **可扩展性**: 易于添加新的MCP组件
3. **统一管理**: 中央协调器统一管理交互数据
4. **标准化**: 统一的MCP协议和接口

---
**下一步**: 开始实施增量修改，首先启动MCP Coordinator服务

