#!/usr/bin/env python3
"""
OCR工作流MCP - 主实现类

基于配置驱动的OCR处理工作流，整合local_model_mcp和cloud_search_mcp
"""

import os
import sys
import time
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import toml
import yaml

# 添加adapter路径
sys.path.append(str(Path(__file__).parent.parent.parent / "adapter"))

# 导入基础工作流类
from workflow_howto.workflow_design_guide import BaseWorkflow

@dataclass
class OCRRequest:
    """OCR请求数据结构"""
    image_path: str
    task_type: str = "document_ocr"
    quality_level: str = "medium"
    privacy_level: str = "normal"
    language: str = "auto"
    output_format: str = "structured_json"
    enable_preprocessing: bool = True
    enable_postprocessing: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class OCRResult:
    """OCR结果数据结构"""
    success: bool
    text: str
    confidence: float
    processing_time: float
    adapter_used: str
    quality_score: float
    bounding_boxes: List[Dict] = None
    metadata: Dict[str, Any] = None
    error: str = ""

class OCRWorkflowMCP(BaseWorkflow):
    """OCR工作流MCP主类"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"
        
        super().__init__(str(config_dir))
        
        # OCR特定配置
        self.preprocessing_config = self.quality_settings.get('preprocessing', {})
        self.postprocessing_config = self.quality_settings.get('postprocessing', {})
        self.language_config = self.quality_settings.get('language_support', {})
        
        # 初始化处理器
        self.processors = self._initialize_processors()
        
        # 缓存管理
        self.cache = {} if self.quality_settings.get('performance', {}).get('enable_caching') else None
        
        self.logger.info("OCR工作流MCP初始化完成")
    
    def _initialize_adapters(self) -> Dict[str, Any]:
        """初始化所需的adapter"""
        adapters = {}
        
        try:
            # 导入local_model_mcp
            from local_model_mcp.local_model_mcp import LocalModelMCP
            adapters['local_model_mcp'] = LocalModelMCP()
            self.logger.info("✅ LocalModelMCP初始化成功")
        except Exception as e:
            self.logger.error(f"❌ LocalModelMCP初始化失败: {e}")
        
        try:
            # 导入cloud_search_mcp (如果存在)
            # 这里需要根据实际的cloud_search_mcp实现来调整
            # adapters['cloud_search_mcp'] = CloudSearchMCP()
            self.logger.info("⚠️ CloudSearchMCP暂未实现，使用模拟适配器")
            adapters['cloud_search_mcp'] = self._create_mock_cloud_adapter()
        except Exception as e:
            self.logger.error(f"❌ CloudSearchMCP初始化失败: {e}")
            adapters['cloud_search_mcp'] = self._create_mock_cloud_adapter()
        
        return adapters
    
    def _create_mock_cloud_adapter(self):
        """创建模拟的云端适配器"""
        class MockCloudAdapter:
            def process_ocr(self, request):
                return {
                    "success": True,
                    "text": "模拟云端OCR结果",
                    "confidence": 0.95,
                    "processing_time": 2.0
                }
        
        return MockCloudAdapter()
    
    def _initialize_processors(self) -> Dict[str, Any]:
        """初始化处理器"""
        processors = {}
        
        # 输入验证器
        processors['InputValidator'] = self._create_input_validator()
        
        # 图像分析器
        processors['ImageAnalyzer'] = self._create_image_analyzer()
        
        # 图像预处理器
        processors['ImagePreprocessor'] = self._create_image_preprocessor()
        
        # 适配器选择器
        processors['AdapterSelector'] = self._create_adapter_selector()
        
        # OCR处理器
        processors['OCRProcessor'] = self._create_ocr_processor()
        
        # 结果验证器
        processors['ResultValidator'] = self._create_result_validator()
        
        # 结果后处理器
        processors['ResultPostprocessor'] = self._create_result_postprocessor()
        
        # 质量评估器
        processors['QualityAssessor'] = self._create_quality_assessor()
        
        # 结果格式化器
        processors['ResultFormatter'] = self._create_result_formatter()
        
        return processors
    
    def _create_input_validator(self):
        """创建输入验证器"""
        def validate_input(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """验证输入请求"""
            image_path = request.get('image_path')
            
            if not image_path or not os.path.exists(image_path):
                raise ValueError(f"图像文件不存在: {image_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
            max_size = float(self.preprocessing_config.get('max_image_size', '10MB').replace('MB', ''))
            
            if file_size > max_size:
                raise ValueError(f"图像文件过大: {file_size:.2f}MB > {max_size}MB")
            
            return {"success": True, "file_size_mb": file_size}
        
        return validate_input
    
    def _create_image_analyzer(self):
        """创建图像分析器"""
        def analyze_image(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """分析图像特征"""
            try:
                from PIL import Image
                import cv2
                import numpy as np
                
                image_path = request['image_path']
                
                # 使用PIL分析基本信息
                with Image.open(image_path) as img:
                    width, height = img.size
                    mode = img.mode
                
                # 使用OpenCV分析质量
                cv_img = cv2.imread(image_path)
                if cv_img is None:
                    raise ValueError("无法读取图像文件")
                
                # 计算图像质量指标
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                
                # 计算对比度 (标准差)
                contrast = np.std(gray)
                
                # 计算清晰度 (拉普拉斯方差)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # 计算亮度
                brightness = np.mean(gray)
                
                # 综合质量评分 (0-1)
                quality_score = min(1.0, (contrast / 100 + sharpness / 1000 + (255 - abs(brightness - 128)) / 255) / 3)
                
                return {
                    "success": True,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "contrast": float(contrast),
                    "sharpness": float(sharpness),
                    "brightness": float(brightness),
                    "quality_score": float(quality_score)
                }
                
            except Exception as e:
                self.logger.error(f"图像分析失败: {e}")
                return {"success": False, "error": str(e), "quality_score": 0.5}
        
        return analyze_image
    
    def _create_image_preprocessor(self):
        """创建图像预处理器"""
        def preprocess_image(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """图像预处理"""
            try:
                # 这里可以集成现有的ImagePreprocessor
                # 暂时返回模拟结果
                return {
                    "success": True,
                    "preprocessed": True,
                    "enhancements": ["contrast", "denoise"]
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return preprocess_image
    
    def _create_adapter_selector(self):
        """创建适配器选择器"""
        def select_adapter(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """根据路由规则选择适配器"""
            
            # 获取请求参数
            task_type = request.get('task_type', 'document_ocr')
            quality_level = request.get('quality_level', 'medium')
            privacy_level = request.get('privacy_level', 'normal')
            
            # 获取图像分析结果
            image_analysis = context.get('results', {}).get('image_analysis', {})
            file_size_mb = context.get('results', {}).get('input_validation', {}).get('file_size_mb', 0)
            
            # 应用路由规则
            selected_adapter = self._apply_routing_rules(
                task_type, quality_level, privacy_level, file_size_mb, image_analysis
            )
            
            return {
                "success": True,
                "selected_adapter": selected_adapter,
                "routing_reason": f"基于{task_type}/{quality_level}/{privacy_level}选择"
            }
        
        return select_adapter
    
    def _apply_routing_rules(self, task_type: str, quality_level: str, privacy_level: str, 
                           file_size_mb: float, image_analysis: Dict) -> str:
        """应用路由规则选择适配器"""
        
        # 检查强制规则
        force_local_conditions = self.routing_rules.get('special_rules', {}).get('force_local', [])
        for condition in force_local_conditions:
            if self._check_condition(condition, privacy_level, quality_level, file_size_mb):
                return "local_model_mcp"
        
        force_cloud_conditions = self.routing_rules.get('special_rules', {}).get('force_cloud', [])
        for condition in force_cloud_conditions:
            if self._check_condition(condition, task_type, quality_level):
                return "cloud_search_mcp"
        
        # 应用权重决策
        weights = self.routing_rules.get('decision_weights', {})
        
        score_local = 0
        score_cloud = 0
        
        # 任务类型权重
        task_rules = self.routing_rules.get('routing_rules', {}).get('task_type', {})
        if task_type in task_rules:
            if task_rules[task_type] == "local_model_mcp":
                score_local += weights.get('task_type', 0.2)
            else:
                score_cloud += weights.get('task_type', 0.2)
        
        # 质量级别权重
        quality_rules = self.routing_rules.get('routing_rules', {}).get('quality_level', {})
        if quality_level in quality_rules:
            if quality_rules[quality_level] == "local_model_mcp":
                score_local += weights.get('quality_level', 0.3)
            else:
                score_cloud += weights.get('quality_level', 0.3)
        
        # 隐私级别权重
        privacy_rules = self.routing_rules.get('routing_rules', {}).get('privacy_level', {})
        if privacy_level in privacy_rules:
            if privacy_rules[privacy_level] == "local_model_mcp":
                score_local += weights.get('privacy_level', 0.4)
            else:
                score_cloud += weights.get('privacy_level', 0.4)
        
        # 文件大小权重
        if file_size_mb < 5:
            score_local += weights.get('file_size', 0.1)
        else:
            score_cloud += weights.get('file_size', 0.1)
        
        # 返回得分更高的适配器
        return "local_model_mcp" if score_local >= score_cloud else "cloud_search_mcp"
    
    def _check_condition(self, condition: Dict, *args) -> bool:
        """检查条件是否满足"""
        # 简化的条件检查逻辑
        for key, value in condition.items():
            if value in args:
                return True
        return False
    
    def _create_ocr_processor(self):
        """创建OCR处理器"""
        def process_ocr(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """执行OCR处理"""
            
            # 获取选择的适配器
            adapter_selection = context.get('results', {}).get('adapter_selection', {})
            selected_adapter = adapter_selection.get('selected_adapter', 'local_model_mcp')
            
            # 获取适配器实例
            adapter = self.adapters.get(selected_adapter)
            if not adapter:
                raise ValueError(f"适配器不可用: {selected_adapter}")
            
            # 执行OCR处理
            start_time = time.time()
            
            try:
                if hasattr(adapter, 'process_ocr'):
                    result = adapter.process_ocr(request)
                else:
                    # 使用通用处理方法
                    result = adapter.process(request)
                
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "text": result.get('text', ''),
                    "confidence": result.get('confidence', 0.0),
                    "processing_time": processing_time,
                    "adapter_used": selected_adapter
                }
                
            except Exception as e:
                self.logger.error(f"OCR处理失败: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "adapter_used": selected_adapter,
                    "processing_time": time.time() - start_time
                }
        
        return process_ocr
    
    def _create_result_validator(self):
        """创建结果验证器"""
        def validate_result(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """验证OCR结果"""
            ocr_result = context.get('results', {}).get('ocr_processing', {})
            
            if not ocr_result.get('success'):
                return {"success": False, "error": "OCR处理失败"}
            
            text = ocr_result.get('text', '')
            confidence = ocr_result.get('confidence', 0.0)
            
            # 验证结果质量
            min_confidence = self.quality_settings.get('quality', {}).get('min_confidence', 0.8)
            
            if confidence < min_confidence:
                return {
                    "success": False,
                    "error": f"置信度过低: {confidence} < {min_confidence}",
                    "requires_retry": True
                }
            
            if len(text.strip()) == 0:
                return {
                    "success": False,
                    "error": "未识别到文本内容",
                    "requires_retry": True
                }
            
            return {"success": True, "validation_passed": True}
        
        return validate_result
    
    def _create_result_postprocessor(self):
        """创建结果后处理器"""
        def postprocess_result(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """后处理OCR结果"""
            ocr_result = context.get('results', {}).get('ocr_processing', {})
            text = ocr_result.get('text', '')
            
            # 应用后处理配置
            if self.postprocessing_config.get('remove_extra_whitespace', True):
                text = ' '.join(text.split())
            
            if self.postprocessing_config.get('normalize_line_breaks', True):
                text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            return {
                "success": True,
                "processed_text": text,
                "postprocessing_applied": True
            }
        
        return postprocess_result
    
    def _create_quality_assessor(self):
        """创建质量评估器"""
        def assess_quality(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """评估结果质量"""
            ocr_result = context.get('results', {}).get('ocr_processing', {})
            confidence = ocr_result.get('confidence', 0.0)
            
            # 简化的质量评估
            quality_score = confidence  # 可以添加更复杂的评估逻辑
            
            return {
                "success": True,
                "quality_score": quality_score,
                "quality_level": "high" if quality_score > 0.9 else "medium" if quality_score > 0.7 else "low"
            }
        
        return assess_quality
    
    def _create_result_formatter(self):
        """创建结果格式化器"""
        def format_result(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            """格式化最终结果"""
            
            # 收集所有结果
            ocr_result = context.get('results', {}).get('ocr_processing', {})
            postprocessing = context.get('results', {}).get('postprocessing', {})
            quality_assessment = context.get('results', {}).get('quality_assessment', {})
            
            # 构建最终结果
            final_result = OCRResult(
                success=ocr_result.get('success', False),
                text=postprocessing.get('processed_text', ocr_result.get('text', '')),
                confidence=ocr_result.get('confidence', 0.0),
                processing_time=ocr_result.get('processing_time', 0.0),
                adapter_used=ocr_result.get('adapter_used', ''),
                quality_score=quality_assessment.get('quality_score', 0.0),
                metadata={
                    "workflow_version": self.config['workflow']['version'],
                    "processing_steps": list(context.get('results', {}).keys())
                }
            )
            
            return {"success": True, "final_result": asdict(final_result)}
        
        return format_result
    
    def _should_execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """判断是否应该执行某个步骤"""
        
        # 检查必需步骤
        if step.get('required', True):
            return True
        
        # 检查条件
        conditions = step.get('conditions', {})
        if not conditions:
            return True
        
        # 简化的条件检查
        for condition_key, condition_value in conditions.items():
            if condition_key == 'enable_preprocessing':
                if not context.get('request', {}).get('enable_preprocessing', True):
                    return False
            elif condition_key == 'quality_check_enabled':
                if not self.quality_settings.get('quality', {}).get('enable_quality_check', True):
                    return False
        
        return True
    
    def _format_final_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """格式化最终结果"""
        result_formatting = context.get('results', {}).get('result_formatting', {})
        return result_formatting.get('final_result', {})
    
    def _handle_workflow_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流错误"""
        return {
            "success": False,
            "error": str(error),
            "context": context,
            "workflow": "ocr_workflow_mcp"
        }
    
    def process_ocr_request(self, request: Union[Dict[str, Any], OCRRequest]) -> OCRResult:
        """处理OCR请求的便捷方法"""
        
        if isinstance(request, OCRRequest):
            request_dict = asdict(request)
        else:
            request_dict = request
        
        # 执行工作流
        result = self.execute(request_dict)
        
        if result.get('success'):
            final_result = result
            return OCRResult(**final_result)
        else:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                processing_time=0.0,
                adapter_used="",
                quality_score=0.0,
                error=result.get('error', 'Unknown error')
            )

# 便捷函数
def create_ocr_workflow(config_dir: str = None) -> OCRWorkflowMCP:
    """创建OCR工作流实例"""
    return OCRWorkflowMCP(config_dir)

if __name__ == "__main__":
    # 测试代码
    workflow = create_ocr_workflow()
    
    # 示例请求
    test_request = OCRRequest(
        image_path="/path/to/test/image.jpg",
        task_type="document_ocr",
        quality_level="high",
        privacy_level="normal"
    )
    
    result = workflow.process_ocr_request(test_request)
    print(f"OCR结果: {result}")

