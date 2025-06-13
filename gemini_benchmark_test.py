#!/usr/bin/env python3
"""
使用Gemini Vision OCR的Benchmark测试
"""

import os
import json
import time
import logging
from pathlib import Path
import google.generativeai as genai
from config import GEMINI_API_KEY

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiBenchmarkTester:
    """Gemini Vision OCR Benchmark测试器"""
    
    def __init__(self):
        """初始化测试器"""
        # 初始化Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        logger.info("Gemini Vision OCR Benchmark测试器初始化完成")
    
    def run_benchmark(self, test_dir, ground_truth_dir, output_dir):
        """运行benchmark测试"""
        test_dir = Path(test_dir)
        ground_truth_dir = Path(ground_truth_dir)
        output_dir = Path(output_dir)
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # 获取所有测试图片
        image_files = list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.jpeg"))
        
        logger.info(f"找到{len(image_files)}个测试图片")
        
        for image_file in image_files:
            logger.info(f"处理图片: {image_file.name}")
            
            # 获取对应的标准答案文件
            ground_truth_file = ground_truth_dir / f"{image_file.stem}.txt"
            
            if not ground_truth_file.exists():
                logger.warning(f"未找到标准答案文件: {ground_truth_file}")
                continue
            
            # 读取标准答案
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                ground_truth = f.read().strip()
            
            # 运行OCR测试
            result = self.test_single_image(image_file, ground_truth)
            result['image_file'] = image_file.name
            result['ground_truth_file'] = ground_truth_file.name
            
            results.append(result)
            
            # 保存单个结果
            result_file = output_dir / f"{image_file.stem}_benchmark.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"完成处理: {image_file.name}")
        
        # 生成总结报告
        summary = self.generate_summary(results)
        
        # 保存总结报告
        summary_file = output_dir / "benchmark_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 生成CSV报告
        self.generate_csv_report(results, output_dir / "benchmark_results.csv")
        
        logger.info(f"Benchmark测试完成，结果保存在: {output_dir}")
        return summary
    
    def test_single_image(self, image_file, ground_truth):
        """测试单个图片"""
        start_time = time.time()
        
        try:
            # 使用Gemini Vision进行OCR
            from PIL import Image
            image = Image.open(image_file)
            
            # 构建提示词
            prompt = "请识别图片中的所有文本内容，按照原文的顺序和格式输出，不要添加任何额外的格式或说明。"
            
            # 调用Gemini Vision
            response = self.model.generate_content([image, prompt])
            ocr_text = response.text.strip()
            
            processing_time = time.time() - start_time
            
            # 计算准确率指标
            metrics = self.calculate_metrics(ocr_text, ground_truth)
            
            return {
                "success": True,
                "ocr_text": ocr_text,
                "ground_truth": ground_truth,
                "processing_time": processing_time,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"处理图片失败 {image_file}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ocr_text": "",
                "ground_truth": ground_truth,
                "processing_time": time.time() - start_time,
                "metrics": {
                    "character_accuracy": 0.0,
                    "word_accuracy": 0.0,
                    "line_accuracy": 0.0
                }
            }
    
    def calculate_metrics(self, ocr_text, ground_truth):
        """计算准确率指标"""
        # 字符级准确率
        char_accuracy = self.calculate_character_accuracy(ocr_text, ground_truth)
        
        # 词级准确率
        word_accuracy = self.calculate_word_accuracy(ocr_text, ground_truth)
        
        # 行级准确率
        line_accuracy = self.calculate_line_accuracy(ocr_text, ground_truth)
        
        return {
            "character_accuracy": char_accuracy,
            "word_accuracy": word_accuracy,
            "line_accuracy": line_accuracy
        }
    
    def calculate_character_accuracy(self, ocr_text, ground_truth):
        """计算字符级准确率"""
        if not ground_truth:
            return 1.0 if not ocr_text else 0.0
        
        # 简单的字符匹配
        correct_chars = 0
        total_chars = len(ground_truth)
        
        for i, char in enumerate(ground_truth):
            if i < len(ocr_text) and ocr_text[i] == char:
                correct_chars += 1
        
        return correct_chars / total_chars if total_chars > 0 else 0.0
    
    def calculate_word_accuracy(self, ocr_text, ground_truth):
        """计算词级准确率"""
        ocr_words = ocr_text.split()
        truth_words = ground_truth.split()
        
        if not truth_words:
            return 1.0 if not ocr_words else 0.0
        
        correct_words = 0
        for i, word in enumerate(truth_words):
            if i < len(ocr_words) and ocr_words[i] == word:
                correct_words += 1
        
        return correct_words / len(truth_words)
    
    def calculate_line_accuracy(self, ocr_text, ground_truth):
        """计算行级准确率"""
        ocr_lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        truth_lines = [line.strip() for line in ground_truth.split('\n') if line.strip()]
        
        if not truth_lines:
            return 1.0 if not ocr_lines else 0.0
        
        correct_lines = 0
        for i, line in enumerate(truth_lines):
            if i < len(ocr_lines) and ocr_lines[i] == line:
                correct_lines += 1
        
        return correct_lines / len(truth_lines)
    
    def generate_summary(self, results):
        """生成总结报告"""
        total_tests = len(results)
        successful_tests = len([r for r in results if r['success']])
        
        if successful_tests == 0:
            return {
                "total_tests": total_tests,
                "successful_tests": 0,
                "success_rate": 0.0,
                "average_metrics": {
                    "character_accuracy": 0.0,
                    "word_accuracy": 0.0,
                    "line_accuracy": 0.0
                },
                "average_processing_time": 0.0
            }
        
        # 计算平均指标
        avg_char_acc = sum(r['metrics']['character_accuracy'] for r in results if r['success']) / successful_tests
        avg_word_acc = sum(r['metrics']['word_accuracy'] for r in results if r['success']) / successful_tests
        avg_line_acc = sum(r['metrics']['line_accuracy'] for r in results if r['success']) / successful_tests
        avg_time = sum(r['processing_time'] for r in results if r['success']) / successful_tests
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests,
            "average_metrics": {
                "character_accuracy": avg_char_acc,
                "word_accuracy": avg_word_acc,
                "line_accuracy": avg_line_acc
            },
            "average_processing_time": avg_time,
            "individual_results": results
        }
    
    def generate_csv_report(self, results, csv_file):
        """生成CSV报告"""
        import csv
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                'Image File', 'Success', 'Character Accuracy', 
                'Word Accuracy', 'Line Accuracy', 'Processing Time'
            ])
            
            # 写入数据行
            for result in results:
                writer.writerow([
                    result['image_file'],
                    result['success'],
                    result['metrics']['character_accuracy'],
                    result['metrics']['word_accuracy'],
                    result['metrics']['line_accuracy'],
                    result['processing_time']
                ])

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gemini Vision OCR Benchmark测试')
    parser.add_argument('test_dir', help='测试图片目录')
    parser.add_argument('ground_truth_dir', help='标准答案目录')
    parser.add_argument('--output-dir', default='benchmark_results', help='输出目录')
    
    args = parser.parse_args()
    
    # 运行benchmark测试
    tester = GeminiBenchmarkTester()
    summary = tester.run_benchmark(args.test_dir, args.ground_truth_dir, args.output_dir)
    
    # 打印总结
    print("\n=== Benchmark测试结果 ===")
    print(f"总测试数: {summary['total_tests']}")
    print(f"成功测试数: {summary['successful_tests']}")
    print(f"成功率: {summary['success_rate']:.2%}")
    print(f"平均字符准确率: {summary['average_metrics']['character_accuracy']:.2%}")
    print(f"平均词准确率: {summary['average_metrics']['word_accuracy']:.2%}")
    print(f"平均行准确率: {summary['average_metrics']['line_accuracy']:.2%}")
    print(f"平均处理时间: {summary['average_processing_time']:.2f}秒")

if __name__ == "__main__":
    main()
