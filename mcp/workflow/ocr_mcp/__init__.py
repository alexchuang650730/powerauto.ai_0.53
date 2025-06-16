#!/usr/bin/env python3
"""
OCR工作流MCP - 初始化文件
"""

from .src.ocr_workflow_mcp import OCRWorkflowMCP, process_image_ocr, create_ocr_workflow_mcp
from .src.ocr_workflow_executor import OCRWorkflowExecutor, WorkflowOCRRequest, WorkflowOCRResult

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"
__description__ = "智能OCR处理工作流，支持多引擎和云边协同"

__all__ = [
    "OCRWorkflowMCP",
    "OCRWorkflowExecutor", 
    "WorkflowOCRRequest",
    "WorkflowOCRResult",
    "process_image_ocr",
    "create_ocr_workflow_mcp"
]

