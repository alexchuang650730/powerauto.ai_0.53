#!/usr/bin/env python3
"""
正确的Claude API集成示例
基于Anthropic官方Python SDK
"""

import os
import json
import logging
from anthropic import Anthropic

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeAPIClient:
    """Claude API客户端"""
    
    def __init__(self, api_key=None):
        """初始化Claude API客户端"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供ANTHROPIC_API_KEY")
        
        self.client = Anthropic(api_key=self.api_key)
        logger.info("Claude API客户端初始化成功")
    
    def analyze_ocr_results(self, ocr_result, gemini_result=None):
        """
        使用Claude分析OCR结果并提供改进建议
        """
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(ocr_result, gemini_result)
            
            # 调用Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2048,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # 解析响应
            analysis_text = response.content[0].text
            logger.info(f"Claude分析完成，响应长度: {len(analysis_text)}")
            
            # 尝试从响应中提取JSON
            analysis_result = self._parse_analysis_response(analysis_text)
            
            return {
                "success": True,
                "analysis": analysis_result,
                "raw_response": analysis_text,
                "model": "claude-3-sonnet-20240229",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Claude分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def _build_analysis_prompt(self, ocr_result, gemini_result=None):
        """构建Claude分析提示词"""
        prompt = f"""请分析以下OCR识别结果，并提供详细的质量评估和改进建议。

OCR识别结果：
```json
{json.dumps(ocr_result, ensure_ascii=False, indent=2)}
```
"""

        if gemini_result:
            prompt += f"""
Gemini修正结果：
```json
{json.dumps(gemini_result, ensure_ascii=False, indent=2)}
```
"""

        prompt += """
请从以下几个方面进行分析：

1. **文本识别准确性**：评估识别出的文本内容是否准确
2. **布局理解**：评估文本块的位置信息是否合理
3. **置信度评估**：分析置信度分布是否合理
4. **潜在问题**：识别可能存在的OCR错误
5. **改进建议**：提供具体的改进建议

请以JSON格式返回分析结果，包含以下字段：
- accuracy_score: 准确性评分（0-10）
- layout_score: 布局理解评分（0-10）
- confidence_score: 置信度评分（0-10）
- overall_score: 总体评分（0-10）
- issues: 发现的问题列表
- suggestions: 改进建议列表
- summary: 总结性评价

请确保返回有效的JSON格式。"""

        return prompt
    
    def _parse_analysis_response(self, response_text):
        """解析Claude的分析响应"""
        try:
            # 尝试从响应中提取JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # 如果没有```json```，尝试直接解析
                return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回结构化的文本分析
            return {
                "accuracy_score": 7,
                "layout_score": 7,
                "confidence_score": 7,
                "overall_score": 7,
                "issues": ["无法解析JSON格式的分析结果"],
                "suggestions": ["改进响应格式解析"],
                "summary": response_text[:500] + "..." if len(response_text) > 500 else response_text
            }

if __name__ == "__main__":
    print("Claude API客户端模块")
