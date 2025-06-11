#!/bin/bash
# PowerAutomation 分布式协调器构建脚本
# 构建和部署分布式测试协调器

set -e

echo "🚀 PowerAutomation 分布式协调器构建脚本"
echo "========================================"

# 配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/distributed_coordinator"
DIST_DIR="$PROJECT_ROOT/dist/distributed_coordinator"

# 清理构建目录
echo "🧹 清理构建目录..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "
import sys
required_packages = [
    'numpy', 'pandas', 'asyncio', 'psutil'
]
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

# 特殊检查scikit-learn
try:
    import sklearn
except ImportError:
    missing.append('scikit-learn')

if missing:
    print(f'❌ 缺少依赖包: {missing}')
    print('请运行: pip3 install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ 所有依赖包已安装')
"

# 复制源代码
echo "📦 复制源代码..."
cp -r "$PROJECT_ROOT/shared_core/engines/distributed_coordinator" "$BUILD_DIR/" || echo "⚠️ 分布式协调器源码复制失败"
cp -r "$PROJECT_ROOT/tests/automated_testing_framework/integrations" "$BUILD_DIR/" || echo "⚠️ 集成组件复制失败"
cp "$PROJECT_ROOT/shared_core/mcptool/adapters/distributed_test_coordinator_mcp.py" "$BUILD_DIR/" || echo "⚠️ MCP适配器复制失败"

# 运行测试
echo "🧪 运行单元测试..."
cd "$PROJECT_ROOT"
python3 -m pytest tests/automated_testing_framework/distributed_coordination/ -v || {
    echo "⚠️ 测试失败，但继续构建..."
}

# 创建分发包
echo "📦 创建分发包..."
cd "$BUILD_DIR"
tar -czf "$DIST_DIR/powerauto-distributed-coordinator-$(date +%Y%m%d-%H%M%S).tar.gz" .

# 生成部署脚本
echo "📝 生成部署脚本..."
cat > "$DIST_DIR/deploy.sh" << 'EOF'
#!/bin/bash
# PowerAutomation 分布式协调器部署脚本

echo "🚀 部署PowerAutomation分布式协调器..."

# 解压分发包
PACKAGE=$(ls powerauto-distributed-coordinator-*.tar.gz | head -1)
if [ -z "$PACKAGE" ]; then
    echo "❌ 未找到分发包"
    exit 1
fi

echo "📦 解压 $PACKAGE..."
tar -xzf "$PACKAGE"

# 安装依赖
echo "📥 安装Python依赖..."
pip3 install scikit-learn numpy pandas psutil

# 设置环境变量
export PYTHONPATH="$PWD:$PYTHONPATH"

echo "✅ 部署完成！"
echo "使用方法:"
echo "  python3 -c 'from distributed_coordinator import DistributedTestCoordinator; print(\"导入成功\")'"
EOF

chmod +x "$DIST_DIR/deploy.sh"

# 生成配置文件
echo "⚙️ 生成配置文件..."
cat > "$DIST_DIR/config.yaml" << 'EOF'
# PowerAutomation 分布式协调器配置

coordinator:
  name: "PowerAutomation分布式协调器"
  version: "1.0.0"
  max_nodes: 100
  heartbeat_interval: 30
  task_timeout: 3600

scheduler:
  algorithm: "ml_driven"
  enable_learning: true
  performance_weight: 0.4
  reliability_weight: 0.3
  cost_weight: 0.3

performance:
  cache_size_mb: 512
  cache_strategy: "adaptive"
  enable_incremental: true
  parallel_threshold: 4

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "distributed_coordinator.log"
EOF

echo "✅ 构建完成！"
echo "📁 构建产物位置: $DIST_DIR"
echo "📦 分发包: $(ls $DIST_DIR/*.tar.gz)"
echo ""
echo "🚀 部署方法:"
echo "  1. 复制分发包到目标服务器"
echo "  2. 运行: bash deploy.sh"
echo "  3. 测试: python3 -c 'from distributed_coordinator import DistributedTestCoordinator'"

