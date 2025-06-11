# PowerAutomation v0.572 部署指南

## 🚀 快速部署

### 前置要求
- **Python**: 3.11+
- **Node.js**: 18+
- **Git**: 2.30+
- **操作系统**: Linux/macOS/Windows

### 一键部署脚本
```bash
# 克隆项目
git clone https://github.com/alexchuang650730/powerauto.ai_0.53.git
cd powerauto.ai_0.53

# 运行一键部署
bash tools/build_scripts/distributed_coordinator/build.sh
cd tools/dist/distributed_coordinator
bash deploy.sh
```

## 🏗️ 详细部署步骤

### 1. 环境准备

#### Python环境
```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 验证安装
python3 -c "import sklearn, numpy, pandas; print('依赖安装成功')"
```

#### Node.js环境
```bash
# 安装Node.js依赖
cd vscode_extension/distributed_coordinator
npm install

# 编译TypeScript
npm run compile
```

### 2. 核心组件部署

#### 分布式协调器
```bash
# 启动协调器
cd shared_core/engines/distributed_coordinator
python3 -c "
from distributed_coordinator import DistributedTestCoordinator
coordinator = DistributedTestCoordinator()
print('协调器启动成功')
"
```

#### MCP适配器
```bash
# 启动MCP适配器
python3 -c "
from shared_core.mcptool.adapters.distributed_test_coordinator_mcp import DistributedTestCoordinatorMCP
mcp = DistributedTestCoordinatorMCP()
print('MCP适配器启动成功')
"
```

#### 测试架构集成器
```bash
# 启动测试集成器
python3 -c "
from tests.automated_testing_framework.integrations import TestArchitectureIntegrator
integrator = TestArchitectureIntegrator('.')
print('测试集成器启动成功')
"
```

### 3. VSCode扩展安装

#### 开发模式
```bash
# 进入扩展目录
cd vscode_extension/distributed_coordinator

# 安装依赖
npm install

# 编译扩展
npm run compile

# 在VSCode中按F5启动调试模式
```

#### 生产模式
```bash
# 打包扩展
npm install -g vsce
vsce package

# 安装.vsix文件
# 在VSCode中: 命令面板 -> Extensions: Install from VSIX
```

## 🔧 配置管理

### 开发环境配置
```yaml
# config/dev/config.yaml
coordinator:
  max_nodes: 5
  refresh_interval: 5000
  cache_size: 256

performance:
  enable_caching: true
  cache_strategy: "adaptive"
  parallel_limit: 4

monitoring:
  enable_metrics: true
  log_level: "DEBUG"
```

### 生产环境配置
```yaml
# config/prod/config.yaml
coordinator:
  max_nodes: 100
  refresh_interval: 1000
  cache_size: 2048

performance:
  enable_caching: true
  cache_strategy: "lru"
  parallel_limit: 20

monitoring:
  enable_metrics: true
  log_level: "INFO"
```

### 测试环境配置
```yaml
# config/test/config.yaml
coordinator:
  max_nodes: 2
  refresh_interval: 10000
  cache_size: 128

performance:
  enable_caching: false
  cache_strategy: "none"
  parallel_limit: 2

monitoring:
  enable_metrics: false
  log_level: "WARNING"
```

## 🐳 Docker部署

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python3", "-m", "shared_core.engines.distributed_coordinator"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  coordinator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: powerautomation
      POSTGRES_USER: powerauto
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### 部署命令
```bash
# 构建和启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f coordinator
```

## ☸️ Kubernetes部署

### 部署清单
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powerautomation-coordinator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: powerautomation-coordinator
  template:
    metadata:
      labels:
        app: powerautomation-coordinator
    spec:
      containers:
      - name: coordinator
        image: powerautomation:v0.572
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### 服务配置
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: powerautomation-service
spec:
  selector:
    app: powerautomation-coordinator
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 部署命令
```bash
# 应用配置
kubectl apply -f k8s/

# 查看状态
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/powerautomation-coordinator
```

## 📊 监控部署

### Prometheus配置
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'powerautomation'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana仪表板
```json
{
  "dashboard": {
    "title": "PowerAutomation监控",
    "panels": [
      {
        "title": "活跃节点数",
        "type": "stat",
        "targets": [
          {
            "expr": "powerautomation_active_nodes"
          }
        ]
      },
      {
        "title": "测试执行率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(powerautomation_tests_executed[5m])"
          }
        ]
      }
    ]
  }
}
```

## 🔍 故障排除

### 常见问题

#### 1. 导入错误
```bash
# 问题: ModuleNotFoundError
# 解决: 检查Python路径
export PYTHONPATH=/path/to/powerauto.ai_0.53:$PYTHONPATH
```

#### 2. 端口冲突
```bash
# 问题: Address already in use
# 解决: 更改端口或停止冲突进程
lsof -i :8000
kill -9 <PID>
```

#### 3. 权限问题
```bash
# 问题: Permission denied
# 解决: 设置正确权限
chmod +x tools/build_scripts/distributed_coordinator/build.sh
```

### 日志分析
```bash
# 查看协调器日志
tail -f logs/coordinator.log

# 查看性能日志
tail -f logs/performance.log

# 查看错误日志
grep ERROR logs/*.log
```

### 性能调优
```bash
# 监控资源使用
htop
iotop
nethogs

# 调整缓存大小
# 编辑config/prod/config.yaml
coordinator:
  cache_size: 4096  # 增加缓存大小
```

## 📋 部署检查清单

### 部署前检查
- [ ] Python 3.11+ 已安装
- [ ] 所有依赖包已安装
- [ ] 配置文件已准备
- [ ] 网络端口已开放
- [ ] 存储空间充足

### 部署后验证
- [ ] 协调器服务正常启动
- [ ] MCP适配器响应正常
- [ ] VSCode扩展可以连接
- [ ] 测试节点注册成功
- [ ] 监控指标正常收集

### 性能验证
- [ ] 缓存命中率 > 80%
- [ ] 平均响应时间 < 200ms
- [ ] 系统资源利用率 < 80%
- [ ] 错误率 < 1%

---

*PowerAutomation v0.572 部署指南*  
*更新日期: 2025年6月11日*

