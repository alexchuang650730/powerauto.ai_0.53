#!/usr/bin/env python3
"""
Benchmark测试模块
用于评估OCR和Word转换功能的准确率
"""

import os
import sys
import logging
import argparse
import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime
import difflib
import re

# 导入处理器模块
from paddleocr_processor import PaddleOCRProcessor
from gemini_processor import GeminiProcessor
from word_generator import WordGenerator
from main import OCRWordConverter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkTester:
    """OCR和Word转换功能的Benchmark测试器"""
    
    def __init__(self, use_mock: bool = True):
        """
        初始化Benchmark测试器
        
        Args:
            use_mock: 是否使用模拟模式（用于测试，不需要实际安装依赖库）
        """
        self.use_mock = use_mock
        
        # 初始化转换器
        self.converter = OCRWordConverter(use_mock=use_mock)
        
        logger.info("Benchmark测试器初始化完成")
    
    def run_benchmark(self, test_dir: str, ground_truth_dir: str, output_dir: str = None) -> Dict[str, Any]:
        """
        运行Benchmark测试
        
        Args:
            test_dir: 测试文档目录
            ground_truth_dir: 标准答案目录
            output_dir: 输出目录，默认为当前目录
            
        Returns:
            测试结果
        """
        start_time = time.time()
        logger.info(f"开始Benchmark测试: {test_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(test_dir):
            logger.error(f"测试目录不存在: {test_dir}")
            return {"error": "测试目录不存在", "test_dir": test_dir}
        
        if not os.path.exists(ground_truth_dir):
            logger.error(f"标准答案目录不存在: {ground_truth_dir}")
            return {"error": "标准答案目录不存在", "ground_truth_dir": ground_truth_dir}
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(test_dir), "benchmark_results")
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取测试文件列表
        test_files = self._get_test_files(test_dir)
        if not test_files:
            logger.error(f"未找到测试文件: {test_dir}")
            return {"error": "未找到测试文件", "test_dir": test_dir}
        
        # 运行测试
        results = []
        summary = {
            "total_files": len(test_files),
            "processed_files": 0,
            "success_files": 0,
            "failed_files": 0,
            "total_cer": 0.0,
            "total_wer": 0.0,
            "total_structure_score": 0.0,
            "avg_cer": 0.0,
            "avg_wer": 0.0,
            "avg_structure_score": 0.0,
            "gemini_improvement": {
                "cer": 0.0,
                "wer": 0.0
            }
        }
        
        for test_file in test_files:
            file_name = os.path.basename(test_file)
            file_base = os.path.splitext(file_name)[0]
            
            # 查找对应的标准答案文件
            ground_truth_file = os.path.join(ground_truth_dir, f"{file_base}.txt")
            if not os.path.exists(ground_truth_file):
                logger.warning(f"未找到标准答案文件: {ground_truth_file}")
                continue
            
            # 处理测试文件
            logger.info(f"处理测试文件: {file_name}")
            file_output_dir = os.path.join(output_dir, file_base)
            os.makedirs(file_output_dir, exist_ok=True)
            
            # 1. 使用OCR处理器处理文件
            ocr_result = self.converter.ocr_processor.process_document(test_file)
            
            if "error" in ocr_result:
                logger.error(f"OCR处理失败: {ocr_result['error']}")
                summary["failed_files"] += 1
                continue
            
            # 2. 提取OCR文本
            ocr_text = self._extract_text_from_ocr_result(ocr_result)
            
            # 3. 使用Gemini处理器修正OCR结果
            gemini_result = self.converter.gemini_processor.process_ocr_result(ocr_result)
            
            # 4. 提取Gemini修正后的文本
            gemini_text = self._extract_text_from_ocr_result(gemini_result)
            
            # 5. 读取标准答案
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                ground_truth_text = f.read()
            
            # 6. 计算评估指标
            # 6.1 OCR结果的指标
            ocr_cer = self._calculate_cer(ocr_text, ground_truth_text)
            ocr_wer = self._calculate_wer(ocr_text, ground_truth_text)
            ocr_structure_score = self._calculate_structure_score(ocr_result, ground_truth_text)
            
            # 6.2 Gemini修正后的指标
            gemini_cer = self._calculate_cer(gemini_text, ground_truth_text)
            gemini_wer = self._calculate_wer(gemini_text, ground_truth_text)
            gemini_structure_score = self._calculate_structure_score(gemini_result, ground_truth_text)
            
            # 7. 计算Gemini改进程度
            cer_improvement = ocr_cer - gemini_cer
            wer_improvement = ocr_wer - gemini_wer
            
            # 8. 保存结果
            file_result = {
                "file_name": file_name,
                "ocr": {
                    "cer": ocr_cer,
                    "wer": ocr_wer,
                    "structure_score": ocr_structure_score
                },
                "gemini": {
                    "cer": gemini_cer,
                    "wer": gemini_wer,
                    "structure_score": gemini_structure_score
                },
                "improvement": {
                    "cer": cer_improvement,
                    "wer": wer_improvement
                }
            }
            
            results.append(file_result)
            
            # 9. 更新汇总信息
            summary["processed_files"] += 1
            summary["success_files"] += 1
            summary["total_cer"] += gemini_cer
            summary["total_wer"] += gemini_wer
            summary["total_structure_score"] += gemini_structure_score
            summary["gemini_improvement"]["cer"] += cer_improvement
            summary["gemini_improvement"]["wer"] += wer_improvement
            
            # 10. 保存详细结果到文件
            detail_result = {
                "file_name": file_name,
                "ocr_text": ocr_text,
                "gemini_text": gemini_text,
                "ground_truth_text": ground_truth_text,
                "metrics": file_result
            }
            
            detail_file = os.path.join(file_output_dir, f"{file_base}_benchmark.json")
            with open(detail_file, 'w', encoding='utf-8') as f:
                json.dump(detail_result, f, ensure_ascii=False, indent=2)
        
        # 计算平均值
        if summary["success_files"] > 0:
            summary["avg_cer"] = summary["total_cer"] / summary["success_files"]
            summary["avg_wer"] = summary["total_wer"] / summary["success_files"]
            summary["avg_structure_score"] = summary["total_structure_score"] / summary["success_files"]
            summary["gemini_improvement"]["cer"] /= summary["success_files"]
            summary["gemini_improvement"]["wer"] /= summary["success_files"]
        
        # 保存汇总结果
        benchmark_result = {
            "timestamp": datetime.now().isoformat(),
            "test_dir": test_dir,
            "ground_truth_dir": ground_truth_dir,
            "output_dir": output_dir,
            "summary": summary,
            "results": results,
            "processing_time": time.time() - start_time
        }
        
        summary_file = os.path.join(output_dir, "benchmark_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_result, f, ensure_ascii=False, indent=2)
        
        # 生成CSV报告
        csv_file = os.path.join(output_dir, "benchmark_results.csv")
        self._generate_csv_report(results, csv_file)
        
        logger.info(f"Benchmark测试完成，结果保存在: {output_dir}")
        return benchmark_result
    
    def _get_test_files(self, test_dir: str) -> List[str]:
        """获取测试文件列表"""
        supported_formats = ['.jpg', '.jpeg', '.png', '.pdf', '.tif', '.tiff', '.bmp']
        test_files = []
        
        for root, _, files in os.walk(test_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_formats:
                    test_files.append(os.path.join(root, file))
        
        return test_files
    
    def _extract_text_from_ocr_result(self, ocr_result: Dict[str, Any]) -> str:
        """从OCR结果中提取文本"""
        text_blocks = []
        
        for block in ocr_result.get("structure", {}).get("text_blocks", []):
            text_blocks.append(block.get("text", ""))
        
        return "\n".join(text_blocks)
    
    def _calculate_cer(self, hypothesis: str, reference: str) -> float:
        """
        计算字符错误率(Character Error Rate)
        
        CER = (S + D + I) / N
        其中：
        S: 替换的字符数
        D: 删除的字符数
        I: 插入的字符数
        N: 参考文本的字符数
        """
        if not reference:
            return 1.0 if hypothesis else 0.0
        
        # 使用编辑距离计算
        m, n = len(hypothesis), len(reference)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if hypothesis[i-1] == reference[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
        
        return dp[m][n] / n
    
    def _calculate_wer(self, hypothesis: str, reference: str) -> float:
        """
        计算词错误率(Word Error Rate)
        
        WER = (S + D + I) / N
        其中：
        S: 替换的词数
        D: 删除的词数
        I: 插入的词数
        N: 参考文本的词数
        """
        # 分词
        hypothesis_words = re.findall(r'\w+|[^\w\s]', hypothesis)
        reference_words = re.findall(r'\w+|[^\w\s]', reference)
        
        if not reference_words:
            return 1.0 if hypothesis_words else 0.0
        
        # 使用编辑距离计算
        m, n = len(hypothesis_words), len(reference_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if hypothesis_words[i-1] == reference_words[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
        
        return dp[m][n] / n
    
    def _calculate_structure_score(self, ocr_result: Dict[str, Any], reference_text: str) -> float:
        """
        计算结构保持度
        
        这是一个简化的实现，实际应用中可能需要更复杂的算法
        """
        # 提取OCR结果中的结构信息
        text_blocks_count = len(ocr_result.get("structure", {}).get("text_blocks", []))
        tables_count = len(ocr_result.get("structure", {}).get("tables", []))
        figures_count = len(ocr_result.get("structure", {}).get("figures", []))
        
        # 从参考文本中估计结构
        # 这是一个非常简化的方法，实际应用中需要更准确的方法
        reference_paragraphs = reference_text.split("\n\n")
        reference_tables = len(re.findall(r'表\d+|Table\s+\d+', reference_text, re.IGNORECASE))
        reference_figures = len(re.findall(r'图\d+|Figure\s+\d+', reference_text, re.IGNORECASE))
        
        # 计算结构相似度
        # 这是一个简化的计算方法
        structure_score = 0.0
        
        # 段落数量相似度
        if reference_paragraphs:
            paragraphs_similarity = min(text_blocks_count, len(reference_paragraphs)) / max(text_blocks_count, len(reference_paragraphs))
            structure_score += paragraphs_similarity * 0.6  # 段落结构权重60%
        
        # 表格数量相似度
        if reference_tables or tables_count:
            tables_similarity = min(tables_count, reference_tables) / max(tables_count, reference_tables) if max(tables_count, reference_tables) > 0 else 1.0
            structure_score += tables_similarity * 0.2  # 表格结构权重20%
        
        # 图片数量相似度
        if reference_figures or figures_count:
            figures_similarity = min(figures_count, reference_figures) / max(figures_count, reference_figures) if max(figures_count, reference_figures) > 0 else 1.0
            structure_score += figures_similarity * 0.2  # 图片结构权重20%
        
        return structure_score
    
    def _generate_csv_report(self, results: List[Dict[str, Any]], csv_file: str) -> None:
        """生成CSV格式的报告"""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                "文件名", 
                "OCR-CER", "OCR-WER", "OCR-结构分数",
                "Gemini-CER", "Gemini-WER", "Gemini-结构分数",
                "CER改进", "WER改进"
            ])
            
            # 写入数据
            for result in results:
                writer.writerow([
                    result["file_name"],
                    f"{result['ocr']['cer']:.4f}", 
                    f"{result['ocr']['wer']:.4f}", 
                    f"{result['ocr']['structure_score']:.4f}",
                    f"{result['gemini']['cer']:.4f}", 
                    f"{result['gemini']['wer']:.4f}", 
                    f"{result['gemini']['structure_score']:.4f}",
                    f"{result['improvement']['cer']:.4f}", 
                    f"{result['improvement']['wer']:.4f}"
                ])

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="OCR和Word转换功能的Benchmark测试")
    parser.add_argument("test_dir", help="测试文档目录")
    parser.add_argument("ground_truth_dir", help="标准答案目录")
    parser.add_argument("--output-dir", "-o", help="输出目录")
    parser.add_argument("--mock", action="store_true", help="使用模拟模式（不需要实际安装依赖库）")
    
    args = parser.parse_args()
    
    # 创建测试器实例
    tester = BenchmarkTester(use_mock=args.mock)
    
    # 运行测试
    result = tester.run_benchmark(
        args.test_dir,
        args.ground_truth_dir,
        output_dir=args.output_dir
    )
    
    # 输出结果
    if "error" in result:
        print(f"测试失败: {result['error']}")
        return 1
    
    summary = result["summary"]
    print(f"Benchmark测试完成!")
    print(f"总文件数: {summary['total_files']}")
    print(f"成功处理: {summary['success_files']}")
    print(f"处理失败: {summary['failed_files']}")
    print(f"平均字符错误率(CER): {summary['avg_cer']:.4f}")
    print(f"平均词错误率(WER): {summary['avg_wer']:.4f}")
    print(f"平均结构保持度: {summary['avg_structure_score']:.4f}")
    print(f"Gemini平均CER改进: {summary['gemini_improvement']['cer']:.4f}")
    print(f"Gemini平均WER改进: {summary['gemini_improvement']['wer']:.4f}")
    print(f"详细结果保存在: {result['output_dir']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
