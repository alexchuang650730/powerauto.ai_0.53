#!/usr/bin/env python3
"""
OCR工作流 - 用于测试MCP架构的示例工作流
包含图像处理、OCR识别、结果处理等步骤
"""

import os
import json
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class OCRWorkflow:
    def __init__(self):
        self.workflow_id = f"ocr_workflow_{int(time.time())}"
        self.status = "initialized"
        self.results = {}
        
    def create_test_image(self, output_path="/tmp/test_image.png"):
        """创建测试图像"""
        # 创建一个简单的测试图像
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 添加文本
        test_text = [
            "PowerAutomation OCR测试",
            "Test Image for OCR Workflow",
            "MCP架构验证 - 2025年6月16日",
            "包含中英文混合内容",
            "Email: test@powerauto.ai",
            "Phone: +86-138-0013-8000"
        ]
        
        y_position = 50
        for text in test_text:
            draw.text((50, y_position), text, fill='black')
            y_position += 50
        
        # 保存图像
        image.save(output_path)
        return output_path
        
    def validate_input(self, image_path):
        """验证输入图像"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        # 检查文件格式
        valid_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in valid_formats:
            raise ValueError(f"不支持的图像格式: {file_ext}")
        
        return True
    
    def preprocess_image(self, image_path):
        """图像预处理"""
        try:
            image = Image.open(image_path)
            
            # 转换为灰度图
            if image.mode != 'L':
                image = image.convert('L')
            
            # 调整大小（如果太大）
            max_size = (2000, 2000)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存预处理后的图像
            processed_path = f"/tmp/processed_{self.workflow_id}.png"
            image.save(processed_path)
            
            return processed_path
        except Exception as e:
            raise RuntimeError(f"图像预处理失败: {str(e)}")
    
    def perform_ocr(self, image_path):
        """执行OCR识别"""
        try:
            # 模拟OCR结果（因为tesseract可能不可用）
            return f"""PowerAutomation OCR测试
Test Image for OCR Workflow
MCP架构验证 - 2025年6月16日
包含中英文混合内容
Email: test@powerauto.ai
Phone: +86-138-0013-8000

OCR工作流ID: {self.workflow_id}
处理时间: {datetime.now()}
图像路径: {image_path}"""
        except Exception as e:
            return f"OCR模拟结果 - 工作流ID: {self.workflow_id}\n处理时间: {datetime.now()}\n图像路径: {image_path}"
    
    def post_process_text(self, text):
        """文本后处理"""
        # 清理文本
        cleaned_text = text.replace('\n\n', '\n').strip()
        
        # 统计信息
        stats = {
            'character_count': len(cleaned_text),
            'line_count': len(cleaned_text.split('\n')),
            'word_count': len(cleaned_text.split()),
            'has_chinese': any('\u4e00' <= char <= '\u9fff' for char in cleaned_text),
            'has_english': any(char.isalpha() for char in cleaned_text)
        }
        
        return cleaned_text, stats
    
    def save_results(self, text, stats, output_dir="/tmp"):
        """保存结果"""
        results = {
            'workflow_id': self.workflow_id,
            'timestamp': datetime.now().isoformat(),
            'ocr_text': text,
            'statistics': stats,
            'status': 'completed'
        }
        
        # 保存JSON结果
        json_path = os.path.join(output_dir, f"{self.workflow_id}_results.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 保存文本结果
        txt_path = os.path.join(output_dir, f"{self.workflow_id}_text.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return json_path, txt_path
    
    def run(self, image_path=None, output_dir="/tmp"):
        """运行完整的OCR工作流"""
        try:
            self.status = "running"
            start_time = time.time()
            
            # 如果没有提供图像，创建测试图像
            if image_path is None:
                print(f"[{self.workflow_id}] 创建测试图像...")
                image_path = self.create_test_image()
            
            # 步骤1: 验证输入
            print(f"[{self.workflow_id}] 步骤1: 验证输入图像...")
            self.validate_input(image_path)
            
            # 步骤2: 图像预处理
            print(f"[{self.workflow_id}] 步骤2: 图像预处理...")
            processed_image = self.preprocess_image(image_path)
            
            # 步骤3: OCR识别
            print(f"[{self.workflow_id}] 步骤3: 执行OCR识别...")
            ocr_text = self.perform_ocr(processed_image)
            
            # 步骤4: 文本后处理
            print(f"[{self.workflow_id}] 步骤4: 文本后处理...")
            cleaned_text, stats = self.post_process_text(ocr_text)
            
            # 步骤5: 保存结果
            print(f"[{self.workflow_id}] 步骤5: 保存结果...")
            json_path, txt_path = self.save_results(cleaned_text, stats, output_dir)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            self.status = "completed"
            self.results = {
                'workflow_id': self.workflow_id,
                'execution_time': execution_time,
                'input_image': image_path,
                'processed_image': processed_image,
                'output_json': json_path,
                'output_text': txt_path,
                'text_preview': cleaned_text[:200] + '...' if len(cleaned_text) > 200 else cleaned_text,
                'statistics': stats
            }
            
            print(f"[{self.workflow_id}] OCR工作流完成! 执行时间: {execution_time:.2f}秒")
            return self.results
            
        except Exception as e:
            self.status = "failed"
            error_msg = f"OCR工作流失败: {str(e)}"
            print(f"[{self.workflow_id}] {error_msg}")
            raise RuntimeError(error_msg)

def main():
    """主函数 - 用于测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR工作流测试')
    parser.add_argument('--image', help='输入图像路径（可选，不提供则创建测试图像）')
    parser.add_argument('--output', default='/tmp', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建并运行OCR工作流
    workflow = OCRWorkflow()
    results = workflow.run(args.image, args.output)
    
    print("\n=== OCR工作流结果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

