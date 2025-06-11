#!/bin/bash
"""
PowerAutomation v0.5.3 統一構建和部署腳本

支持三種架構的統一構建、打包和部署
"""

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 項目信息
PROJECT_NAME="PowerAutomation"
VERSION="0.5.3"
BUILD_DIR="./build"
DIST_DIR="./dist"

# 支持的架構類型
ARCHITECTURES=("enterprise" "consumer" "opensource")

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 顯示幫助信息
show_help() {
    cat << EOF
PowerAutomation v${VERSION} 統一構建腳本

用法:
    $0 [選項] <命令> [架構類型]

命令:
    build       構建指定架構
    package     打包指定架構
    deploy      部署指定架構
    clean       清理構建文件
    test        運行測試
    all         構建所有架構

架構類型:
    enterprise  企業級架構
    consumer    消費級架構
    opensource  開源社區架構

選項:
    -h, --help      顯示此幫助信息
    -v, --verbose   詳細輸出
    -d, --dev       開發模式
    --docker        使用Docker構建
    --no-cache      不使用緩存

示例:
    $0 build enterprise
    $0 package consumer
    $0 deploy opensource
    $0 all
EOF
}

# 檢查依賴
check_dependencies() {
    log_info "檢查構建依賴..."
    
    # 檢查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安裝"
        exit 1
    fi
    
    # 檢查Node.js (消費級架構需要)
    if ! command -v node &> /dev/null; then
        log_warning "Node.js 未安裝，消費級架構構建可能失敗"
    fi
    
    # 檢查Docker (如果使用Docker模式)
    if [[ "$USE_DOCKER" == "true" ]] && ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝"
        exit 1
    fi
    
    log_success "依賴檢查完成"
}

# 創建構建目錄
setup_build_dirs() {
    log_info "創建構建目錄..."
    
    mkdir -p "$BUILD_DIR"
    mkdir -p "$DIST_DIR"
    
    for arch in "${ARCHITECTURES[@]}"; do
        mkdir -p "$BUILD_DIR/$arch"
        mkdir -p "$DIST_DIR/$arch"
    done
    
    log_success "構建目錄創建完成"
}

# 安裝Python依賴
install_python_deps() {
    log_info "安裝Python依賴..."
    
    if [[ ! -f "requirements.txt" ]]; then
        log_warning "requirements.txt 不存在，跳過Python依賴安裝"
        return
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        pip3 install -r requirements.txt
    else
        pip3 install -r requirements.txt > /dev/null 2>&1
    fi
    
    log_success "Python依賴安裝完成"
}

# 構建共享核心
build_shared_core() {
    log_info "構建共享核心組件..."
    
    # 複製共享核心文件
    cp -r shared_core "$BUILD_DIR/"
    
    # 編譯Python字節碼
    python3 -m compileall "$BUILD_DIR/shared_core" > /dev/null 2>&1
    
    log_success "共享核心構建完成"
}

# 構建企業級架構
build_enterprise() {
    log_info "構建企業級架構..."
    
    local build_path="$BUILD_DIR/enterprise"
    
    # 複製企業級文件
    cp -r enterprise/* "$build_path/"
    
    # 複製共享核心
    cp -r "$BUILD_DIR/shared_core" "$build_path/"
    
    # 生成企業級配置
    python3 -c "
import sys
sys.path.append('shared_core')
from shared_core.config.unified_config import get_config_manager
import yaml

config_manager = get_config_manager()
config = config_manager.get_all_config('enterprise')

# 轉換為可序列化格式
serializable_config = {}
for key, value in config.items():
    if hasattr(value, '__dict__'):
        serializable_config[key] = value.__dict__
    else:
        serializable_config[key] = value

with open('$build_path/config.yaml', 'w') as f:
    yaml.dump(serializable_config, f)
"
    
    # 創建Docker文件
    cat > "$build_path/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "backend/enterprise_server.py"]
EOF
    
    # 創建docker-compose文件
    cat > "$build_path/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  powerautomation-enterprise:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POWERAUTO_ARCHITECTURE_TYPE=enterprise
      - POWERAUTO_DEPLOYMENT_MODE=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=powerautomation
      - POSTGRES_USER=powerauto
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    
    log_success "企業級架構構建完成"
}

# 構建消費級架構
build_consumer() {
    log_info "構建消費級架構..."
    
    local build_path="$BUILD_DIR/consumer"
    
    # 複製消費級文件
    cp -r consumer/* "$build_path/"
    
    # 複製共享核心
    cp -r "$BUILD_DIR/shared_core" "$build_path/"
    
    # 構建瀏覽器插件
    if command -v npm &> /dev/null; then
        log_info "構建瀏覽器插件..."
        
        # 創建package.json
        cat > "$build_path/browser_extension/package.json" << 'EOF'
{
  "name": "powerautomation-browser-extension",
  "version": "0.5.3",
  "description": "PowerAutomation 瀏覽器插件",
  "scripts": {
    "build": "webpack --mode production",
    "dev": "webpack --mode development --watch"
  },
  "devDependencies": {
    "webpack": "^5.0.0",
    "webpack-cli": "^4.0.0"
  }
}
EOF
        
        # 簡化的webpack配置
        cat > "$build_path/browser_extension/webpack.config.js" << 'EOF'
const path = require('path');

module.exports = {
  entry: {
    popup: './popup.js',
    content_script: './content_script.js',
    background: './background.js'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js'
  },
  mode: 'production'
};
EOF
    fi
    
    # 創建Electron應用配置
    cat > "$build_path/desktop_app/package.json" << 'EOF'
{
  "name": "powerautomation-desktop",
  "version": "0.5.3",
  "description": "PowerAutomation 桌面應用",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "dist": "electron-builder --publish=never"
  },
  "devDependencies": {
    "electron": "^20.0.0",
    "electron-builder": "^23.0.0"
  },
  "build": {
    "appId": "com.powerautomation.desktop",
    "productName": "PowerAutomation",
    "directories": {
      "output": "dist"
    },
    "files": [
      "**/*",
      "!node_modules"
    ]
  }
}
EOF
    
    log_success "消費級架構構建完成"
}

# 構建開源架構
build_opensource() {
    log_info "構建開源社區架構..."
    
    local build_path="$BUILD_DIR/opensource"
    
    # 複製開源文件
    cp -r opensource/* "$build_path/"
    
    # 複製共享核心
    cp -r "$BUILD_DIR/shared_core" "$build_path/"
    
    # 創建setup.py
    cat > "$build_path/setup.py" << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="powerautomation-cli",
    version="0.5.3",
    author="PowerAutomation Team",
    author_email="team@powerautomation.com",
    description="PowerAutomation 開源社區版 CLI工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/powerautomation/powerautomation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "powerauto=cli_tool.powerauto_cli:cli",
        ],
    },
)
EOF
    
    # 創建README.md
    cat > "$build_path/README.md" << 'EOF'
# PowerAutomation CLI

PowerAutomation 開源社區版命令行工具

## 安裝

```bash
pip install powerautomation-cli
```

## 使用

```bash
# 初始化工作空間
powerauto init

# 查看狀態
powerauto status

# 列出工作流
powerauto workflow list

# 執行工作流
powerauto workflow run my_workflow

# 列出插件
powerauto plugin list
```

## 文檔

詳細文檔請訪問: https://docs.powerautomation.com
EOF
    
    log_success "開源社區架構構建完成"
}

# 打包架構
package_architecture() {
    local arch=$1
    log_info "打包 $arch 架構..."
    
    local build_path="$BUILD_DIR/$arch"
    local dist_path="$DIST_DIR/$arch"
    
    case $arch in
        "enterprise")
            # 創建Docker鏡像
            if [[ "$USE_DOCKER" == "true" ]]; then
                cd "$build_path"
                docker build -t "powerautomation-enterprise:$VERSION" .
                docker save "powerautomation-enterprise:$VERSION" > "$dist_path/powerautomation-enterprise-$VERSION.tar"
                cd - > /dev/null
            fi
            
            # 創建tar.gz包
            tar -czf "$dist_path/powerautomation-enterprise-$VERSION.tar.gz" -C "$BUILD_DIR" "$arch"
            ;;
            
        "consumer")
            # 打包瀏覽器插件
            if [[ -d "$build_path/browser_extension" ]]; then
                cd "$build_path/browser_extension"
                zip -r "$dist_path/powerautomation-browser-extension-$VERSION.zip" . -x "node_modules/*" "*.log"
                cd - > /dev/null
            fi
            
            # 打包桌面應用
            tar -czf "$dist_path/powerautomation-consumer-$VERSION.tar.gz" -C "$BUILD_DIR" "$arch"
            ;;
            
        "opensource")
            # 創建Python包
            cd "$build_path"
            python3 setup.py sdist bdist_wheel > /dev/null 2>&1
            cp dist/* "$dist_path/"
            cd - > /dev/null
            
            # 創建源碼包
            tar -czf "$dist_path/powerautomation-opensource-$VERSION-source.tar.gz" -C "$BUILD_DIR" "$arch"
            ;;
    esac
    
    log_success "$arch 架構打包完成"
}

# 部署架構
deploy_architecture() {
    local arch=$1
    log_info "部署 $arch 架構..."
    
    case $arch in
        "enterprise")
            if [[ "$USE_DOCKER" == "true" ]]; then
                log_info "使用Docker Compose部署企業級架構..."
                cd "$BUILD_DIR/$arch"
                docker-compose up -d
                cd - > /dev/null
            else
                log_info "啟動企業級服務器..."
                cd "$BUILD_DIR/$arch"
                python3 backend/enterprise_server.py &
                cd - > /dev/null
            fi
            ;;
            
        "consumer")
            log_info "消費級架構需要手動安裝瀏覽器插件和桌面應用"
            log_info "瀏覽器插件包: $DIST_DIR/$arch/powerautomation-browser-extension-$VERSION.zip"
            ;;
            
        "opensource")
            log_info "安裝開源CLI工具..."
            cd "$BUILD_DIR/$arch"
            pip3 install -e .
            cd - > /dev/null
            log_info "使用 'powerauto --help' 查看命令"
            ;;
    esac
    
    log_success "$arch 架構部署完成"
}

# 運行測試
run_tests() {
    log_info "運行測試套件..."
    
    if [[ -d "tests" ]]; then
        python3 -m pytest tests/ -v
    else
        log_warning "測試目錄不存在，跳過測試"
    fi
    
    log_success "測試完成"
}

# 清理構建文件
clean_build() {
    log_info "清理構建文件..."
    
    rm -rf "$BUILD_DIR"
    rm -rf "$DIST_DIR"
    
    # 清理Python緩存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "清理完成"
}

# 主構建函數
build_architecture() {
    local arch=$1
    
    if [[ ! " ${ARCHITECTURES[@]} " =~ " ${arch} " ]]; then
        log_error "不支持的架構類型: $arch"
        log_info "支持的架構: ${ARCHITECTURES[*]}"
        exit 1
    fi
    
    log_info "開始構建 $arch 架構..."
    
    # 構建共享核心（如果還沒構建）
    if [[ ! -d "$BUILD_DIR/shared_core" ]]; then
        build_shared_core
    fi
    
    # 構建特定架構
    case $arch in
        "enterprise")
            build_enterprise
            ;;
        "consumer")
            build_consumer
            ;;
        "opensource")
            build_opensource
            ;;
    esac
    
    log_success "$arch 架構構建完成"
}

# 構建所有架構
build_all() {
    log_info "構建所有架構..."
    
    build_shared_core
    
    for arch in "${ARCHITECTURES[@]}"; do
        build_architecture "$arch"
    done
    
    log_success "所有架構構建完成"
}

# 主函數
main() {
    local command=""
    local architecture=""
    
    # 解析命令行參數
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -d|--dev)
                DEV_MODE="true"
                shift
                ;;
            --docker)
                USE_DOCKER="true"
                shift
                ;;
            --no-cache)
                NO_CACHE="true"
                shift
                ;;
            build|package|deploy|clean|test|all)
                command=$1
                shift
                ;;
            enterprise|consumer|opensource)
                architecture=$1
                shift
                ;;
            *)
                log_error "未知參數: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 檢查命令
    if [[ -z "$command" ]]; then
        log_error "請指定命令"
        show_help
        exit 1
    fi
    
    # 執行命令
    case $command in
        "build")
            check_dependencies
            setup_build_dirs
            install_python_deps
            
            if [[ "$command" == "all" ]] || [[ -z "$architecture" ]]; then
                build_all
            else
                build_architecture "$architecture"
            fi
            ;;
            
        "package")
            if [[ -z "$architecture" ]]; then
                log_error "打包命令需要指定架構類型"
                exit 1
            fi
            package_architecture "$architecture"
            ;;
            
        "deploy")
            if [[ -z "$architecture" ]]; then
                log_error "部署命令需要指定架構類型"
                exit 1
            fi
            deploy_architecture "$architecture"
            ;;
            
        "clean")
            clean_build
            ;;
            
        "test")
            run_tests
            ;;
            
        "all")
            check_dependencies
            setup_build_dirs
            install_python_deps
            build_all
            
            # 打包所有架構
            for arch in "${ARCHITECTURES[@]}"; do
                package_architecture "$arch"
            done
            ;;
    esac
    
    log_success "操作完成"
}

# 設置默認值
VERBOSE="false"
DEV_MODE="false"
USE_DOCKER="false"
NO_CACHE="false"

# 執行主函數
main "$@"

