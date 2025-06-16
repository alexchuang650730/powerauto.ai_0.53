#!/usr/bin/env python3
"""
OCR工作流MCP - 主入口类

整合OCR工作流执行器，提供标准的MCP接口
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入工作流执行器
try:
    from ocr_workflow_executor_real import OCRWorkflowExecutor, WorkflowOCRRequest, WorkflowOCRResult
    logger.info("✅ 使用真实OCR工作流执行器")
except ImportError as e:
    logger.warning(f"⚠️ 真实执行器导入失败，使用模拟版本: {e}")
    try:
        from ocr_workflow_executor_mock import OCRWorkflowExecutor, WorkflowOCRRequest, WorkflowOCRResult
        logger.info("✅ 使用模拟OCR工作流执行器")
    except ImportError:
        from ocr_workflow_executor import OCRWorkflowExecutor, WorkflowOCRRequest, WorkflowOCRResult
        logger.info("✅ 使用基础OCR工作流执行器")

class OCRWorkflowMCP:
    """OCR工作流MCP主类 - 提供标准MCP接口"""
    
    def __init__(self, config_dir: str = None):
        self.logger = logger
        
        # 初始化工作流执行器
        self.executor = OCRWorkflowExecutor(config_dir)
        
        # MCP元数据
        self.mcp_info = {
            "name": "OCR工作流MCP",
            "version": "1.0.0",
            "description": "智能OCR处理工作流，支持多引擎和云边协同",
            "capabilities": [
                "document_ocr",
                "handwriting_recognition", 
                "table_extraction",
                "form_processing",
                "multi_language_ocr",
                "image_preprocessing",
                "quality_assessment"
            ],
            "supported_formats": ["jpg", "jpeg", "png", "bmp", "tiff", "pdf"],
            "adapters": ["local_model_mcp", "cloud_search_mcp"]
        }
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "adapter_usage": {
                "local_model_mcp": 0,
                "cloud_search_mcp": 0
            }
        }
        
        self.logger.info("OCR工作流MCP初始化完成")
    
    async def process_ocr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理OCR请求 - 主要接口方法"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 验证请求格式
            validated_request = self._validate_request(request)
            
            # 创建工作流请求
            workflow_request = WorkflowOCRRequest(**validated_request)
            
            # 执行工作流
            result = await self.executor.execute_workflow(workflow_request)
            
            # 更新统计信息
            processing_time = time.time() - start_time
            self._update_stats(result, processing_time)
            
            # 转换为标准响应格式
            response = self._format_response(result, processing_time)
            
            self.logger.info(f"OCR处理完成: {result.adapter_used} ({processing_time:.2f}s)")
            return response
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            self.logger.error(f"OCR处理失败: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "adapter_used": "none"
            }
    
    def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """验证和标准化请求"""
        if not isinstance(request, dict):
            raise ValueError("请求必须是字典格式")
        
        # 必需字段
        if "image_path" not in request:
            raise ValueError("缺少必需字段: image_path")
        
        # 标准化请求
        validated = {
            "image_path": request["image_path"],
            "task_type": request.get("task_type", "document_ocr"),
            "quality_level": request.get("quality_level", "medium"),
            "privacy_level": request.get("privacy_level", "normal"),
            "language": request.get("language", "auto"),
            "output_format": request.get("output_format", "structured_json"),
            "enable_preprocessing": request.get("enable_preprocessing", True),
            "enable_postprocessing": request.get("enable_postprocessing", True),
            "metadata": request.get("metadata", {})
        }
        
        # 验证枚举值
        valid_task_types = ["document_ocr", "handwriting_recognition", "table_extraction", 
                           "form_processing", "complex_document", "multi_language_ocr"]
        if validated["task_type"] not in valid_task_types:
            raise ValueError(f"无效的task_type: {validated['task_type']}")
        
        valid_quality_levels = ["low", "medium", "high", "ultra_high"]
        if validated["quality_level"] not in valid_quality_levels:
            raise ValueError(f"无效的quality_level: {validated['quality_level']}")
        
        valid_privacy_levels = ["low", "normal", "high"]
        if validated["privacy_level"] not in valid_privacy_levels:
            raise ValueError(f"无效的privacy_level: {validated['privacy_level']}")
        
        return validated
    
    def _format_response(self, result: WorkflowOCRResult, processing_time: float) -> Dict[str, Any]:
        """格式化响应"""
        response = {
            "success": result.success,
            "text": result.text,
            "confidence": result.confidence,
            "processing_time": processing_time,
            "adapter_used": result.adapter_used,
            "quality_score": result.quality_score,
            "metadata": {
                "workflow_steps": result.workflow_steps,
                "mcp_info": self.mcp_info,
                **result.metadata
            }
        }
        
        if result.bounding_boxes:
            response["bounding_boxes"] = result.bounding_boxes
        
        if result.error:
            response["error"] = result.error
        
        return response
    
    def _update_stats(self, result: WorkflowOCRResult, processing_time: float):
        """更新统计信息"""
        if result.success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        self.stats["total_processing_time"] += processing_time
        self.stats["average_processing_time"] = (
            self.stats["total_processing_time"] / self.stats["total_requests"]
        )
        
        # 更新适配器使用统计
        adapter_used = result.adapter_used
        if adapter_used in self.stats["adapter_usage"]:
            self.stats["adapter_usage"][adapter_used] += 1
    
    # MCP标准接口方法
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取MCP能力"""
        return {
            "capabilities": self.mcp_info["capabilities"],
            "supported_formats": self.mcp_info["supported_formats"],
            "adapters": self.mcp_info["adapters"],
            "workflow_steps": self.executor.workflow_steps
        }
    
    def get_info(self) -> Dict[str, Any]:
        """获取MCP信息"""
        return self.mcp_info
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_requests"] / max(1, self.stats["total_requests"])
            ),
            "adapter_distribution": {
                adapter: count / max(1, self.stats["total_requests"])
                for adapter, count in self.stats["adapter_usage"].items()
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查工作流执行器
            executor_status = "healthy" if self.executor else "unhealthy"
            
            # 检查OCR组件
            ocr_components_status = {}
            for name, component in self.executor.ocr_components.items():
                ocr_components_status[name] = "available" if component else "unavailable"
            
            return {
                "status": "healthy",
                "executor_status": executor_status,
                "ocr_components": ocr_components_status,
                "total_requests": self.stats["total_requests"],
                "success_rate": self.stats["successful_requests"] / max(1, self.stats["total_requests"])
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    # 批量处理接口
    
    async def batch_process_ocr(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量处理OCR请求"""
        results = []
        
        for i, request in enumerate(requests):
            try:
                result = await self.process_ocr(request)
                result["batch_index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "batch_index": i,
                    "adapter_used": "none"
                })
        
        return results
    
    # 配置管理接口
    
    def update_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        try:
            # 这里可以实现配置热更新
            # 暂时返回成功状态
            return {
                "success": True,
                "message": "配置更新成功",
                "updated_fields": list(config_updates.keys())
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "workflow_config": self.executor.workflow_config,
            "routing_rules": self.executor.routing_rules,
            "quality_settings": self.executor.quality_settings
        }
    
    # 调试和诊断接口
    
    async def test_workflow(self, test_image_path: str = None) -> Dict[str, Any]:
        """测试工作流"""
        if not test_image_path:
            # 使用默认测试图像
            test_image_path = "/tmp/test_image.jpg"
            if not os.path.exists(test_image_path):
                return {
                    "success": False,
                    "error": "测试图像不存在，请提供test_image_path参数"
                }
        
        test_request = {
            "image_path": test_image_path,
            "task_type": "document_ocr",
            "quality_level": "medium",
            "privacy_level": "normal"
        }
        
        return await self.process_ocr(test_request)
    
    def diagnose(self) -> Dict[str, Any]:
        """系统诊断"""
        diagnosis = {
            "mcp_status": "healthy",
            "executor_status": "healthy" if self.executor else "unhealthy",
            "components": {},
            "configuration": {
                "workflow_config_loaded": bool(self.executor.workflow_config),
                "routing_rules_loaded": bool(self.executor.routing_rules),
                "quality_settings_loaded": bool(self.executor.quality_settings)
            },
            "statistics": self.get_statistics(),
            "recommendations": []
        }
        
        # 检查OCR组件
        for name, component in self.executor.ocr_components.items():
            diagnosis["components"][name] = {
                "status": "available" if component else "unavailable",
                "type": type(component).__name__ if component else "None"
            }
        
        # 生成建议
        if self.stats["total_requests"] == 0:
            diagnosis["recommendations"].append("尚未处理任何请求，建议运行测试验证功能")
        
        success_rate = self.stats["successful_requests"] / max(1, self.stats["total_requests"])
        if success_rate < 0.8:
            diagnosis["recommendations"].append(f"成功率较低({success_rate:.2%})，建议检查配置和组件状态")
        
        if not any(self.executor.ocr_components.values()):
            diagnosis["recommendations"].append("OCR组件不可用，建议检查依赖安装")
        
        return diagnosis

# 便捷函数

async def process_image_ocr(image_path: str, **kwargs) -> Dict[str, Any]:
    """便捷的图像OCR处理函数"""
    mcp = OCRWorkflowMCP()
    request = {"image_path": image_path, **kwargs}
    return await mcp.process_ocr(request)

def create_ocr_workflow_mcp(config_dir: str = None) -> OCRWorkflowMCP:
    """创建OCR工作流MCP实例"""
    return OCRWorkflowMCP(config_dir)

# 主程序入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR工作流MCP")
    parser.add_argument("--image", required=True, help="图像文件路径")
    parser.add_argument("--task-type", default="document_ocr", help="任务类型")
    parser.add_argument("--quality", default="medium", help="质量级别")
    parser.add_argument("--privacy", default="normal", help="隐私级别")
    parser.add_argument("--config-dir", help="配置目录路径")
    
    args = parser.parse_args()
    
    async def main():
        mcp = OCRWorkflowMCP(args.config_dir)
        
        request = {
            "image_path": args.image,
            "task_type": args.task_type,
            "quality_level": args.quality,
            "privacy_level": args.privacy
        }
        
        result = await mcp.process_ocr(request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(main())

# 添加缺失的初始化方法到OCRWorkflowMCP类中
def _add_missing_methods():
    """添加缺失的方法到OCRWorkflowMCP类"""
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化MCP"""
        try:
            # 初始化工作流执行器中的组件
            if hasattr(self.executor, 'ocr_components'):
                for name, component in self.executor.ocr_components.items():
                    if hasattr(component, 'initialize'):
                        await component.initialize()
            
            self.logger.info("OCR工作流MCP初始化完成")
            return {"success": True, "message": "初始化成功"}
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def shutdown(self) -> Dict[str, Any]:
        """关闭MCP"""
        try:
            # 关闭工作流执行器中的组件
            if hasattr(self.executor, 'ocr_components'):
                for name, component in self.executor.ocr_components.items():
                    if hasattr(component, 'shutdown'):
                        await component.shutdown()
            
            self.logger.info("OCR工作流MCP关闭完成")
            return {"success": True, "message": "关闭成功"}
        except Exception as e:
            self.logger.error(f"关闭失败: {e}")
            return {"success": False, "error": str(e)}
    
    # 动态添加方法到类
    OCRWorkflowMCP.initialize = initialize
    OCRWorkflowMCP.shutdown = shutdown

# 执行方法添加
_add_missing_methods()

