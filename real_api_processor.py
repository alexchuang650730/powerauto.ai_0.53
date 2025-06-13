#!/usr/bin/env python3
"""
使用真实API处理PDF文档，包括Gemini Vision OCR、Gemini和Claude
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
import google.generativeai as genai
from anthropic import Anthropic
from PIL import Image
from pdf2image import convert_from_path
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class RealAPIProcessor:
    def __init__(self):
        """初始化处理器，加载所有真实API"""
        logger.info("初始化真实API处理器")
        
        # 初始化Gemini
        logger.info("初始化Gemini API")
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(
            model_name=config.GEMINI_CONFIG["model"],
            generation_config={
                "temperature": config.GEMINI_CONFIG["temperature"],
                "max_output_tokens": config.GEMINI_CONFIG["max_output_tokens"],
            }
        )
        
        # 初始化Claude
        logger.info("初始化Claude API")
        self.claude_client = Anthropic(api_key=config.CLAUDE_API_KEY)
        
        # 创建输出目录
        os.makedirs("user_documents/output", exist_ok=True)
        
    def process_document(self, file_path):
        """处理文档并返回结果"""
        start_time = time.time()
        logger.info(f"开始处理文档: {file_path}")
        
        # 1. 使用Gemini Vision进行OCR识别
        logger.info("执行Gemini Vision OCR识别...")
        ocr_result = self._perform_ocr(file_path)
        
        # 2. 使用Gemini进行后处理修正
        logger.info("执行Gemini修正...")
        gemini_result = self._perform_gemini_correction(ocr_result)
        
        # 3. 使用Claude进行比对分析
        logger.info("执行Claude比对分析...")
        claude_result = self._perform_claude_comparison(ocr_result, gemini_result)
        
        # 4. 保存所有结果
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = "user_documents/output"
        
        ocr_output_path = os.path.join(output_dir, f"{base_name}_ocr.json")
        gemini_output_path = os.path.join(output_dir, f"{base_name}_gemini.json")
        claude_output_path = os.path.join(output_dir, f"{base_name}_claude.json")
        comparison_path = os.path.join(output_dir, f"{base_name}_comparison.json")
        
        with open(ocr_output_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_result, f, ensure_ascii=False, indent=2)
            
        with open(gemini_output_path, 'w', encoding='utf-8') as f:
            json.dump(gemini_result, f, ensure_ascii=False, indent=2)
            
        with open(claude_output_path, 'w', encoding='utf-8') as f:
            json.dump(claude_result, f, ensure_ascii=False, indent=2)
        
        # 创建比较结果
        comparison = {
            "file_path": file_path,
            "ocr_result": ocr_result,
            "gemini_result": gemini_result,
            "claude_result": claude_result,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        
        logger.info(f"文档处理完成，总耗时: {time.time() - start_time:.2f}秒")
        return {
            "ocr_output_path": ocr_output_path,
            "gemini_output_path": gemini_output_path,
            "claude_output_path": claude_output_path,
            "comparison_path": comparison_path,
            "processing_time": time.time() - start_time
        }
    
    def _perform_ocr(self, file_path):
        """使用Gemini Vision执行OCR识别"""
        start_time = time.time()
        text_blocks = []
        try:
            # 将PDF转换为图像
            images = convert_from_path(file_path, poppler_path="/usr/bin")
            
            for idx, image in enumerate(images):
                # 将PIL Image转换为字节流，以便发送给Gemini Vision
                # image_bytes = io.BytesIO()
                # image.save(image_bytes, format='PNG')
                # image_data = image_bytes.getvalue()
                
                # Gemini Vision直接支持PIL Image对象
                
                # 构建Gemini Vision提示词
                prompt_parts = [
                    image,
                    "请识别图片中的所有文本，并提供每个文本块的精确位置信息（bounding box）。请以JSON格式返回结果，包含文本内容、置信度（如果可用）和bounding box。bounding box格式为 [x_min, y_min, x_max, y_max]。"
                ]
                
                # 调用Gemini Vision API
                response = self.gemini_model.generate_content(prompt_parts)
                
                # 解析响应
                response_text = response.text
                logger.info(f"Gemini Vision响应: {response_text[:200]}...")
                
                # 尝试从响应中提取JSON
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    try:
                        json_content = json_match.group(1)
                        # Gemini返回的是数组格式，需要包装成我们期望的格式
                        ocr_array = json.loads(json_content)
                        ocr_data = {"text_blocks": ocr_array}
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {e}")
                        # 如果JSON解析失败，创建一个简单的文本块
                        ocr_data = {
                            "text_blocks": [{
                                "text": response_text,
                                "confidence": 0.8,
                                "bounding_box": [0, 0, 100, 100]
                            }]
                        }
                else:
                    # 如果没有```json```，尝试直接解析
                    try:
                        # 尝试直接解析为数组
                        ocr_array = json.loads(response_text)
                        ocr_data = {"text_blocks": ocr_array}
                    except json.JSONDecodeError as e:
                        logger.error(f"直接JSON解析失败: {e}")
                        # 如果JSON解析失败，创建一个简单的文本块
                        ocr_data = {
                            "text_blocks": [{
                                "text": response_text,
                                "confidence": 0.8,
                                "bounding_box": [0, 0, 100, 100]
                            }]
                        }

                for block_idx, item in enumerate(ocr_data.get("text_blocks", [])):
                    text_blocks.append({
                        "id": f"block_{idx}_{block_idx}",
                        "text": item.get("text", ""),
                        "confidence": item.get("confidence", 0.9), # Gemini Vision通常置信度较高
                        "position": item.get("bbox", []), # Gemini返回的是bbox字段
                        "page": idx
                    })
            
            # 识别低置信度文本块 (这里暂时假设Gemini Vision的置信度都较高，或者根据实际情况调整)
            low_confidence_blocks = [
                block["id"] for block in text_blocks 
                if block.get("confidence", 1.0) < 0.8 # 默认置信度为1.0，如果Gemini Vision不提供则不会被标记为低置信度
            ]
            
            # 计算平均置信度
            avg_confidence = sum(block.get("confidence", 1.0) for block in text_blocks) / len(text_blocks) if text_blocks else 0
            
            # 构建结构化结果
            ocr_result = {
                "file_path": file_path,
                "text_blocks": text_blocks,
                "low_confidence_blocks": low_confidence_blocks,
                "metadata": {
                    "total_blocks": len(text_blocks),
                    "low_confidence_blocks": len(low_confidence_blocks),
                    "average_confidence": avg_confidence
                },
                "processing_time": time.time() - start_time
            }
            
            logger.info(f"Gemini Vision OCR识别完成，识别了{len(text_blocks)}个文本块，其中{len(low_confidence_blocks)}个低置信度，耗时: {time.time() - start_time:.2f}秒")
            return ocr_result
            
        except Exception as e:
            logger.error(f"Gemini Vision OCR识别失败: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e),
                "text_blocks": [],
                "low_confidence_blocks": [],
                "metadata": {
                    "total_blocks": 0,
                    "low_confidence_blocks": 0,
                    "average_confidence": 0
                },
                "processing_time": time.time() - start_time
            }
    
    def _perform_gemini_correction(self, ocr_result):
        """使用Gemini API进行OCR结果修正"""
        start_time = time.time()
        
        # 如果没有低置信度文本块，则不需要修正
        if not ocr_result["low_confidence_blocks"]:
            logger.info("未发现需要修正的低置信度文本块")
            return {
                "file_path": ocr_result["file_path"],
                "corrections": [],
                "metadata": {
                    "total_corrections": 0,
                    "average_confidence_improvement": 0
                },
                "processing_time": time.time() - start_time
            }
        
        # 提取需要修正的文本块
        low_confidence_blocks = [
            block for block in ocr_result["text_blocks"]
            if block["id"] in ocr_result["low_confidence_blocks"]
        ]
        
        # 构建Gemini提示词
        prompt = f"""
        你是一个专业的OCR后处理专家，请帮我修正以下OCR识别结果中的错误。
        这些文本块的置信度较低，可能存在识别错误。请根据上下文和常见OCR错误模式进行修正。
        
        原始文本块:
        """
        
        for block in low_confidence_blocks:
            prompt += f"\nID: {block['id']}\n文本: {block['text']}\n置信度: {block['confidence']}\n"
        
        prompt += """
        请按以下格式返回修正结果:
        {
          "corrections": [
            {
              "id": "block_id",
              "original": "原始文本",
              "corrected": "修正后文本",
              "confidence": 0.95
            },
            ...
          ]
        }
        
        只返回JSON格式的结果，不要有任何其他解释。
        """
        
        try:
            # 调用Gemini API
            response = self.gemini_model.generate_content(prompt)
            
            # 解析响应
            correction_text = response.text
            
            # 提取JSON部分
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', correction_text, re.DOTALL)
            if json_match:
                correction_text = json_match.group(1)
            else:
                # 尝试直接解析
                json_match = re.search(r'\{.*\}', correction_text, re.DOTALL)
                if json_match:
                    correction_text = json_match.group(0)
            
            # 解析JSON
            corrections = json.loads(correction_text)
            
            # 计算平均置信度提升
            total_improvement = 0
            for correction in corrections.get("corrections", []):
                block_id = correction["id"]
                original_block = next((b for b in ocr_result["text_blocks"] if b["id"] == block_id), None)
                if original_block:
                    improvement = correction["confidence"] - original_block["confidence"]
                    total_improvement += improvement
            
            avg_improvement = total_improvement / len(corrections.get("corrections", [])) if corrections.get("corrections", []) else 0
            
            # 构建结果
            gemini_result = {
                "file_path": ocr_result["file_path"],
                "corrections": corrections.get("corrections", []),
                "metadata": {
                    "total_corrections": len(corrections.get("corrections", [])),
                    "average_confidence_improvement": avg_improvement
                },
                "processing_time": time.time() - start_time
            }
            
            logger.info(f"Gemini修正完成，修正了{len(corrections.get('corrections', []))}个文本块，平均提升{avg_improvement:.4f}，耗时: {time.time() - start_time:.2f}秒")
            return gemini_result
            
        except Exception as e:
            logger.error(f"Gemini修正失败: {str(e)}")
            return {
                "file_path": ocr_result["file_path"],
                "error": str(e),
                "corrections": [],
                "metadata": {
                    "total_corrections": 0,
                    "average_confidence_improvement": 0
                },
                "processing_time": time.time() - start_time
            }
    
    def _perform_claude_comparison(self, ocr_result, gemini_result):
        """使用Claude API进行比对分析"""
        start_time = time.time()
        
        # 构建Claude提示词
        prompt = f"""
        你是一个专业的OCR结果分析专家，请对比分析以下OCR原始结果和Gemini修正后的结果，评估修正质量。
        
        ## OCR原始结果
        总文本块数: {ocr_result["metadata"]["total_blocks"]}
        低置信度文本块数: {ocr_result["metadata"]["low_confidence_blocks"]}
        平均置信度: {ocr_result["metadata"]["average_confidence"]:.4f}
        
        ## 低置信度文本块:
        """
        
        low_confidence_blocks = [
            block for block in ocr_result["text_blocks"]
            if block["id"] in ocr_result["low_confidence_blocks"]
        ]
        
        for block in low_confidence_blocks:
            prompt += f"\nID: {block['id']}\n文本: {block['text']}\n置信度: {block['confidence']}\n"
        
        prompt += "\n## Gemini修正结果\n"
        
        for correction in gemini_result.get("corrections", []):
            prompt += f"\nID: {correction['id']}\n原文: {correction['original']}\n修正: {correction['corrected']}\n置信度: {correction['confidence']}\n"
        
        prompt += """
        请进行以下分析:
        1. 评估Gemini修正的准确性和合理性
        2. 指出任何可能的错误修正或遗漏
        3. 提供整体质量评分(1-10分)
        4. 给出改进建议
        
        请以JSON格式返回分析结果:
        {
          "analysis": {
            "accuracy_evaluation": "对修正准确性的评估",
            "error_identification": ["错误1", "错误2", ...],
            "quality_score": 8.5,
            "improvement_suggestions": ["建议1", "建议2", ...]
          }
        }
        
        只返回JSON格式的结果，不要有任何其他解释。
        """
        
        try:
            # 调用Claude API
            response = self.claude_client.messages.create(
                model=config.CLAUDE_CONFIG["model"],
                max_tokens=config.CLAUDE_CONFIG["max_tokens"],
                temperature=config.CLAUDE_CONFIG["temperature"],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 解析响应
            analysis_text = response.content[0].text
            
            # 提取JSON部分
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', analysis_text, re.DOTALL)
            if json_match:
                analysis_text = json_match.group(1)
            else:
                # 尝试直接解析
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis_text = json_match.group(0)
            
            # 解析JSON
            analysis = json.loads(analysis_text)
            
            # 构建结果
            claude_result = {
                "file_path": ocr_result["file_path"],
                "analysis": analysis.get("analysis", {}),
                "processing_time": time.time() - start_time
            }
            
            logger.info(f"Claude比对分析完成，质量评分: {analysis.get('analysis', {}).get('quality_score', 'N/A')}，耗时: {time.time() - start_time:.2f}秒")
            return claude_result
            
        except Exception as e:
            logger.error(f"Claude比对分析失败: {str(e)}")
            return {
                "file_path": ocr_result["file_path"],
                "error": str(e),
                "analysis": {},
                "processing_time": time.time() - start_time
            }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python real_api_processor.py <pdf_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    processor = RealAPIProcessor()
    result = processor.process_document(file_path)
    
    print(f"处理完成!")
    print(f"OCR结果: {result['ocr_output_path']}")
    print(f"Gemini修正结果: {result['gemini_output_path']}")
    print(f"Claude比对分析: {result['claude_output_path']}")
    print(f"比较结果: {result['comparison_path']}")
    print(f"总耗时: {result['processing_time']:.2f}秒")

if __name__ == "__main__":
    main()


