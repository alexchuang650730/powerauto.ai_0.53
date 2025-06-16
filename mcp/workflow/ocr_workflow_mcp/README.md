# OCR工作流MCP

## 概述

OCR工作流MCP是一个智能的光学字符识别(OCR)处理工作流，整合了多种OCR引擎和云边协同能力，为用户提供高质量、高效率的文档识别服务。

## 主要特性

### 🎯 多任务支持
- **文档OCR**: 通用文档文字识别
- **手写识别**: 手写文字识别和转换
- **表格提取**: 表格结构识别和数据提取
- **表单处理**: 表单字段识别和数据提取
- **复杂文档**: 复杂版面文档处理
- **多语言OCR**: 多语言混合文档处理

### 🔧 智能工作流
- **配置驱动**: 基于TOML/YAML/JSON配置文件的灵活配置
- **智能路由**: 根据任务类型、质量要求、隐私级别自动选择最佳处理方案
- **多步骤处理**: 输入验证 → 图像分析 → 预处理 → 适配器选择 → OCR处理 → 结果验证 → 后处理 → 质量评估 → 结果格式化
- **容错机制**: 完善的错误处理和重试机制

### 🌐 云边协同
- **本地处理**: 集成local_model_mcp，支持Tesseract、EasyOCR、PaddleOCR、Mistral等
- **云端处理**: 集成cloud_search_mcp，支持高精度云端OCR服务
- **智能选择**: 根据隐私要求、质量需求、文件大小等因素智能选择处理方式

### 📊 质量保证
- **图像预处理**: 自动图像增强、去噪、对比度调整
- **结果验证**: 置信度检查、内容验证
- **质量评估**: 综合质量评分和等级评定
- **结果后处理**: 文本清理、格式标准化

## 目录结构

```
ocr_workflow_mcp/
├── config/                     # 配置文件目录
│   ├── workflow_config.toml    # 主工作流配置
│   ├── routing_rules.yaml      # 路由规则配置
│   ├── processing_steps.json   # 处理步骤配置
│   └── quality_settings.toml   # 质量设置配置
├── src/                        # 源代码目录
│   ├── ocr_workflow_mcp.py     # 主MCP类
│   └── ocr_workflow_executor.py # 工作流执行器
├── cli.py                      # 命令行接口
├── __init__.py                 # 包初始化文件
└── README.md                   # 说明文档
```

## 快速开始

### 安装依赖

```bash
# 基础OCR依赖
pip install pytesseract easyocr paddlepaddle paddleocr

# 图像处理依赖
pip install opencv-python pillow numpy

# 配置文件依赖
pip install toml pyyaml

# 系统依赖 (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

### 基本使用

#### 1. Python API

```python
import asyncio
from ocr_workflow_mcp import OCRWorkflowMCP

async def main():
    # 创建MCP实例
    mcp = OCRWorkflowMCP()
    
    # 处理图像
    request = {
        "image_path": "/path/to/image.jpg",
        "task_type": "document_ocr",
        "quality_level": "medium",
        "privacy_level": "normal"
    }
    
    result = await mcp.process_ocr(request)
    print(f"识别结果: {result['text']}")
    print(f"置信度: {result['confidence']}")
    print(f"质量分数: {result['quality_score']}")

asyncio.run(main())
```

#### 2. 命令行接口

```bash
# 处理单个图像
python cli.py process --image /path/to/image.jpg

# 高质量处理
python cli.py process --image /path/to/image.jpg --quality high

# 手写识别
python cli.py process --image /path/to/handwriting.jpg --task-type handwriting_recognition

# 批量处理
python cli.py batch --batch-dir /path/to/images/

# 系统信息
python cli.py info

# 健康检查
python cli.py health
```

## 配置说明

### 工作流配置 (workflow_config.toml)

```toml
[workflow]
name = "OCR处理工作流"
version = "1.0"
description = "智能OCR处理工作流，支持多引擎和云边协同"

[execution]
timeout = 300
retry_count = 2
parallel_processing = false
```

### 路由规则 (routing_rules.yaml)

```yaml
routing_rules:
  task_type:
    document_ocr: "local_model_mcp"
    handwriting_recognition: "cloud_search_mcp"
    table_extraction: "local_model_mcp"
    form_processing: "local_model_mcp"
    complex_document: "cloud_search_mcp"
  
  quality_level:
    low: "local_model_mcp"
    medium: "local_model_mcp"
    high: "cloud_search_mcp"
    ultra_high: "cloud_search_mcp"
  
  privacy_level:
    low: "cloud_search_mcp"
    normal: "local_model_mcp"
    high: "local_model_mcp"

special_rules:
  force_local:
    - privacy_level: "high"
  force_cloud:
    - quality_level: "ultra_high"
    - task_type: "complex_document"

decision_weights:
  task_type: 0.2
  quality_level: 0.3
  privacy_level: 0.4
  file_size: 0.1
```

### 质量设置 (quality_settings.toml)

```toml
[quality]
min_confidence = 0.6
target_confidence = 0.8
quality_threshold = 0.7

[limits]
max_image_size_mb = 50
max_processing_time = 300
max_retry_count = 3

[preprocessing]
auto_enhance = true
denoise_threshold = 0.3
contrast_enhancement = true

[postprocessing]
remove_extra_whitespace = true
normalize_line_breaks = true
remove_special_chars = false
```

## API参考

### OCRWorkflowMCP类

#### 主要方法

- `process_ocr(request: Dict) -> Dict`: 处理OCR请求
- `batch_process_ocr(requests: List[Dict]) -> List[Dict]`: 批量处理OCR请求
- `get_capabilities() -> Dict`: 获取MCP能力
- `get_info() -> Dict`: 获取MCP信息
- `get_statistics() -> Dict`: 获取统计信息
- `health_check() -> Dict`: 健康检查
- `test_workflow(test_image_path: str) -> Dict`: 测试工作流
- `diagnose() -> Dict`: 系统诊断

#### 请求参数

```python
request = {
    "image_path": str,              # 必需：图像文件路径
    "task_type": str,               # 可选：任务类型，默认"document_ocr"
    "quality_level": str,           # 可选：质量级别，默认"medium"
    "privacy_level": str,           # 可选：隐私级别，默认"normal"
    "language": str,                # 可选：语言设置，默认"auto"
    "output_format": str,           # 可选：输出格式，默认"structured_json"
    "enable_preprocessing": bool,   # 可选：启用预处理，默认True
    "enable_postprocessing": bool,  # 可选：启用后处理，默认True
    "metadata": dict               # 可选：元数据
}
```

#### 响应格式

```python
response = {
    "success": bool,                # 处理是否成功
    "text": str,                    # 识别的文本内容
    "confidence": float,            # 置信度 (0-1)
    "processing_time": float,       # 处理时间(秒)
    "adapter_used": str,            # 使用的适配器
    "quality_score": float,         # 质量分数 (0-1)
    "metadata": dict,               # 元数据信息
    "bounding_boxes": list,         # 可选：边界框信息
    "error": str                    # 可选：错误信息
}
```

## 支持的任务类型

| 任务类型 | 描述 | 推荐适配器 |
|---------|------|-----------|
| document_ocr | 通用文档OCR | local_model_mcp |
| handwriting_recognition | 手写识别 | cloud_search_mcp |
| table_extraction | 表格提取 | local_model_mcp |
| form_processing | 表单处理 | local_model_mcp |
| complex_document | 复杂文档 | cloud_search_mcp |
| multi_language_ocr | 多语言OCR | 智能选择 |

## 支持的质量级别

| 质量级别 | 描述 | 特点 |
|---------|------|------|
| low | 低质量 | 快速处理，适合预览 |
| medium | 中等质量 | 平衡速度和质量 |
| high | 高质量 | 优先质量，可能较慢 |
| ultra_high | 超高质量 | 最高质量，使用云端处理 |

## 支持的隐私级别

| 隐私级别 | 描述 | 处理方式 |
|---------|------|---------|
| low | 低隐私 | 优先云端处理 |
| normal | 普通隐私 | 智能选择 |
| high | 高隐私 | 强制本地处理 |

## 性能优化

### 1. 图像预处理优化
- 自动检测图像质量
- 智能选择预处理策略
- 支持对比度增强、去噪、锐化等

### 2. 引擎选择优化
- 根据任务类型选择最佳OCR引擎
- 支持多引擎并行处理
- 智能结果融合

### 3. 缓存机制
- 支持结果缓存
- 避免重复处理
- 提高响应速度

## 错误处理

### 常见错误类型

1. **文件错误**
   - 文件不存在
   - 文件格式不支持
   - 文件大小超限

2. **处理错误**
   - OCR引擎不可用
   - 处理超时
   - 内存不足

3. **质量错误**
   - 置信度过低
   - 无法识别文本
   - 图像质量过差

### 错误恢复机制

- 自动重试机制
- 降级处理策略
- 详细错误报告

## 监控和诊断

### 统计信息
- 总请求数
- 成功率
- 平均处理时间
- 适配器使用分布

### 健康检查
- MCP状态
- 组件可用性
- 配置完整性

### 系统诊断
- 组件状态详情
- 配置加载状态
- 性能建议

## 扩展开发

### 添加新的OCR引擎

1. 在`ocr_workflow_executor.py`中添加引擎初始化
2. 实现引擎接口方法
3. 更新路由规则配置
4. 添加相应测试

### 添加新的处理步骤

1. 在`workflow_steps`中添加步骤名称
2. 在`_execute_step`方法中添加处理逻辑
3. 更新配置文件
4. 添加相应测试

### 自定义路由规则

1. 修改`routing_rules.yaml`配置
2. 更新`_apply_routing_rules`方法
3. 测试路由逻辑

## 故障排除

### 常见问题

1. **OCR引擎不可用**
   ```bash
   # 检查依赖安装
   pip list | grep -E "(tesseract|easyocr|paddleocr)"
   
   # 检查系统依赖
   tesseract --version
   ```

2. **配置文件错误**
   ```bash
   # 运行诊断
   python cli.py diagnose
   
   # 检查配置语法
   python -c "import toml; toml.load('config/workflow_config.toml')"
   ```

3. **性能问题**
   ```bash
   # 查看统计信息
   python cli.py info
   
   # 运行性能测试
   python cli.py test --test-image /path/to/test.jpg
   ```

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多引擎OCR处理
- 实现云边协同架构
- 提供完整的CLI接口
- 支持配置驱动的工作流

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进本项目。

## 联系方式

如有问题或建议，请联系PowerAutomation团队。

