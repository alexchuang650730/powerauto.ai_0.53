#!/usr/bin/env python3
"""
OCR和Word转换功能主模块
集成PaddleOCR处理器、Gemini处理器和Word生成器
"""

import os
import sys
import logging
import argparse
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
from datetime import datetime

# 导入处理器模块
from paddleocr_processor import PaddleOCRProcessor
from gemini_processor import GeminiProcessor
from word_generator import WordGenerator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRWordConverter:
    """OCR和Word转换功能集成类"""
    
    def __init__(self, use_mock: bool = True):
        """
        初始化OCR和Word转换器
        
        Args:
            use_mock: 是否使用模拟模式（用于测试，不需要实际安装依赖库）
        """
        self.use_mock = use_mock
        
        # 初始化处理器
        self.ocr_processor = PaddleOCRProcessor(use_mock=use_mock)
        self.gemini_processor = GeminiProcessor(use_mock=use_mock)
        self.word_generator = WordGenerator(use_mock=use_mock)
        
        logger.info("OCR和Word转换器初始化完成")
    
    def process_document(self, file_path: str, output_dir: str = None, apply_gemini: bool = True) -> Dict[str, Any]:
        """
        处理文档，执行OCR识别、Gemini修正和Word生成
        
        Args:
            file_path: 文档文件路径
            output_dir: 输出目录，默认为当前目录
            apply_gemini: 是否应用Gemini修正
            
        Returns:
            处理结果信息
        """
        start_time = time.time()
        logger.info(f"开始处理文档: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return {"error": "文件不存在", "file_path": file_path}
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        file_name = os.path.basename(file_path)
        file_base = os.path.splitext(file_name)[0]
        
        # 1. OCR处理
        logger.info("执行OCR处理...")
        ocr_result = self.ocr_processor.process_document(file_path)
        
        if "error" in ocr_result:
            logger.error(f"OCR处理失败: {ocr_result['error']}")
            return ocr_result
        
        # 保存OCR结果
        ocr_json_path = os.path.join(output_dir, f"{file_base}_ocr.json")
        with open(ocr_json_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_result, f, ensure_ascii=False, indent=2)
        
        # 2. Gemini修正（如果启用）
        if apply_gemini:
            logger.info("执行Gemini修正...")
            ocr_result = self.gemini_processor.process_ocr_result(ocr_result)
            
            # 保存修正后的结果
            gemini_json_path = os.path.join(output_dir, f"{file_base}_gemini.json")
            with open(gemini_json_path, 'w', encoding='utf-8') as f:
                json.dump(ocr_result, f, ensure_ascii=False, indent=2)
        
        # 3. 生成Word文档
        logger.info("生成Word文档...")
        word_path = os.path.join(output_dir, f"{file_base}_output.docx")
        generated_path = self.word_generator.generate_document(ocr_result, word_path)
        
        # 计算总处理时间
        total_time = time.time() - start_time
        
        # 返回处理结果
        result = {
            "status": "success",
            "file_path": file_path,
            "ocr_json_path": ocr_json_path,
            "word_path": generated_path,
            "processing_time": total_time
        }
        
        if apply_gemini:
            result["gemini_json_path"] = gemini_json_path
        
        logger.info(f"文档处理完成，总耗时: {total_time:.2f}秒")
        return result

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="OCR和Word转换工具")
    parser.add_argument("file_path", help="要处理的文档文件路径")
    parser.add_argument("--output-dir", "-o", help="输出目录")
    parser.add_argument("--no-gemini", action="store_true", help="禁用Gemini修正")
    parser.add_argument("--mock", action="store_true", help="使用模拟模式（不需要实际安装依赖库）")
    
    args = parser.parse_args()
    
    # 创建转换器实例
    converter = OCRWordConverter(use_mock=args.mock)
    
    # 处理文档
    result = converter.process_document(
        args.file_path,
        output_dir=args.output_dir,
        apply_gemini=not args.no_gemini
    )
    
    # 输出结果
    if "error" in result:
        print(f"处理失败: {result['error']}")
        return 1
    
    print(f"处理成功!")
    print(f"OCR结果: {result['ocr_json_path']}")
    if "gemini_json_path" in result:
        print(f"Gemini修正结果: {result['gemini_json_path']}")
    print(f"Word文档: {result['word_path']}")
    print(f"总耗时: {result['processing_time']:.2f}秒")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
