# SmartUI MCP 快速开始指南

## 🚀 快速启动

### 1. 启动服务
```bash
# 进入SmartUI目录
cd /opt/powerautomation/mcp/adapters/smartui_mcp

# 启动主UI服务 (端口5001)
python3 complete_api_server.py &

# 启动MCP组件 (端口8090)
python3 smart_ui_mcp.py --port 8090 &
```

### 2. 验证服务
```bash
# 检查服务状态
netstat -tlnp | grep -E '(5001|8090)'

# 测试主界面
curl http://localhost:5001

# 测试MCP API
curl http://localhost:8090/api/status
```

### 3. 访问界面
- **主界面**: http://98.81.255.168:5001
- **管理后台**: http://98.81.255.168:5001/admin

## 📋 基本操作

### 查看系统状态
1. 打开主界面
2. 查看"系统状态监控"面板
3. 确认所有MCP组件状态为"运行中"

### 使用AI聊天
1. 点击AI聊天按钮
2. 输入查询或指令
3. 查看AI响应和系统操作

### 管理MCP组件
1. 进入管理界面
2. 查看"MCP协调器"状态
3. 监控各个组件运行情况

## 🔧 常用命令

### 服务管理
```bash
# 查看运行进程
ps aux | grep -E '(complete_api_server|smart_ui_mcp)'

# 停止服务
pkill -f complete_api_server
pkill -f smart_ui_mcp

# 重启服务
cd /opt/powerautomation/mcp/adapters/smartui_mcp
python3 complete_api_server.py &
python3 smart_ui_mcp.py --port 8090 &
```

### 日志查看
```bash
# 查看实时日志
tail -f smartui_main.log
tail -f smart_ui_mcp_new.log

# 查看错误日志
grep -i error *.log
```

## ⚠️ 注意事项

1. **端口冲突**: 确保5001和8090端口未被占用
2. **依赖服务**: 需要MCP Coordinator (端口8089) 正常运行
3. **权限问题**: 确保有足够权限访问文件和端口
4. **网络访问**: 外网访问需要防火墙配置

## 📞 快速支持

遇到问题时的检查顺序：
1. 检查服务是否正常启动
2. 查看日志文件中的错误信息
3. 验证MCP Coordinator连接状态
4. 检查网络和防火墙配置

