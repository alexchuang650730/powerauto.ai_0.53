#!/usr/bin/env python3
"""
创建OCR测试图像
将文本内容转换为图像，用于OCR准确率测试
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_text_image(text, output_path, width=800, height=600, font_size=24):
    """
    创建包含文本的图像
    
    Args:
        text: 要显示的文本
        output_path: 输出图像路径
        width: 图像宽度
        height: 图像高度
        font_size: 字体大小
    """
    # 创建白色背景图像
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        # 尝试加载字体
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 文本换行
    margin = 20
    max_width = width - 2 * margin
    lines = []
    
    for paragraph in text.split('\n'):
        if paragraph.strip():
            wrapped_lines = textwrap.wrap(paragraph, width=max_width // (font_size // 2))
            lines.extend(wrapped_lines)
        else:
            lines.append('')
    
    # 绘制文本
    y_position = margin
    for line in lines:
        draw.text((margin, y_position), line, font=font, fill=(0, 0, 0))
        y_position += font_size + 5
    
    # 保存图像
    image.save(output_path)
    print(f"图像已保存: {output_path}")

def main():
    # 确保输出目录存在
    os.makedirs("test_data/documents", exist_ok=True)
    
    # 读取示例文本
    with open("test_data/documents/sample1.txt", "r", encoding="utf-8") as f:
        sample_text = f.read()
    
    # 创建包含OCR错误的图像
    error_text = sample_text.replace("行走", "彳亍").replace("明月", "未月").replace("人们", "人口").replace("相", "木目")
    create_text_image(error_text, "test_data/documents/sample1.png")
    
    # 创建第二个测试图像
    error_text2 = """这是第二个测试文档，用于评估OCR和Gemini修正的准确率。
    
本文档包含一些常见的OCR错误和格式问题：

1. 曰出东方（应为"日出东方"）
2. 囗家安全（应为"国家安全"）
3. 丨流不息（应为"川流不息"）
4. 刂法严明（应为"刀法严明"）

表格示例：
项目    数量    单价
商品A   2       50.00
商品B   1       100.00
    """
    create_text_image(error_text2, "test_data/documents/sample2.png")
    
    # 创建对应的标准答案
    with open("test_data/ground_truth/sample2.txt", "w", encoding="utf-8") as f:
        f.write(error_text2.replace("曰出东方", "日出东方").replace("囗家安全", "国家安全")
                .replace("丨流不息", "川流不息").replace("刂法严明", "刀法严明"))
    
    print("测试图像和标准答案创建完成")

if __name__ == "__main__":
    main()
