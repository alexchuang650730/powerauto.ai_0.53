# Workflow设计和配置指南

## 🎯 Workflow设计原则

### **1. 配置驱动的工作流**
所有workflow都应该通过配置文件定义流程，而不是硬编码逻辑。

### **2. Adapter复用优先**
优先使用现有的adapter (local_model_mcp, cloud_search_mcp)，避免重复实现。

### **3. 标准化接口**
所有workflow都应该实现统一的接口规范。

## 📁 Workflow目录结构标准

```
mcp/workflow/{workflow_name}/
├── config/
│   ├── workflow_config.toml     # 主配置文件
│   ├── routing_rules.yaml       # 路由规则
│   ├── processing_steps.json    # 处理步骤定义
│   └── quality_settings.toml    # 质量和性能设置
├── src/
│   ├── {workflow_name}.py       # 主工作流类
│   ├── workflow_executor.py     # 执行器
│   ├── step_processors/         # 步骤处理器
│   └── utils/                   # 工具函数
├── tests/
│   ├── test_{workflow_name}.py  # 单元测试
│   ├── integration_tests.py     # 集成测试
│   └── performance_tests.py     # 性能测试
├── docs/
│   ├── README.md               # 使用说明
│   ├── api_reference.md        # API参考
│   └── examples/               # 使用示例
└── cli.py                      # 命令行接口
```

## ⚙️ 配置文件规范

### **workflow_config.toml**
```toml
[workflow]
name = "OCR处理工作流"
version = "1.0.0"
description = "智能OCR处理和文档分析工作流"
author = "PowerAutomation Team"

[dependencies]
adapters = ["local_model_mcp", "cloud_search_mcp"]
required_models = ["qwen", "mistral", "gemini"]

[execution]
timeout = 300  # 秒
max_retries = 3
parallel_processing = true
batch_size = 10

[monitoring]
enable_logging = true
log_level = "INFO"
metrics_collection = true
performance_tracking = true
```

### **routing_rules.yaml**
```yaml
routing_rules:
  # 基于任务类型的路由
  task_type:
    ocr_simple: "local_model_mcp"
    ocr_complex: "cloud_search_mcp"
    handwriting: "cloud_search_mcp"
    table_extraction: "cloud_search_mcp"
  
  # 基于质量要求的路由
  quality_level:
    high: "cloud_search_mcp"
    medium: "local_model_mcp"
    fast: "local_model_mcp"
  
  # 基于隐私要求的路由
  privacy_level:
    sensitive: "local_model_mcp"
    normal: "cloud_search_mcp"
    public: "cloud_search_mcp"
  
  # 基于文件大小的路由
  file_size:
    small: "local_model_mcp"    # < 5MB
    medium: "cloud_search_mcp"  # 5-20MB
    large: "cloud_search_mcp"   # > 20MB
```

### **processing_steps.json**
```json
{
  "steps": [
    {
      "id": "input_validation",
      "name": "输入验证",
      "processor": "InputValidator",
      "required": true,
      "timeout": 10,
      "retry_count": 1
    },
    {
      "id": "preprocessing",
      "name": "图像预处理",
      "processor": "ImagePreprocessor",
      "required": false,
      "timeout": 30,
      "retry_count": 2,
      "conditions": {
        "image_quality": "< 0.8"
      }
    },
    {
      "id": "adapter_selection",
      "name": "适配器选择",
      "processor": "AdapterSelector",
      "required": true,
      "timeout": 5,
      "retry_count": 1
    },
    {
      "id": "ocr_processing",
      "name": "OCR处理",
      "processor": "OCRProcessor",
      "required": true,
      "timeout": 120,
      "retry_count": 3
    },
    {
      "id": "postprocessing",
      "name": "结果后处理",
      "processor": "ResultPostprocessor",
      "required": true,
      "timeout": 30,
      "retry_count": 2
    },
    {
      "id": "quality_check",
      "name": "质量检查",
      "processor": "QualityChecker",
      "required": false,
      "timeout": 15,
      "retry_count": 1,
      "conditions": {
        "quality_check_enabled": true
      }
    }
  ],
  "error_handling": {
    "on_step_failure": "retry_or_skip",
    "on_critical_failure": "abort_workflow",
    "fallback_adapter": "local_model_mcp"
  }
}
```

### **quality_settings.toml**
```toml
[quality]
# 质量阈值设置
min_confidence = 0.8
min_accuracy = 0.9
max_processing_time = 300

[performance]
# 性能设置
enable_caching = true
cache_ttl = 3600
enable_compression = true
max_memory_usage = "2GB"

[cost_optimization]
# 成本优化设置
prefer_local = true
cost_threshold = 0.01  # 美元
quality_cost_balance = 0.7  # 0-1之间，越高越偏向质量

[fallback]
# 降级策略
enable_fallback = true
fallback_quality_threshold = 0.6
max_fallback_attempts = 2
```

## 🔧 Workflow基础类实现

### **BaseWorkflow类**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import toml
import yaml
import json
import logging

class BaseWorkflow(ABC):
    """工作流基础类"""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.config = self._load_config()
        self.routing_rules = self._load_routing_rules()
        self.processing_steps = self._load_processing_steps()
        self.quality_settings = self._load_quality_settings()
        
        # 初始化adapter
        self.adapters = self._initialize_adapters()
        
        # 设置日志
        self.logger = self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        config_path = f"{self.config_dir}/workflow_config.toml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return toml.load(f)
    
    def _load_routing_rules(self) -> Dict[str, Any]:
        """加载路由规则"""
        rules_path = f"{self.config_dir}/routing_rules.yaml"
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_processing_steps(self) -> Dict[str, Any]:
        """加载处理步骤"""
        steps_path = f"{self.config_dir}/processing_steps.json"
        with open(steps_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_quality_settings(self) -> Dict[str, Any]:
        """加载质量设置"""
        quality_path = f"{self.config_dir}/quality_settings.toml"
        with open(quality_path, 'r', encoding='utf-8') as f:
            return toml.load(f)
    
    @abstractmethod
    def _initialize_adapters(self) -> Dict[str, Any]:
        """初始化所需的adapter"""
        pass
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(self.config['workflow']['name'])
        logger.setLevel(self.config['monitoring']['log_level'])
        return logger
    
    def select_adapter(self, request: Dict[str, Any]) -> str:
        """根据路由规则选择adapter"""
        # 实现路由逻辑
        pass
    
    def execute_step(self, step_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个处理步骤"""
        # 实现步骤执行逻辑
        pass
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整工作流"""
        context = {"request": request, "results": {}}
        
        try:
            for step in self.processing_steps['steps']:
                if self._should_execute_step(step, context):
                    result = self.execute_step(step, context)
                    context['results'][step['id']] = result
            
            return self._format_final_result(context)
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return self._handle_workflow_error(e, context)
    
    @abstractmethod
    def _should_execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """判断是否应该执行某个步骤"""
        pass
    
    @abstractmethod
    def _format_final_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """格式化最终结果"""
        pass
    
    @abstractmethod
    def _handle_workflow_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流错误"""
        pass
```

## 🧪 测试框架

### **测试配置**
```python
# tests/test_config.py
import pytest
from pathlib import Path

@pytest.fixture
def test_config_dir():
    """测试配置目录"""
    return Path(__file__).parent / "test_configs"

@pytest.fixture
def sample_request():
    """示例请求"""
    return {
        "task_type": "ocr_simple",
        "image_path": "/path/to/test_image.jpg",
        "quality_level": "high",
        "privacy_level": "normal"
    }
```

### **单元测试示例**
```python
# tests/test_workflow.py
import pytest
from src.ocr_workflow import OCRWorkflow

class TestOCRWorkflow:
    
    def test_adapter_selection(self, test_config_dir, sample_request):
        """测试adapter选择逻辑"""
        workflow = OCRWorkflow(test_config_dir)
        adapter = workflow.select_adapter(sample_request)
        assert adapter in ["local_model_mcp", "cloud_search_mcp"]
    
    def test_workflow_execution(self, test_config_dir, sample_request):
        """测试工作流执行"""
        workflow = OCRWorkflow(test_config_dir)
        result = workflow.execute(sample_request)
        assert result['success'] is True
        assert 'ocr_result' in result
    
    def test_error_handling(self, test_config_dir):
        """测试错误处理"""
        workflow = OCRWorkflow(test_config_dir)
        invalid_request = {"invalid": "request"}
        result = workflow.execute(invalid_request)
        assert result['success'] is False
        assert 'error' in result
```

### **性能测试示例**
```python
# tests/performance_tests.py
import time
import pytest
from src.ocr_workflow import OCRWorkflow

class TestPerformance:
    
    def test_processing_time(self, test_config_dir, sample_request):
        """测试处理时间"""
        workflow = OCRWorkflow(test_config_dir)
        
        start_time = time.time()
        result = workflow.execute(sample_request)
        end_time = time.time()
        
        processing_time = end_time - start_time
        max_time = workflow.quality_settings['quality']['max_processing_time']
        
        assert processing_time < max_time
        assert result['success'] is True
    
    def test_batch_processing(self, test_config_dir):
        """测试批量处理性能"""
        workflow = OCRWorkflow(test_config_dir)
        requests = [sample_request for _ in range(10)]
        
        start_time = time.time()
        results = workflow.batch_execute(requests)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / len(requests)
        assert avg_time < 30  # 平均每个请求不超过30秒
```

## 📋 开发检查清单

### **新Workflow开发清单**
- [ ] 创建标准目录结构
- [ ] 编写配置文件 (config/, routing_rules, processing_steps, quality_settings)
- [ ] 实现BaseWorkflow子类
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 编写性能测试
- [ ] 创建CLI接口
- [ ] 编写文档和示例
- [ ] 性能基准测试
- [ ] 代码审查和优化

### **配置验证清单**
- [ ] 配置文件语法正确
- [ ] 路由规则覆盖所有场景
- [ ] 处理步骤逻辑合理
- [ ] 质量设置符合要求
- [ ] 错误处理策略完善
- [ ] 性能参数合理
- [ ] 监控配置完整

这个指南提供了完整的workflow设计和配置框架，确保所有workflow都能标准化开发和部署。

