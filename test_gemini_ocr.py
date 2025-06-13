#!/usr/bin/env python3
"""
简化的Gemini Vision OCR测试脚本
"""

import json
import logging
from pdf2image import convert_from_path
import google.generativeai as genai
from config import GEMINI_API_KEY

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gemini_vision_ocr(pdf_path):
    """测试Gemini Vision OCR功能"""
    try:
        # 初始化Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # 将PDF转换为图像
        logger.info(f"转换PDF为图像: {pdf_path}")
        images = convert_from_path(pdf_path, poppler_path="/usr/bin")
        logger.info(f"成功转换，共{len(images)}页")
        
        all_text_blocks = []
        
        for idx, image in enumerate(images):
            logger.info(f"处理第{idx+1}页...")
            
            # 构建提示词
            prompt_parts = [
                image,
                "请识别图片中的所有文本，并提供每个文本块的精确位置信息（bounding box）。请以JSON格式返回结果，包含文本内容和bounding box。bounding box格式为 [x_min, y_min, x_max, y_max]。"
            ]
            
            # 调用Gemini Vision API
            response = model.generate_content(prompt_parts)
            response_text = response.text
            
            logger.info(f"Gemini Vision原始响应长度: {len(response_text)}")
            logger.info(f"响应前500字符: {response_text[:500]}")
            
            # 保存原始响应到文件
            with open(f"gemini_response_page_{idx+1}.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            
            # 尝试解析JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                logger.info(f"提取的JSON内容长度: {len(json_content)}")
                logger.info(f"JSON前200字符: {json_content[:200]}")
                
                try:
                    # 解析JSON
                    ocr_array = json.loads(json_content)
                    logger.info(f"成功解析JSON，包含{len(ocr_array)}个文本块")
                    
                    # 转换为我们的格式
                    for block_idx, item in enumerate(ocr_array):
                        text_block = {
                            "id": f"page_{idx+1}_block_{block_idx+1}",
                            "text": item.get("text", ""),
                            "confidence": item.get("confidence", 0.9),
                            "position": item.get("bbox", []),
                            "page": idx + 1
                        }
                        all_text_blocks.append(text_block)
                        logger.info(f"文本块 {block_idx+1}: {text_block['text'][:50]}...")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"尝试解析的内容: {json_content[:200]}...")
            else:
                logger.warning("未找到JSON格式的响应")
        
        # 构建最终结果
        result = {
            "file_path": pdf_path,
            "text_blocks": all_text_blocks,
            "metadata": {
                "total_blocks": len(all_text_blocks),
                "total_pages": len(images)
            }
        }
        
        # 保存结果
        with open("gemini_ocr_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"OCR完成，共识别{len(all_text_blocks)}个文本块")
        return result
        
    except Exception as e:
        logger.error(f"OCR处理失败: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python test_gemini_ocr.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = test_gemini_vision_ocr(pdf_path)
    
    if result:
        print(f"成功处理PDF文件: {pdf_path}")
        print(f"识别文本块数量: {result['metadata']['total_blocks']}")
        print(f"处理页数: {result['metadata']['total_pages']}")
        print("详细结果已保存到 gemini_ocr_result.json")
    else:
        print("处理失败")

