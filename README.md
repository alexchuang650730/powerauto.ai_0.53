<<<<<<< HEAD
# PowerAutomation v0.5.3 統一架構

基於v0.5.2版本設計的三種前端架構統一方案，整合最新release代碼，提供企業級、消費級和開源社區三種不同的使用體驗。

## 🎯 項目概覽

PowerAutomation v0.5.3 採用統一核心、差異化前端的設計理念，通過共享核心組件庫支持三種不同的架構模式：

- **🏢 企業級架構** - 完整雲服務架構，提供Web控制台、認證服務、計費系統
- **👤 消費級架構** - 輕量插件架構，包括瀏覽器插件、桌面應用
- **🔓 開源社區架構** - 純CLI工具架構，提供命令行工具、SDK、社區插件

## 📁 項目結構

```
powerautomation_v0.53_unified/
├── shared_core/                    # 共享核心組件庫 ⭐
│   ├── architecture/               # 統一架構核心
│   ├── engines/                    # 智能引擎
│   ├── server/                     # 統一服務器
│   ├── mcptool/                    # MCP工具集
│   ├── config/                     # 統一配置
│   └── utils/                      # 工具函數
├── enterprise/                     # 2B企業級架構 🏢
│   ├── frontend/                   # 企業級前端
│   ├── backend/                    # 企業級後端
│   ├── deployment/                 # 部署配置
│   └── config/                     # 企業級配置
├── consumer/                       # 2C消費級架構 👤
│   ├── browser_extension/          # 瀏覽器插件
│   ├── desktop_app/                # 桌面應用
│   ├── mobile_app/                 # 移動應用
│   └── config/                     # 消費級配置
├── opensource/                     # 開源社區架構 🔓
│   ├── cli_tool/                   # 命令行工具
│   ├── sdk/                        # 開發SDK
│   ├── community_plugins/          # 社區插件
│   └── config/                     # 開源配置
├── tests/                          # 統一測試套件
├── docs/                           # 統一文檔
├── tools/                          # 開發工具
└── release/                        # 發布包
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 克隆項目
git clone https://github.com/powerautomation/powerautomation.git
cd powerautomation_v0.53_unified

# 安裝Python依賴
pip install -r requirements.txt

# 安裝Node.js依賴（消費級架構需要）
npm install
```

### 2. 構建項目

使用統一構建腳本構建所有架構：

```bash
# 構建所有架構
./tools/build_scripts/unified_build.sh all

# 構建特定架構
./tools/build_scripts/unified_build.sh build enterprise
./tools/build_scripts/unified_build.sh build consumer
./tools/build_scripts/unified_build.sh build opensource
```

### 3. 運行演示

#### 企業級架構
```bash
cd build/enterprise
python backend/enterprise_server.py
# 訪問 http://localhost:8000
```

#### 消費級架構
```bash
cd build/consumer
python desktop_app/consumer_app.py
```

#### 開源社區架構
```bash
cd build/opensource
python cli_tool/powerauto_cli.py --help
```

## 🏗️ 架構特性

### 共享核心組件庫

所有架構共享的核心功能：

- **統一架構核心** - 基於v0.5.2的統一架構實現
- **智能引擎** - RL-SRT學習系統和多角色智能引擎
- **MCP工具集** - 完整的MCP適配器和工具
- **統一配置** - 支持三種架構的配置管理
- **標準化日誌** - 統一的日誌系統

### 企業級架構特性

- ✅ **Web控制台** - 企業級管理界面
- ✅ **認證服務** - JWT令牌認證和用戶管理
- ✅ **計費系統** - 使用量統計和賬單生成
- ✅ **多租戶支持** - 組織和用戶管理
- ✅ **API網關** - 統一的API接入點
- ✅ **Docker部署** - 容器化部署支持

### 消費級架構特性

- ✅ **瀏覽器插件** - Chrome/Firefox插件支持
- ✅ **桌面應用** - Electron桌面應用
- ✅ **本地數據庫** - SQLite本地存儲
- ✅ **雲端同步** - 數據雲端同步功能
- ✅ **離線模式** - 離線工作支持
- ✅ **自動化任務** - 個人自動化任務管理

### 開源社區架構特性

- ✅ **CLI工具** - 功能完整的命令行工具
- ✅ **工作流管理** - YAML格式工作流定義
- ✅ **插件系統** - 可擴展的插件架構
- ✅ **多語言SDK** - Python/JavaScript/Go SDK
- ✅ **社區插件** - VS Code/Vim/Emacs插件
- ✅ **開源協議** - MIT開源許可證

## 📦 部署方案

### 企業級部署

#### Docker部署
```bash
cd build/enterprise
docker-compose up -d
```

#### Kubernetes部署
```bash
kubectl apply -f deployment/kubernetes/
```

#### AWS CloudFormation部署
```bash
aws cloudformation create-stack \
  --stack-name powerautomation-enterprise \
  --template-body file://deployment/aws_cloudformation/template.yaml
```

### 消費級部署

#### 瀏覽器插件安裝
1. 打開Chrome擴展管理頁面
2. 啟用開發者模式
3. 加載已解壓的擴展程序
4. 選擇 `dist/consumer/browser_extension` 目錄

#### 桌面應用安裝
```bash
# Windows
./dist/consumer/PowerAutomation-Setup.exe

# macOS
./dist/consumer/PowerAutomation.dmg

# Linux
./dist/consumer/PowerAutomation.AppImage
```

### 開源社區部署

#### PyPI安裝
```bash
pip install powerautomation-cli
powerauto --help
```

#### 源碼安裝
```bash
cd build/opensource
pip install -e .
powerauto init
```

## 🧪 測試

### 運行所有測試
```bash
./tools/build_scripts/unified_build.sh test
```

### 運行特定測試
```bash
# 單元測試
python -m pytest tests/unit_tests/

# 集成測試
python -m pytest tests/integration_tests/

# 端到端測試
python -m pytest tests/e2e_tests/

# 性能測試
python -m pytest tests/performance_tests/
```

## 📚 文檔

- [架構設計文檔](docs/architecture/unified_design_specification.md)
- [API參考文檔](docs/api_reference/)
- [用戶指南](docs/user_guides/)
- [開發者指南](docs/developer_guides/)

## 🤝 貢獻

歡迎貢獻代碼！請閱讀 [貢獻指南](CONTRIBUTING.md) 了解詳細信息。

### 開發流程

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳細信息。

## 🆘 支持

- 📧 郵件支持: support@powerautomation.com
- 💬 社區討論: https://github.com/powerautomation/powerautomation/discussions
- 🐛 問題報告: https://github.com/powerautomation/powerautomation/issues
- 📖 文檔網站: https://docs.powerautomation.com

## 🎉 致謝

感謝所有貢獻者和社區成員的支持！

---

**PowerAutomation v0.5.3** - 讓自動化更簡單，讓工作更高效！

=======
# powerauto.ai_0.53
powerauto.ai_0.53
>>>>>>> af7c063e18bcc1603845cc6c8c0a95d34db3c562
