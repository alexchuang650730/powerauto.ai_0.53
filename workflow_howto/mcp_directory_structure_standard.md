# MCP Adapters 目录结构标准

## 📁 **标准MCP目录结构**

每个MCP都应该遵循以下目录结构：

```
mcp/adapters/{mcp_name}/
├── {mcp_name}.py              # 主MCP实现文件
├── {mcp_name}_cli.py          # CLI接口文件 (可选)
├── config.py                  # 配置文件 (可选)
├── __init__.py               # Python包初始化文件
├── README.md                 # MCP说明文档
├── requirements.txt          # 依赖包列表 (可选)
└── tests/                    # 测试文件目录 (可选)
    ├── test_{mcp_name}.py
    └── __init__.py
```

## ✅ **当前MCP目录状态**

### **1. kilocode_mcp** ✅ 完整
```
mcp/adapters/kilocode_mcp/
├── kilocode_mcp.py
├── config.py
├── __init__.py
└── test_kilocode_mcp.py
```

### **2. github_mcp** ✅ 完整
```
mcp/adapters/github_mcp/
├── github_mcp.py
├── github_mcp_cli.py
└── github_mcp.log
```

### **3. release_manager_mcp** ✅ 完整
```
mcp/adapters/release_manager_mcp/
├── release_manager_mcp.py
├── release_manager_cli.py
└── release_manager.log
```

### **4. test_manager_mcp** ✅ 完整
```
mcp/adapters/test_manager_mcp/
├── test_manager_mcp.py
├── test_manager_cli.py
└── test_manager.log
```

### **5. smartui_mcp** ✅ 完整
```
mcp/adapters/smartui_mcp/
├── smartui_mcp.py
└── smartui_mcp_cli.py
```

### **6. smart_intervention_mcp** ⚠️ 需要补全
```
mcp/adapters/smart_intervention_mcp/
└── smart_intervention_mcp.py
```
**缺少**: CLI文件、README、__init__.py

### **7. development_intervention_mcp** ⚠️ 需要补全
```
mcp/adapters/development_intervention_mcp/
└── development_intervention_mcp.py
```
**缺少**: CLI文件、README、__init__.py

## 🔧 **需要补全的文件**

1. **为每个MCP添加 __init__.py**
2. **为每个MCP添加 README.md**
3. **为Smart Intervention MCP添加CLI文件**
4. **统一日志文件命名规范**

