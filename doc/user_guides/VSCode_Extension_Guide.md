# PowerAutomation 分布式协调器 VSCode 扩展

## 安装说明

### 1. 开发模式安装
```bash
# 进入扩展目录
cd /home/ubuntu/powerauto.ai_0.53/vscode_extension/distributed_coordinator

# 安装依赖
npm install

# 编译扩展
npm run compile

# 在VSCode中按F5启动调试模式
```

### 2. 手动安装
```bash
# 打包扩展
npm install -g vsce
vsce package

# 在VSCode中安装.vsix文件
# 命令面板 -> Extensions: Install from VSIX
```

### 3. 功能特性

#### 🎯 分布式节点监控
- 实时显示节点状态 (在线/离线/忙碌)
- CPU和内存使用率监控
- 活跃任务数量统计
- 心跳状态检查

#### 📊 性能监控面板
- 缓存命中率实时图表
- 平均执行时间统计
- 并行效率指标
- 资源利用率监控

#### 🎛️ 交互式控制
- 一键启动/停止分布式测试
- 节点状态快速查看
- 任务重新分配
- 故障节点修复

#### 🔧 开发调试工具
- 实时日志查看
- 性能瓶颈分析
- 配置参数调整
- 测试流程监控

### 4. 使用方法

#### 激活扩展
1. 打开包含PowerAutomation项目的工作区
2. 扩展会自动检测并激活
3. 在侧边栏看到"PowerAutomation"图标

#### 查看节点状态
1. 点击侧边栏的"分布式节点"视图
2. 查看所有节点的实时状态
3. 点击节点查看详细信息

#### 监控性能
1. 打开"性能监控"面板
2. 查看实时性能指标
3. 分析系统瓶颈

#### 运行分布式测试
1. 使用命令面板 (Ctrl+Shift+P)
2. 搜索"PowerAutomation: 运行分布式测试"
3. 监控测试进度

### 5. 配置选项

```json
{
  "powerautomation.distributed.autoStart": true,
  "powerautomation.distributed.refreshInterval": 5000,
  "powerautomation.distributed.maxNodes": 10,
  "powerautomation.performance.cacheSize": 512
}
```

### 6. 故障排除

#### 扩展无法激活
- 确保工作区包含PowerAutomation项目
- 检查项目结构是否正确
- 查看VSCode输出面板的错误信息

#### 节点状态显示异常
- 检查分布式协调器是否运行
- 验证网络连接
- 查看MCP适配器状态

#### 性能数据不更新
- 检查刷新间隔设置
- 验证性能监控服务状态
- 重启扩展

### 7. 开发说明

#### 扩展结构
```
vscode_extension/distributed_coordinator/
├── package.json          # 扩展配置
├── tsconfig.json         # TypeScript配置
├── src/
│   └── extension.ts      # 主扩展文件
├── out/                  # 编译输出
└── node_modules/         # 依赖包
```

#### 调试模式
1. 在VSCode中打开扩展目录
2. 按F5启动扩展开发主机
3. 在新窗口中测试扩展功能

#### 发布扩展
```bash
# 安装发布工具
npm install -g vsce

# 打包扩展
vsce package

# 发布到市场
vsce publish
```

## 支持

如有问题，请联系PowerAutomation团队或查看项目文档。

