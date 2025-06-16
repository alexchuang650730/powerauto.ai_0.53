# SmartUI MCP 完整介绍文档

## 🎯 概述

SmartUI MCP是PowerAutomation生态系统中的智能用户界面管理组件，采用双层架构设计，提供统一的Web界面管理和MCP组件协调功能。

## 🏗️ 架构设计

### 双层架构
SmartUI MCP采用创新的双层架构设计：

1. **主UI服务层** (端口5001)
   - 提供Web用户界面
   - 处理用户交互
   - 作为MCP Coordinator的代理
   - 前端界面渲染

2. **MCP组件层** (端口8090)
   - 标准MCP组件
   - UI组件管理和协调
   - 会话管理
   - 与其他MCP组件通信

### 通信流程
```
用户浏览器 → SmartUI主服务(5001) → MCP Coordinator(8089) → 各个MCP组件
                     ↓
              Smart UI MCP(8090) ← MCP Coordinator(8089)
```

## 📁 目录结构

```
mcp/adapters/smartui_mcp/
├── complete_api_server.py           # 主UI服务器
├── smart_ui_mcp.py                 # MCP组件
├── api_server.py                   # API服务器组件
├── frontend/                       # 前端资源
│   ├── smart_ui_enhanced_dashboard.html    # 增强版仪表板
│   ├── client_webadmin.html               # 管理界面
│   ├── client_webadmin_v2.html            # 管理界面v2
│   ├── ai_chat_interface_v2.html          # AI聊天界面
│   └── smart_ui_manus_app_intervention.html # Manus应用介入界面
├── backup/                         # 旧版本备份
│   ├── README.md                   # 旧版本说明
│   ├── api_server.py              # 旧版API服务器
│   ├── sync_engine.py             # 同步引擎
│   ├── workflow_manager.py        # 工作流管理器
│   └── user_manager.py            # 用户管理器
└── remote_deploy.sh               # 远程部署脚本
```

## 🚀 核心功能

### 1. 系统状态监控
- **MCP协调器状态**: 实时监控MCP Coordinator运行状态
- **组件状态显示**: 显示所有MCP组件的运行状态
  - KILOCODE MCP: 工作流兜底创建引擎
  - RELEASE MANAGER MCP: 发布管理系统
  - SMART UI MCP: 智能UI管理组件
  - TEST MANAGER MCP: 测试管理系统

### 2. 飞书集成
- **实时通知**: 与飞书平台集成，提供实时通知功能
- **团队协作**: 支持团队协作和移动端同步
- **群组管理**: 管理活跃群组和通知

### 3. GitHub同步
- **代码同步**: 与GitHub仓库实时同步
- **Webhook监听**: 监听GitHub事件
- **自动部署**: 支持自动部署功能
- **代码质量检查**: 集成代码质量检查

### 4. 系统资源监控
- **CPU使用率**: 实时监控CPU使用情况
- **内存使用**: 监控内存使用状态
- **网络状态**: 检查网络连接状态
- **存储空间**: 监控存储使用情况
- **Amazon EC2**: 监控EC2实例状态

## 🔧 服务配置

### 主UI服务启动
```bash
cd /opt/powerautomation/mcp/adapters/smartui_mcp
python3 complete_api_server.py
```

### MCP组件启动
```bash
cd /opt/powerautomation/mcp/adapters/smartui_mcp
python3 smart_ui_mcp.py --port 8090
```

### 服务验证
```bash
# 检查主UI服务
curl http://localhost:5001

# 检查MCP组件
curl http://localhost:8090/api/status
```

## 🌐 访问地址

- **主界面**: http://98.81.255.168:5001
- **MCP API**: http://98.81.255.168:8090/api/status
- **MCP Coordinator**: http://98.81.255.168:8089/api/mcp/status

## 📊 界面功能

### 主仪表板
- **系统状态概览**: 显示所有系统组件状态
- **实时数据**: 动态更新系统指标
- **快速操作**: 提供常用操作的快速入口

### 管理界面
- **MCP组件管理**: 管理和监控所有MCP组件
- **配置管理**: 系统配置和参数设置
- **日志查看**: 查看系统运行日志

### AI聊天界面
- **智能对话**: 与AI助手进行交互
- **工作流操作**: 通过对话执行工作流
- **系统查询**: 查询系统状态和信息

## 🔄 版本历史

### v1.0.0 (当前版本)
- ✅ 双层架构设计
- ✅ MCP组件集成
- ✅ 飞书集成
- ✅ GitHub同步
- ✅ 系统监控
- ✅ 统一目录结构

### 备份版本
- 📦 旧版本文件安全备份在 `backup/` 目录
- 📦 保留历史功能和配置
- 📦 支持版本回滚

## 🛠️ 技术栈

### 后端技术
- **Python 3.11**: 主要开发语言
- **Flask**: Web框架
- **MCP协议**: 组件间通信

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript**: 交互逻辑
- **响应式设计**: 支持多设备

### 集成服务
- **飞书API**: 团队协作
- **GitHub API**: 代码管理
- **Amazon EC2**: 云服务

## 🔐 安全特性

### 访问控制
- **端口隔离**: 不同服务使用不同端口
- **内网访问**: 核心服务仅内网访问
- **外网代理**: 通过主UI服务代理访问

### 数据安全
- **配置加密**: 敏感配置信息加密存储
- **日志管理**: 安全的日志记录和管理
- **备份机制**: 完整的数据备份策略

## 📈 性能优化

### 响应优化
- **异步处理**: 使用异步机制提高响应速度
- **缓存机制**: 智能缓存减少重复请求
- **负载均衡**: 支持负载均衡配置

### 资源优化
- **内存管理**: 优化内存使用
- **CPU优化**: 高效的CPU使用策略
- **网络优化**: 减少网络传输开销

## 🚨 故障排除

### 常见问题

#### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep -E '(5001|8090)'

# 检查进程状态
ps aux | grep -E '(complete_api_server|smart_ui_mcp)'

# 重启服务
cd /opt/powerautomation/mcp/adapters/smartui_mcp
python3 complete_api_server.py &
python3 smart_ui_mcp.py --port 8090 &
```

#### MCP组件连接失败
```bash
# 检查MCP Coordinator状态
curl http://localhost:8089/api/mcp/status

# 重启MCP Coordinator
cd /opt/powerautomation/mcp_coordinator
python3 mcp_coordinator.py --port 8089 &
```

### 日志查看
```bash
# 查看主UI服务日志
tail -f /opt/powerautomation/mcp/adapters/smartui_mcp/smartui_main.log

# 查看MCP组件日志
tail -f /opt/powerautomation/mcp/adapters/smartui_mcp/smart_ui_mcp_new.log
```

## 🔮 未来规划

### 短期目标
- [ ] 增强AI聊天功能
- [ ] 优化界面响应速度
- [ ] 添加更多监控指标

### 长期目标
- [ ] 支持多租户架构
- [ ] 集成更多第三方服务
- [ ] 开发移动端应用

## 📞 支持与联系

- **项目仓库**: https://github.com/alexchuang650730/powerauto.ai_0.53
- **文档位置**: `/opt/powerautomation/docs/smartui/`
- **技术支持**: PowerAutomation团队

---

*最后更新: 2025年6月16日*
*版本: v1.0.0*

