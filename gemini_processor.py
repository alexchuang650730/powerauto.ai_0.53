#!/usr/bin/env python3
"""
优化版Gemini处理器模块
提供OCR结果的后处理修正功能，集成Gemini API
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiProcessor:
    """Gemini处理器，提供OCR结果的后处理修正功能"""
    
    def __init__(self, use_mock: bool = True, confidence_threshold: float = 0.75, api_key: str = None):
        """
        初始化Gemini处理器
        
        Args:
            use_mock: 是否使用模拟模式（用于测试，不需要实际调用API）
            confidence_threshold: 置信度阈值，低于此值的识别结果将被修正
            api_key: Gemini API密钥，如果为None则尝试从环境变量获取
        """
        self.use_mock = use_mock
        self.confidence_threshold = confidence_threshold
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.gemini_client = None
        
        # 如果不是模拟模式，则尝试初始化Gemini客户端
        if not self.use_mock:
            if not self.api_key:
                logger.warning("未设置GEMINI_API_KEY环境变量，将使用模拟模式")
                self.use_mock = True
            else:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.gemini_client = genai
                    logger.info("Gemini API客户端初始化成功")
                except ImportError:
                    logger.warning("未找到google-generativeai库，将使用模拟模式")
                    self.use_mock = True
        
        if self.use_mock:
            logger.info("使用模拟模式，不会执行实际的API调用")
    
    def process_ocr_result(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理OCR结果，修正低置信度的文本
        
        Args:
            ocr_result: OCR识别结果
            
        Returns:
            修正后的OCR结果
        """
        start_time = time.time()
        logger.info("开始使用Gemini处理OCR结果")
        
        # 检查OCR结果是否有效
        if "error" in ocr_result:
            logger.error(f"OCR结果包含错误: {ocr_result['error']}")
            return ocr_result
        
        # 获取低置信度的文本块
        low_confidence_blocks = ocr_result.get("low_confidence_blocks", [])
        text_blocks = ocr_result.get("text_blocks", [])
        
        # 如果没有低置信度的文本块，则不需要修正
        if not low_confidence_blocks:
            logger.info("未发现需要修正的低置信度文本块")
            
            # 添加Gemini修正信息
            ocr_result["gemini_corrections"] = {
                "blocks_corrected": 0,
                "processing_time": time.time() - start_time,
                "corrections": []
            }
            
            return ocr_result
        
        # 获取需要修正的文本块
        blocks_to_correct = []
        for block_id in low_confidence_blocks:
            for block in text_blocks:
                if block["id"] == block_id:
                    blocks_to_correct.append(block)
                    break
        
        # 修正文本块
        corrections = []
        for block in blocks_to_correct:
            if self.use_mock:
                corrected_block, correction_info = self._mock_correct_text(block)
            else:
                corrected_block, correction_info = self._correct_text_with_gemini(block, ocr_result)
            
            # 更新文本块
            for i, original_block in enumerate(text_blocks):
                if original_block["id"] == block["id"]:
                    text_blocks[i] = corrected_block
                    break
            
            corrections.append(correction_info)
        
        # 更新结构化文本
        self._update_structure_text(ocr_result)
        
        # 添加Gemini修正信息
        ocr_result["gemini_corrections"] = {
            "blocks_corrected": len(corrections),
            "processing_time": time.time() - start_time,
            "corrections": corrections
        }
        
        logger.info(f"Gemini处理完成，修正了{len(corrections)}个文本块，耗时: {time.time() - start_time:.2f}秒")
        return ocr_result
    
    def _correct_text_with_gemini(self, block: Dict[str, Any], ocr_result: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        使用Gemini API修正文本
        
        Args:
            block: 需要修正的文本块
            ocr_result: 完整的OCR结果，用于提供上下文
            
        Returns:
            修正后的文本块和修正信息
        """
        # 保存原始文本
        original_text = block["text"]
        original_confidence = block["confidence"]
        
        # 构建提示词
        prompt = self._build_correction_prompt(block, ocr_result)
        
        try:
            # 调用Gemini API
            model = self.gemini_client.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # 解析响应
            corrected_text = response.text.strip()
            
            # 如果响应为空或格式不正确，则保持原文
            if not corrected_text:
                logger.warning(f"Gemini返回空响应，保持原文: {original_text}")
                corrected_text = original_text
            
            # 更新文本块
            block["original_text"] = original_text
            block["text"] = corrected_text
            block["confidence"] = min(1.0, original_confidence + 0.2)  # 提高置信度，但不超过1.0
            
            # 创建修正信息
            correction_info = {
                "block_id": block["id"],
                "original_text": original_text,
                "corrected_text": corrected_text,
                "confidence_before": original_confidence,
                "confidence_after": block["confidence"]
            }
            
            return block, correction_info
        
        except Exception as e:
            logger.error(f"Gemini API调用失败: {str(e)}")
            
            # 创建修正信息（未修正）
            correction_info = {
                "block_id": block["id"],
                "original_text": original_text,
                "corrected_text": original_text,
                "confidence_before": original_confidence,
                "confidence_after": original_confidence,
                "error": str(e)
            }
            
            return block, correction_info
    
    def _build_correction_prompt(self, block: Dict[str, Any], ocr_result: Dict[str, Any]) -> str:
        """
        构建用于Gemini API的提示词
        
        Args:
            block: 需要修正的文本块
            ocr_result: 完整的OCR结果，用于提供上下文
            
        Returns:
            提示词
        """
        # 获取上下文
        context = self._get_context(block, ocr_result)
        
        # 构建提示词
        prompt = f"""你是一个专业的OCR后处理专家，擅长修正OCR识别错误。请修正以下文本中可能存在的错误：

【需要修正的文本】
{block["text"]}

【文本置信度】
{block["confidence"]}

【上下文信息】
{context}

【常见OCR错误模式】
1. 形近字错误：如"人口"误识别为"人们"，"未月"误识别为"明月"
2. 部首错误：如"彳亍"误识别为"行走"，"木目"误识别为"相"
3. 标点符号错误：如逗号、句号、引号等
4. 数字混淆：如"0"和"O"，"1"和"I"，"8"和"B"等

请直接返回修正后的文本，不要包含任何解释或额外信息。如果文本没有明显错误，请原样返回。
"""
        
        return prompt
    
    def _get_context(self, block: Dict[str, Any], ocr_result: Dict[str, Any]) -> str:
        """
        获取文本块的上下文
        
        Args:
            block: 需要修正的文本块
            ocr_result: 完整的OCR结果
            
        Returns:
            上下文信息
        """
        text_blocks = ocr_result.get("text_blocks", [])
        
        # 找到当前块的索引
        current_index = -1
        for i, b in enumerate(text_blocks):
            if b["id"] == block["id"]:
                current_index = i
                break
        
        if current_index == -1:
            return "无上下文信息"
        
        # 获取前后各一个块的文本作为上下文
        context_blocks = []
        
        # 前一个块
        if current_index > 0:
            context_blocks.append(f"前文：{text_blocks[current_index - 1]['text']}")
        
        # 后一个块
        if current_index < len(text_blocks) - 1:
            context_blocks.append(f"后文：{text_blocks[current_index + 1]['text']}")
        
        # 如果没有上下文，则返回文档标题或其他信息
        if not context_blocks:
            if "metadata" in ocr_result and "title" in ocr_result["metadata"]:
                context_blocks.append(f"文档标题：{ocr_result['metadata']['title']}")
            else:
                context_blocks.append("无上下文信息")
        
        return "\n".join(context_blocks)
    
    def _mock_correct_text(self, block: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        模拟修正文本
        
        Args:
            block: 需要修正的文本块
            
        Returns:
            修正后的文本块和修正信息
        """
        # 保存原始文本
        original_text = block["text"]
        original_confidence = block["confidence"]
        
        # 模拟修正
        corrected_text = original_text
        
        # 常见OCR错误的模拟修正
        corrections = {
            "彳亍": "行走",
            "未月": "明月",
            "人口": "人们",
            "木目": "相",
            "曰出": "日出",
            "囗家": "国家",
            "丨流": "川流",
            "刂法": "刀法"
        }
        
        for error, correction in corrections.items():
            if error in corrected_text:
                corrected_text = corrected_text.replace(error, correction)
        
        # 如果没有修改，则保持原文
        if corrected_text == original_text:
            # 创建修正信息（未修正）
            correction_info = {
                "block_id": block["id"],
                "original_text": original_text,
                "corrected_text": original_text,
                "confidence_before": original_confidence,
                "confidence_after": original_confidence,
                "note": "未发现需要修正的错误"
            }
            
            return block, correction_info
        
        # 更新文本块
        block["original_text"] = original_text
        block["text"] = corrected_text
        block["confidence"] = min(1.0, original_confidence + 0.2)  # 提高置信度，但不超过1.0
        
        # 创建修正信息
        correction_info = {
            "block_id": block["id"],
            "original_text": original_text,
            "corrected_text": corrected_text,
            "confidence_before": original_confidence,
            "confidence_after": block["confidence"]
        }
        
        return block, correction_info
    
    def _update_structure_text(self, ocr_result: Dict[str, Any]) -> None:
        """
        更新结构化文本
        
        Args:
            ocr_result: OCR结果
        """
        # 获取文本块和结构
        text_blocks = ocr_result.get("text_blocks", [])
        structure = ocr_result.get("structure", {})
        
        # 更新段落文本
        for paragraph in structure.get("text_blocks", []):
            block_ids = paragraph.get("blocks", [])
            texts = []
            
            for block_id in block_ids:
                for block in text_blocks:
                    if block["id"] == block_id:
                        texts.append(block["text"])
                        break
            
            paragraph["text"] = "\n".join(texts)
            
            # 如果有原始文本，也保存
            original_texts = []
            has_original = False
            
            for block_id in block_ids:
                for block in text_blocks:
                    if block["id"] == block_id:
                        if "original_text" in block:
                            original_texts.append(block["original_text"])
                            has_original = True
                        else:
                            original_texts.append(block["text"])
                        break
            
            if has_original:
                paragraph["original_text"] = "\n".join(original_texts)

# 测试代码
if __name__ == "__main__":
    # 创建处理器实例
    processor = GeminiProcessor(use_mock=True)
    
    # 测试OCR结果
    test_ocr_result = {
        "text_blocks": [
            {
                "id": "block_1",
                "text": "这是一个测试文档",
                "confidence": 0.95
            },
            {
                "id": "block_2",
                "text": "它包含一些彳亍和未月等OCR错误",
                "confidence": 0.65,
                "low_confidence": True
            }
        ],
        "low_confidence_blocks": ["block_2"],
        "structure": {
            "text_blocks": [
                {
                    "id": "text_1",
                    "text": "这是一个测试文档",
                    "blocks": ["block_1"]
                },
                {
                    "id": "text_2",
                    "text": "它包含一些彳亍和未月等OCR错误",
                    "blocks": ["block_2"]
                }
            ]
        }
    }
    
    # 处理OCR结果
    result = processor.process_ocr_result(test_ocr_result)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
