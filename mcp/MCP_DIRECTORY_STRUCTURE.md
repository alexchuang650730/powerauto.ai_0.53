# MCP目录结构规范

## 📁 目录组织规范

### **小型MCP (Adapter模式)**
```
/mcp/adapter/
├── local_model_mcp/          # 本地模型适配器
├── cloud_search_mcp/         # 云端搜索适配器  
├── kilocode_mcp/            # KiloCode适配器
└── cloud_edge_data_mcp/     # 云边数据适配器
```

### **大型MCP (Workflow模式)**
```
/mcp/workflow/
└── ocr_mcp/                 # OCR工作流MCP
```

## 🎯 分类标准

### **Adapter类型 (小型MCP)**
- **特点**: 单一功能，轻量级，专注特定任务
- **用途**: 作为其他系统的适配器或接口
- **示例**: 
  - `local_model_mcp` - 本地AI模型调用
  - `cloud_search_mcp` - 云端搜索服务
  - `kilocode_mcp` - 代码生成服务

### **Workflow类型 (大型MCP)**
- **特点**: 复杂工作流，多步骤处理，智能路由
- **用途**: 完整的业务流程管理
- **示例**:
  - `ocr_mcp` - 完整的OCR处理工作流

## 📊 当前状态

### ✅ **已重新组织的MCP**

#### **Adapter类型**
- ✅ `/mcp/adapter/local_model_mcp/` - 本地模型适配器
- ✅ `/mcp/adapter/cloud_search_mcp/` - 云端搜索适配器
- ✅ `/mcp/adapter/kilocode_mcp/` - KiloCode适配器
- ✅ `/mcp/adapter/cloud_edge_data_mcp/` - 云边数据适配器

#### **Workflow类型**
- ✅ `/mcp/workflow/ocr_mcp/` - OCR工作流MCP

### 🔧 **目录结构优化**
- 清理了重复的目录
- 统一了命名规范
- 按功能类型分类组织
- 便于维护和扩展

## 🚀 **扩展指南**

### **添加新的Adapter MCP**
```bash
mkdir /mcp/adapter/new_adapter_mcp/
cd /mcp/adapter/new_adapter_mcp/
# 创建标准文件结构
```

### **添加新的Workflow MCP**
```bash
mkdir /mcp/workflow/new_workflow_mcp/
cd /mcp/workflow/new_workflow_mcp/
# 创建工作流文件结构
```

这种组织方式使得MCP的功能定位更加清晰，便于开发者理解和使用。

