#!/usr/bin/env python3
"""
优化版PaddleOCR处理器模块
提供文档OCR识别功能，集成PaddleOCR引擎
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

class PaddleOCRProcessor:
    """PaddleOCR处理器，提供文档OCR识别功能"""
    
    def __init__(self, use_mock: bool = True, confidence_threshold: float = 0.75):
        """
        初始化PaddleOCR处理器
        
        Args:
            use_mock: 是否使用模拟模式（用于测试，不需要实际安装PaddleOCR）
            confidence_threshold: 置信度阈值，低于此值的识别结果将被标记为低置信度
        """
        self.use_mock = use_mock
        self.confidence_threshold = confidence_threshold
        self.paddle_ocr = None
        
        # 如果不是模拟模式，则尝试导入PaddleOCR
        if not self.use_mock:
            try:
                from paddleocr import PaddleOCR
                # 使用GPU加速（如果可用）
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True)
                logger.info("PaddleOCR引擎加载成功")
            except ImportError:
                logger.warning("未找到PaddleOCR库，将使用模拟模式")
                self.use_mock = True
        
        if self.use_mock:
            logger.info("使用模拟模式，不会执行实际的OCR识别")
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        处理文档，执行OCR识别
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            OCR识别结果
        """
        start_time = time.time()
        logger.info(f"开始处理文档: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return {"error": "文件不存在", "file_path": file_path}
        
        # 检查文件格式
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.jpg', '.jpeg', '.png', '.pdf', '.tif', '.tiff', '.bmp']
        
        if file_ext not in supported_formats:
            logger.error(f"不支持的文件格式: {file_ext}")
            return {"error": "不支持的文件格式", "file_path": file_path, "format": file_ext}
        
        # 处理文档
        if self.use_mock:
            result = self._generate_mock_result(file_path)
        else:
            result = self._process_with_paddleocr(file_path)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        logger.info(f"文档处理完成，耗时: {processing_time:.2f}秒")
        return result
    
    def _process_with_paddleocr(self, file_path: str) -> Dict[str, Any]:
        """
        使用PaddleOCR处理文档
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            OCR识别结果
        """
        try:
            # 执行OCR识别
            ocr_result = self.paddle_ocr.ocr(file_path, cls=True)
            
            # 处理结果
            return self._process_paddleocr_result(ocr_result, file_path)
        except Exception as e:
            logger.error(f"PaddleOCR处理失败: {str(e)}")
            return {"error": f"PaddleOCR处理失败: {str(e)}", "file_path": file_path}
    
    def _process_paddleocr_result(self, ocr_result: List, file_path: str) -> Dict[str, Any]:
        """
        处理PaddleOCR的识别结果
        
        Args:
            ocr_result: PaddleOCR的识别结果
            file_path: 文档文件路径
            
        Returns:
            处理后的OCR结果
        """
        # 提取文本块
        text_blocks = []
        low_confidence_blocks = []
        
        for page_idx, page_result in enumerate(ocr_result):
            for block_idx, block in enumerate(page_result):
                # 提取位置和文本信息
                position = block[0]  # 四个坐标点
                text_info = block[1]  # (文本, 置信度)
                
                text = text_info[0]
                confidence = float(text_info[1])
                
                # 创建文本块
                block_id = f"page_{page_idx}_block_{block_idx}"
                text_block = {
                    "id": block_id,
                    "text": text,
                    "confidence": confidence,
                    "position": position,
                    "page": page_idx
                }
                
                # 检查置信度
                if confidence < self.confidence_threshold:
                    text_block["low_confidence"] = True
                    low_confidence_blocks.append(block_id)
                
                text_blocks.append(text_block)
        
        # 分析文档结构（段落、表格等）
        structure = self._analyze_document_structure(text_blocks)
        
        # 构建结果
        result = {
            "file_path": file_path,
            "text_blocks": text_blocks,
            "structure": structure,
            "low_confidence_blocks": low_confidence_blocks,
            "metadata": {
                "total_blocks": len(text_blocks),
                "low_confidence_blocks": len(low_confidence_blocks),
                "average_confidence": sum(block["confidence"] for block in text_blocks) / len(text_blocks) if text_blocks else 0
            }
        }
        
        return result
    
    def _analyze_document_structure(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析文档结构
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            文档结构信息
        """
        # 这里可以实现更复杂的文档结构分析
        # 例如识别标题、段落、列表、表格等
        
        # 简单的结构分析示例
        paragraphs = []
        current_paragraph = []
        
        for block in text_blocks:
            # 简单的段落划分逻辑
            if not current_paragraph or self._is_same_paragraph(current_paragraph[-1], block):
                current_paragraph.append(block)
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                current_paragraph = [block]
        
        if current_paragraph:
            paragraphs.append(current_paragraph)
        
        # 识别表格（简化版）
        tables = self._detect_tables(text_blocks)
        
        # 识别图片（简化版）
        figures = self._detect_figures(text_blocks)
        
        return {
            "paragraphs": paragraphs,
            "tables": tables,
            "figures": figures
        }
    
    def _is_same_paragraph(self, block1: Dict[str, Any], block2: Dict[str, Any]) -> bool:
        """
        判断两个文本块是否属于同一段落
        
        Args:
            block1: 第一个文本块
            block2: 第二个文本块
            
        Returns:
            是否属于同一段落
        """
        # 简单的判断逻辑：如果两个块在同一页，且垂直位置接近，则认为是同一段落
        if block1["page"] != block2["page"]:
            return False
        
        # 获取块的垂直位置（取中点）
        y1 = sum(p[1] for p in block1["position"]) / 4
        y2 = sum(p[1] for p in block2["position"]) / 4
        
        # 计算块的高度
        height1 = max(p[1] for p in block1["position"]) - min(p[1] for p in block1["position"])
        
        # 如果垂直距离小于块高的1.5倍，则认为是同一段落
        return abs(y2 - y1) < height1 * 1.5
    
    def _detect_tables(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测文档中的表格
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            表格列表
        """
        # 简化版表格检测
        # 实际应用中，可能需要更复杂的表格检测算法
        tables = []
        
        # 检测表格的简单逻辑：查找包含多个数字和分隔符的文本块
        for block in text_blocks:
            text = block["text"]
            
            # 如果文本包含多个数字和分隔符，可能是表格
            if (text.count("|") > 2 or text.count("\t") > 2) and sum(c.isdigit() for c in text) > 5:
                tables.append({
                    "id": f"table_{len(tables)}",
                    "blocks": [block["id"]],
                    "position": block["position"],
                    "page": block["page"],
                    "content": text
                })
        
        return tables
    
    def _detect_figures(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测文档中的图片
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            图片列表
        """
        # 简化版图片检测
        # 实际应用中，需要使用图像处理算法检测图片
        figures = []
        
        # 检测图片的简单逻辑：查找包含"图"、"Figure"等关键词的文本块
        for block in text_blocks:
            text = block["text"]
            
            # 如果文本包含"图"、"Figure"等关键词，可能是图片标题
            if re.search(r'图\s*\d+|Figure\s+\d+', text, re.IGNORECASE):
                figures.append({
                    "id": f"figure_{len(figures)}",
                    "blocks": [block["id"]],
                    "position": block["position"],
                    "page": block["page"],
                    "caption": text
                })
        
        return figures
    
    def _generate_mock_result(self, file_path: str) -> Dict[str, Any]:
        """
        生成模拟的OCR结果
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            模拟的OCR结果
        """
        logger.info(f"生成模拟OCR结果: {file_path}")
        
        # 根据文件名生成不同的模拟结果
        file_name = os.path.basename(file_path)
        
        # 默认模拟结果
        text_blocks = []
        structure = {
            "text_blocks": [],
            "tables": [],
            "figures": []
        }
        
        # 根据文件名生成特定的模拟结果
        if "sample1" in file_name:
            # 第一个示例：包含OCR错误
            text_blocks = [
                {
                    "id": "block_1",
                    "text": "这是一个测试文档，用于评估OCR和Gemini修正的准确率。",
                    "confidence": 0.95,
                    "position": [[10, 10], [500, 10], [500, 50], [10, 50]]
                },
                {
                    "id": "block_2",
                    "text": "文档包含一些常见的OCR错误，如：",
                    "confidence": 0.92,
                    "position": [[10, 60], [500, 60], [500, 100], [10, 100]]
                },
                {
                    "id": "block_3",
                    "text": "1. 彳亍（应为\"行走\"）",
                    "confidence": 0.65,
                    "low_confidence": True,
                    "position": [[10, 110], [500, 110], [500, 150], [10, 150]]
                },
                {
                    "id": "block_4",
                    "text": "2. 未月（应为\"明月\"）",
                    "confidence": 0.68,
                    "low_confidence": True,
                    "position": [[10, 160], [500, 160], [500, 200], [10, 200]]
                },
                {
                    "id": "block_5",
                    "text": "3. 人口（应为\"人们\"）",
                    "confidence": 0.72,
                    "low_confidence": True,
                    "position": [[10, 210], [500, 210], [500, 250], [10, 250]]
                },
                {
                    "id": "block_6",
                    "text": "4. 木目（应为\"相\"）",
                    "confidence": 0.70,
                    "low_confidence": True,
                    "position": [[10, 260], [500, 260], [500, 300], [10, 300]]
                },
                {
                    "id": "block_7",
                    "text": "这些错误将用于测试Gemini的修正能力。",
                    "confidence": 0.90,
                    "position": [[10, 310], [500, 310], [500, 350], [10, 350]]
                }
            ]
            
            structure["text_blocks"] = [
                {
                    "id": "text_1",
                    "text": "这是一个测试文档，用于评估OCR和Gemini修正的准确率。\n文档包含一些常见的OCR错误，如：",
                    "blocks": ["block_1", "block_2"]
                },
                {
                    "id": "text_2",
                    "text": "1. 彳亍（应为\"行走\"）\n2. 未月（应为\"明月\"）\n3. 人口（应为\"人们\"）\n4. 木目（应为\"相\"）",
                    "blocks": ["block_3", "block_4", "block_5", "block_6"]
                },
                {
                    "id": "text_3",
                    "text": "这些错误将用于测试Gemini的修正能力。",
                    "blocks": ["block_7"]
                }
            ]
        elif "sample2" in file_name:
            # 第二个示例：包含表格和更多OCR错误
            text_blocks = [
                {
                    "id": "block_1",
                    "text": "这是第二个测试文档，用于评估OCR和Gemini修正的准确率。",
                    "confidence": 0.94,
                    "position": [[10, 10], [500, 10], [500, 50], [10, 50]]
                },
                {
                    "id": "block_2",
                    "text": "本文档包含一些常见的OCR错误和格式问题：",
                    "confidence": 0.93,
                    "position": [[10, 60], [500, 60], [500, 100], [10, 100]]
                },
                {
                    "id": "block_3",
                    "text": "1. 曰出东方（应为\"日出东方\"）",
                    "confidence": 0.67,
                    "low_confidence": True,
                    "position": [[10, 110], [500, 110], [500, 150], [10, 150]]
                },
                {
                    "id": "block_4",
                    "text": "2. 囗家安全（应为\"国家安全\"）",
                    "confidence": 0.65,
                    "low_confidence": True,
                    "position": [[10, 160], [500, 160], [500, 200], [10, 200]]
                },
                {
                    "id": "block_5",
                    "text": "3. 丨流不息（应为\"川流不息\"）",
                    "confidence": 0.69,
                    "low_confidence": True,
                    "position": [[10, 210], [500, 210], [500, 250], [10, 250]]
                },
                {
                    "id": "block_6",
                    "text": "4. 刂法严明（应为\"刀法严明\"）",
                    "confidence": 0.71,
                    "low_confidence": True,
                    "position": [[10, 260], [500, 260], [500, 300], [10, 300]]
                },
                {
                    "id": "block_7",
                    "text": "表格示例：",
                    "confidence": 0.92,
                    "position": [[10, 310], [500, 310], [500, 350], [10, 350]]
                },
                {
                    "id": "block_8",
                    "text": "项目    数量    单价\n商品A   2       50.00\n商品B   1       100.00",
                    "confidence": 0.85,
                    "position": [[10, 360], [500, 360], [500, 450], [10, 450]]
                }
            ]
            
            structure["text_blocks"] = [
                {
                    "id": "text_1",
                    "text": "这是第二个测试文档，用于评估OCR和Gemini修正的准确率。\n本文档包含一些常见的OCR错误和格式问题：",
                    "blocks": ["block_1", "block_2"]
                },
                {
                    "id": "text_2",
                    "text": "1. 曰出东方（应为\"日出东方\"）\n2. 囗家安全（应为\"国家安全\"）\n3. 丨流不息（应为\"川流不息\"）\n4. 刂法严明（应为\"刀法严明\"）",
                    "blocks": ["block_3", "block_4", "block_5", "block_6"]
                },
                {
                    "id": "text_3",
                    "text": "表格示例：",
                    "blocks": ["block_7"]
                }
            ]
            
            structure["tables"] = [
                {
                    "id": "table_1",
                    "text": "项目    数量    单价\n商品A   2       50.00\n商品B   1       100.00",
                    "blocks": ["block_8"],
                    "position": [[10, 360], [500, 360], [500, 450], [10, 450]],
                    "content": "<table><tr><td>项目</td><td>数量</td><td>单价</td></tr><tr><td>商品A</td><td>2</td><td>50.00</td></tr><tr><td>商品B</td><td>1</td><td>100.00</td></tr></table>"
                }
            ]
        else:
            # 通用模拟结果
            text_blocks = [
                {
                    "id": "block_1",
                    "text": "这是一个通用的OCR测试文档。",
                    "confidence": 0.90,
                    "position": [[10, 10], [500, 10], [500, 50], [10, 50]]
                },
                {
                    "id": "block_2",
                    "text": "它包含一些文本内容，用于测试OCR识别效果。",
                    "confidence": 0.85,
                    "position": [[10, 60], [500, 60], [500, 100], [10, 100]]
                }
            ]
            
            structure["text_blocks"] = [
                {
                    "id": "text_1",
                    "text": "这是一个通用的OCR测试文档。\n它包含一些文本内容，用于测试OCR识别效果。",
                    "blocks": ["block_1", "block_2"]
                }
            ]
        
        # 构建低置信度块列表
        low_confidence_blocks = [block["id"] for block in text_blocks if block.get("low_confidence", False)]
        
        # 构建结果
        result = {
            "file_path": file_path,
            "text_blocks": text_blocks,
            "structure": structure,
            "low_confidence_blocks": low_confidence_blocks,
            "metadata": {
                "total_blocks": len(text_blocks),
                "low_confidence_blocks": len(low_confidence_blocks),
                "average_confidence": sum(block["confidence"] for block in text_blocks) / len(text_blocks) if text_blocks else 0
            }
        }
        
        return result

# 测试代码
if __name__ == "__main__":
    # 创建处理器实例
    processor = PaddleOCRProcessor(use_mock=True)
    
    # 测试文件路径
    test_file = "test.jpg"
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    
    # 处理文档
    result = processor.process_document(test_file)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
