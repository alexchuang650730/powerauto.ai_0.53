#!/usr/bin/env python3
"""
OCR工作流执行器 - 真实版本

集成Local Model MCP的实际OCR功能到workflow架构中
"""

import os
import sys
import time
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

@dataclass
class WorkflowOCRRequest:
    """工作流OCR请求"""
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
class WorkflowOCRResult:
    """工作流OCR结果"""
    success: bool
    text: str
    confidence: float
    processing_time: float
    adapter_used: str
    quality_score: float
    workflow_steps: List[str] = None
    bounding_boxes: List[Dict] = None
    metadata: Dict[str, Any] = None
    error: str = ""

class OCRWorkflowExecutor:
    """OCR工作流执行器 - 真实版本"""
    
    def __init__(self, config_dir: str = None):
        self.logger = logging.getLogger(__name__)
        
        # 配置目录
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = Path(config_dir)
        
        # 加载配置
        self._load_configurations()
        
        # 初始化OCR组件
        self._initialize_ocr_components()
        
        # 工作流步骤定义
        self.workflow_steps = [
            "input_validation",
            "image_analysis", 
            "preprocessing",
            "adapter_selection",
            "ocr_processing",
            "result_validation",
            "postprocessing",
            "quality_assessment",
            "result_formatting"
        ]
        
        self.logger.info("OCR工作流执行器(真实版)初始化完成")
    
    def _load_configurations(self):
        """加载配置文件"""
        import toml
        import yaml
        
        try:
            # 加载主配置
            workflow_config_path = self.config_dir / "workflow_config.toml"
            if workflow_config_path.exists():
                with open(workflow_config_path, 'r', encoding='utf-8') as f:
                    self.workflow_config = toml.load(f)
            else:
                self.workflow_config = self._get_default_workflow_config()
            
            # 加载路由规则
            routing_rules_path = self.config_dir / "routing_rules.yaml"
            if routing_rules_path.exists():
                with open(routing_rules_path, 'r', encoding='utf-8') as f:
                    self.routing_rules = yaml.safe_load(f)
            else:
                self.routing_rules = self._get_default_routing_rules()
            
            # 加载处理步骤
            processing_steps_path = self.config_dir / "processing_steps.json"
            if processing_steps_path.exists():
                with open(processing_steps_path, 'r', encoding='utf-8') as f:
                    self.processing_steps = json.load(f)
            else:
                self.processing_steps = self._get_default_processing_steps()
            
            # 加载质量设置
            quality_settings_path = self.config_dir / "quality_settings.toml"
            if quality_settings_path.exists():
                with open(quality_settings_path, 'r', encoding='utf-8') as f:
                    self.quality_settings = toml.load(f)
            else:
                self.quality_settings = self._get_default_quality_settings()
                
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            self._load_default_configurations()
    
    def _initialize_ocr_components(self):
        """初始化OCR组件"""
        self.ocr_components = {}
        
        try:
            # 初始化Local Model MCP
            from mcp.adapter.local_model_mcp.local_model_mcp import LocalModelMCP
            self.ocr_components['local_model_mcp'] = LocalModelMCP()
            self.logger.info("✅ Local Model MCP初始化成功")
        except Exception as e:
            self.logger.error(f"❌ Local Model MCP初始化失败: {e}")
        
        try:
            # 初始化图像预处理器
            from mcp.adapter.local_model_mcp.image_preprocessor import ImagePreprocessor
            self.ocr_components['preprocessor'] = ImagePreprocessor()
            self.logger.info("✅ 图像预处理器初始化成功")
        except Exception as e:
            self.logger.error(f"❌ 图像预处理器初始化失败: {e}")
        
        try:
            # 初始化多引擎OCR管理器
            from mcp.adapter.local_model_mcp.multi_engine_ocr import MultiEngineOCRManager
            self.ocr_components['multi_engine'] = MultiEngineOCRManager()
            self.logger.info("✅ 多引擎OCR管理器初始化成功")
        except Exception as e:
            self.logger.error(f"❌ 多引擎OCR管理器初始化失败: {e}")
        
        try:
            # 初始化Tesseract优化器
            from mcp.adapter.local_model_mcp.tesseract_optimizer import TesseractOptimizer
            self.ocr_components['tesseract_optimizer'] = TesseractOptimizer()
            self.logger.info("✅ Tesseract优化器初始化成功")
        except Exception as e:
            self.logger.error(f"❌ Tesseract优化器初始化失败: {e}")
        
        try:
            # 初始化Mistral OCR引擎
            from mcp.adapter.local_model_mcp.mistral_ocr_engine import MistralOCREngine
            self.ocr_components['mistral_engine'] = MistralOCREngine()
            self.logger.info("✅ Mistral OCR引擎初始化成功")
        except Exception as e:
            self.logger.error(f"❌ Mistral OCR引擎初始化失败: {e}")
    
    async def execute_workflow(self, request: WorkflowOCRRequest) -> WorkflowOCRResult:
        """执行完整的OCR工作流"""
        start_time = time.time()
        context = {
            "request": asdict(request),
            "results": {},
            "metadata": {
                "workflow_id": self._generate_workflow_id(),
                "start_time": start_time
            }
        }
        
        executed_steps = []
        
        try:
            # 执行工作流步骤
            for step_name in self.workflow_steps:
                step_start = time.time()
                
                try:
                    step_result = await self._execute_step(step_name, context)
                    context["results"][step_name] = step_result
                    executed_steps.append(step_name)
                    
                    step_time = time.time() - step_start
                    self.logger.info(f"✅ 步骤完成: {step_name} ({step_time:.2f}s)")
                    
                    # 检查是否需要提前终止
                    if not step_result.get("success", True):
                        if step_result.get("critical_failure", False):
                            break
                        # 非关键失败，继续执行
                    
                except Exception as e:
                    self.logger.error(f"❌ 步骤失败: {step_name} - {e}")
                    context["results"][step_name] = {
                        "success": False,
                        "error": str(e),
                        "critical_failure": True
                    }
                    break
            
            # 构建最终结果
            total_time = time.time() - start_time
            result = self._build_final_result(context, executed_steps, total_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return WorkflowOCRResult(
                success=False,
                text="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                adapter_used="none",
                quality_score=0.0,
                workflow_steps=executed_steps,
                error=str(e)
            )
    
    async def _execute_step(self, step_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个工作流步骤"""
        
        if step_name == "input_validation":
            return self._validate_input(context)
        elif step_name == "image_analysis":
            return await self._analyze_image(context)
        elif step_name == "preprocessing":
            return await self._preprocess_image(context)
        elif step_name == "adapter_selection":
            return self._select_adapter(context)
        elif step_name == "ocr_processing":
            return await self._process_ocr(context)
        elif step_name == "result_validation":
            return self._validate_result(context)
        elif step_name == "postprocessing":
            return self._postprocess_result(context)
        elif step_name == "quality_assessment":
            return self._assess_quality(context)
        elif step_name == "result_formatting":
            return self._format_result(context)
        else:
            raise ValueError(f"未知的工作流步骤: {step_name}")
    
    def _validate_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """验证输入"""
        request = context["request"]
        image_path = request.get("image_path")
        
        if not image_path:
            return {
                "success": False,
                "error": "缺少图像文件路径",
                "critical_failure": True
            }
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图像文件不存在: {image_path}",
                "critical_failure": True
            }
        
        # 检查文件大小
        try:
            file_size = os.path.getsize(image_path)
            file_size_mb = file_size / (1024 * 1024)
            
            max_size_mb = self.quality_settings.get("limits", {}).get("max_image_size_mb", 50)
            if file_size_mb > max_size_mb:
                return {
                    "success": False,
                    "error": f"文件过大: {file_size_mb:.1f}MB > {max_size_mb}MB",
                    "critical_failure": True
                }
            
            return {
                "success": True,
                "file_size_mb": file_size_mb,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件访问失败: {e}",
                "critical_failure": True
            }
    
    async def _analyze_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析图像特征"""
        try:
            image_path = context["request"]["image_path"]
            
            # 使用PIL分析图像基本信息
            from PIL import Image
            import numpy as np
            
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                
                # 转换为numpy数组进行质量分析
                img_array = np.array(img.convert('RGB'))
                
                # 计算图像质量指标
                contrast = np.std(img_array)
                brightness = np.mean(img_array)
                
                # 简单的锐度估算（拉普拉斯方差）
                gray = np.mean(img_array, axis=2)
                laplacian = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
                sharpness = np.var(np.convolve(gray.flatten(), laplacian.flatten(), mode='valid'))
                
                # 计算综合质量分数
                quality_score = min(1.0, (contrast / 100 + sharpness / 1000 + (brightness - 128) / 128) / 3)
                quality_score = max(0.0, quality_score)
            
            return {
                "success": True,
                "width": width,
                "height": height,
                "mode": mode,
                "contrast": float(contrast),
                "sharpness": float(sharpness),
                "brightness": float(brightness),
                "quality_score": quality_score
            }
            
        except Exception as e:
            self.logger.error(f"图像分析失败: {e}")
            return {"success": False, "error": str(e), "quality_score": 0.5}
    
    async def _preprocess_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """图像预处理"""
        if not context["request"].get("enable_preprocessing", True):
            return {"success": True, "preprocessing_skipped": True}
        
        try:
            preprocessor = self.ocr_components.get('preprocessor')
            if not preprocessor:
                return {"success": False, "error": "图像预处理器不可用"}
            
            image_path = context["request"]["image_path"]
            image_analysis = context["results"].get("image_analysis", {})
            
            # 根据图像质量决定是否需要预处理
            quality_score = image_analysis.get("quality_score", 0.5)
            skip_threshold = self.quality_settings.get("preprocessing", {}).get("quality_skip_threshold", 0.9)
            
            if quality_score > skip_threshold:
                return {
                    "success": True,
                    "preprocessing_skipped": True,
                    "reason": f"图像质量良好 ({quality_score:.2f})"
                }
            
            # 执行预处理
            processed_result = await preprocessor.process_image(image_path)
            
            return {
                "success": True,
                "preprocessed_path": processed_result.get("output_path"),
                "enhancements": processed_result.get("applied_enhancements", []),
                "preprocessing_time": processed_result.get("processing_time", 0)
            }
            
        except Exception as e:
            self.logger.error(f"图像预处理失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _select_adapter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """选择适配器"""
        request = context["request"]
        
        # 获取请求参数
        task_type = request.get("task_type", "document_ocr")
        quality_level = request.get("quality_level", "medium")
        privacy_level = request.get("privacy_level", "normal")
        
        # 获取图像分析结果
        image_analysis = context["results"].get("image_analysis", {})
        file_size_mb = context["results"].get("input_validation", {}).get("file_size_mb", 0)
        
        # 应用路由规则
        selected_adapter = self._apply_routing_rules(
            task_type, quality_level, privacy_level, file_size_mb, image_analysis
        )
        
        return {
            "success": True,
            "selected_adapter": selected_adapter,
            "routing_reason": f"基于{task_type}/{quality_level}/{privacy_level}选择"
        }
    
    async def _process_ocr(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行OCR处理"""
        adapter_selection = context["results"].get("adapter_selection", {})
        selected_adapter = adapter_selection.get("selected_adapter", "local_model_mcp")
        
        # 获取图像路径
        preprocessing_result = context["results"].get("preprocessing", {})
        if preprocessing_result.get("success") and preprocessing_result.get("preprocessed_path"):
            image_path = preprocessing_result["preprocessed_path"]
        else:
            image_path = context["request"]["image_path"]
        
        start_time = time.time()
        
        try:
            if selected_adapter == "local_model_mcp":
                result = await self._process_with_local_adapter(image_path, context)
            elif selected_adapter == "cloud_search_mcp":
                result = await self._process_with_cloud_adapter(image_path, context)
            else:
                raise ValueError(f"未知的适配器: {selected_adapter}")
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "processing_time": processing_time,
                "adapter_used": selected_adapter,
                "engine_details": result.get("engine_details", {})
            }
            
        except Exception as e:
            self.logger.error(f"OCR处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "adapter_used": selected_adapter,
                "processing_time": time.time() - start_time
            }
    
    async def _process_with_local_adapter(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用本地适配器处理"""
        request = context["request"]
        task_type = request.get("task_type", "document_ocr")
        
        # 获取Local Model MCP实例
        local_mcp = self.ocr_components.get('local_model_mcp')
        if not local_mcp:
            raise Exception("Local Model MCP不可用")
        
        # 确保MCP已初始化
        if not local_mcp.initialized:
            await local_mcp.initialize()
        
        # 读取图像数据
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 调用OCR处理
        result = await local_mcp.ocr_processing(
            image_data,
            task_type=task_type,
            language=request.get("language", "auto")
        )
        
        if result["success"]:
            ocr_result = result["result"]
            return {
                "text": ocr_result.get("text", ""),
                "confidence": ocr_result.get("confidence", 0.0),
                "engine_details": {
                    "provider": "local_model_mcp",
                    "engines": ocr_result.get("engines_used", []),
                    "processing_time": result.get("processing_time", 0)
                }
            }
        else:
            raise Exception(f"Local MCP OCR失败: {result.get('error', '未知错误')}")
    
    async def _process_with_cloud_adapter(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用云端适配器处理"""
        # 这里应该调用cloud_search_mcp，目前返回模拟结果
        await asyncio.sleep(0.3)  # 模拟网络延迟
        
        return {
            "text": f"云端OCR结果 - {os.path.basename(image_path)}",
            "confidence": 0.95,
            "engine_details": {"provider": "cloud_search_mcp", "model": "vision-pro"}
        }
    
    def _validate_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """验证OCR结果"""
        ocr_result = context["results"].get("ocr_processing", {})
        
        if not ocr_result.get("success"):
            return {"success": False, "error": "OCR处理失败"}
        
        text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0.0)
        
        # 验证结果质量
        min_confidence = self.quality_settings.get("quality", {}).get("min_confidence", 0.6)
        
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
    
    def _postprocess_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """后处理OCR结果"""
        if not context["request"].get("enable_postprocessing", True):
            return {"success": True, "postprocessing_skipped": True}
        
        ocr_result = context["results"].get("ocr_processing", {})
        text = ocr_result.get("text", "")
        
        # 应用后处理规则
        postprocess_config = self.quality_settings.get("postprocessing", {})
        
        if postprocess_config.get("text_cleaning", {}).get("remove_extra_whitespace", True):
            text = ' '.join(text.split())
        
        if postprocess_config.get("text_cleaning", {}).get("normalize_line_breaks", True):
            text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return {
            "success": True,
            "processed_text": text,
            "postprocessing_applied": True
        }
    
    def _assess_quality(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估结果质量"""
        ocr_result = context["results"].get("ocr_processing", {})
        confidence = ocr_result.get("confidence", 0.0)
        
        # 获取文本长度
        postprocess_result = context["results"].get("postprocessing", {})
        if postprocess_result.get("success"):
            text = postprocess_result.get("processed_text", "")
        else:
            text = ocr_result.get("text", "")
        
        text_length = len(text.strip())
        
        # 计算综合质量分数
        quality_score = self._calculate_quality_score(confidence, text_length, context)
        
        return {
            "success": True,
            "quality_score": quality_score,
            "quality_level": self._get_quality_level(quality_score),
            "text_length": text_length
        }
    
    def _format_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """格式化最终结果"""
        request = context["request"]
        output_format = request.get("output_format", "structured_json")
        
        # 收集所有结果数据
        ocr_result = context["results"].get("ocr_processing", {})
        postprocess_result = context["results"].get("postprocessing", {})
        quality_result = context["results"].get("quality_assessment", {})
        
        # 获取最终文本
        if postprocess_result.get("success"):
            final_text = postprocess_result.get("processed_text", "")
        else:
            final_text = ocr_result.get("text", "")
        
        # 根据输出格式格式化
        if output_format == "plain_text":
            formatted_result = final_text
        elif output_format == "structured_json":
            formatted_result = {
                "text": final_text,
                "confidence": ocr_result.get("confidence", 0.0),
                "quality_score": quality_result.get("quality_score", 0.0),
                "metadata": {
                    "adapter_used": ocr_result.get("adapter_used", ""),
                    "processing_time": ocr_result.get("processing_time", 0.0),
                    "workflow_steps": list(context["results"].keys())
                }
            }
        else:
            formatted_result = final_text
        
        return {
            "success": True,
            "formatted_result": formatted_result,
            "output_format": output_format
        }
    
    def _build_final_result(self, context: Dict[str, Any], executed_steps: List[str], 
                          total_time: float) -> WorkflowOCRResult:
        """构建最终结果"""
        
        # 检查是否成功
        success = all(
            context["results"].get(step, {}).get("success", False) 
            for step in ["input_validation", "ocr_processing"]
        )
        
        # 获取关键结果
        ocr_result = context["results"].get("ocr_processing", {})
        quality_result = context["results"].get("quality_assessment", {})
        format_result = context["results"].get("result_formatting", {})
        
        # 获取最终文本
        if format_result.get("success"):
            final_text = format_result.get("formatted_result", "")
            if isinstance(final_text, dict):
                final_text = final_text.get("text", "")
        else:
            final_text = ocr_result.get("text", "")
        
        return WorkflowOCRResult(
            success=success,
            text=final_text,
            confidence=ocr_result.get("confidence", 0.0),
            processing_time=total_time,
            adapter_used=ocr_result.get("adapter_used", "none"),
            quality_score=quality_result.get("quality_score", 0.0),
            workflow_steps=executed_steps,
            metadata={
                "workflow_id": context["metadata"]["workflow_id"],
                "all_results": context["results"]
            }
        )
    
    # 辅助方法
    def _generate_workflow_id(self) -> str:
        """生成工作流ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _apply_routing_rules(self, task_type: str, quality_level: str, privacy_level: str,
                           file_size_mb: float, image_analysis: Dict) -> str:
        """应用路由规则"""
        
        # 强制本地处理的条件
        if privacy_level == "high":
            return "local_model_mcp"
        
        # 强制云端处理的条件
        if quality_level == "ultra_high":
            return "cloud_search_mcp"
        
        if task_type == "complex_document":
            return "cloud_search_mcp"
        
        # 基于文件大小的决策
        if file_size_mb > 10:
            return "cloud_search_mcp"
        
        # 基于图像质量的决策
        quality_score = image_analysis.get("quality_score", 0.5)
        if quality_score < 0.3:
            return "cloud_search_mcp"  # 低质量图像使用云端处理
        
        # 默认使用本地处理
        return "local_model_mcp"
    
    def _calculate_quality_score(self, confidence: float, text_length: int, 
                               context: Dict[str, Any]) -> float:
        """计算质量分数"""
        # 基础分数来自置信度
        score = confidence
        
        # 文本长度影响
        if text_length > 100:
            score += 0.1
        elif text_length < 10:
            score -= 0.2
        
        # 图像质量影响
        image_analysis = context["results"].get("image_analysis", {})
        image_quality = image_analysis.get("quality_score", 0.5)
        score = (score + image_quality) / 2
        
        return max(0.0, min(1.0, score))
    
    def _get_quality_level(self, quality_score: float) -> str:
        """获取质量级别"""
        if quality_score >= 0.9:
            return "excellent"
        elif quality_score >= 0.8:
            return "high"
        elif quality_score >= 0.6:
            return "medium"
        elif quality_score >= 0.4:
            return "low"
        else:
            return "poor"
    
    # 默认配置方法
    def _get_default_workflow_config(self) -> Dict[str, Any]:
        """获取默认工作流配置"""
        return {
            "workflow": {
                "name": "OCR处理工作流",
                "version": "1.0",
                "description": "智能OCR处理工作流，支持多引擎和云边协同"
            },
            "execution": {
                "timeout": 300,
                "retry_count": 2,
                "parallel_processing": False
            }
        }
    
    def _get_default_routing_rules(self) -> Dict[str, Any]:
        """获取默认路由规则"""
        return {
            "routing_rules": {
                "task_type": {
                    "document_ocr": "local_model_mcp",
                    "handwriting_recognition": "cloud_search_mcp",
                    "table_extraction": "local_model_mcp",
                    "form_processing": "local_model_mcp",
                    "complex_document": "cloud_search_mcp"
                },
                "quality_level": {
                    "low": "local_model_mcp",
                    "medium": "local_model_mcp", 
                    "high": "cloud_search_mcp",
                    "ultra_high": "cloud_search_mcp"
                },
                "privacy_level": {
                    "low": "cloud_search_mcp",
                    "normal": "local_model_mcp",
                    "high": "local_model_mcp"
                }
            }
        }
    
    def _get_default_processing_steps(self) -> Dict[str, Any]:
        """获取默认处理步骤"""
        return {
            "steps": [
                {"name": "input_validation", "required": True},
                {"name": "image_analysis", "required": True},
                {"name": "preprocessing", "required": False},
                {"name": "adapter_selection", "required": True},
                {"name": "ocr_processing", "required": True},
                {"name": "result_validation", "required": True},
                {"name": "postprocessing", "required": False},
                {"name": "quality_assessment", "required": True},
                {"name": "result_formatting", "required": True}
            ]
        }
    
    def _get_default_quality_settings(self) -> Dict[str, Any]:
        """获取默认质量设置"""
        return {
            "quality": {
                "min_confidence": 0.6,
                "target_confidence": 0.8,
                "quality_threshold": 0.7
            },
            "limits": {
                "max_image_size_mb": 50,
                "max_processing_time": 300,
                "max_retry_count": 3
            },
            "preprocessing": {
                "auto_enhance": True,
                "denoise_threshold": 0.3,
                "contrast_enhancement": True,
                "quality_skip_threshold": 0.9
            },
            "postprocessing": {
                "text_cleaning": {
                    "remove_extra_whitespace": True,
                    "normalize_line_breaks": True,
                    "remove_special_chars": False
                }
            }
        }
    
    def _load_default_configurations(self):
        """加载默认配置"""
        self.workflow_config = self._get_default_workflow_config()
        self.routing_rules = self._get_default_routing_rules()
        self.processing_steps = self._get_default_processing_steps()
        self.quality_settings = self._get_default_quality_settings()

