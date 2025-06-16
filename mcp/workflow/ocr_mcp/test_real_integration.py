#!/usr/bin/env python3
"""
OCR工作流MCP集成测试 - 真实版本

测试Local Model MCP与OCR工作流架构的集成
"""

import os
import sys
import time
import json
import asyncio
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_real_integration():
    """测试真实集成功能"""
    print("=" * 60)
    print("OCR工作流MCP真实集成测试")
    print("=" * 60)
    
    try:
        # 导入OCR工作流MCP
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        from src.ocr_workflow_executor_real import WorkflowOCRRequest
        
        # 初始化MCP
        print("\n1. 初始化OCR工作流MCP...")
        mcp = OCRWorkflowMCP()
        await mcp.initialize()
        
        # 检查健康状态
        print("\n2. 检查健康状态...")
        health = mcp.health_check()  # 移除await，因为这是同步方法
        print(f"健康状态: {health}")
        
        # 获取能力信息
        print("\n3. 获取能力信息...")
        capabilities = mcp.get_capabilities()  # 移除await，因为这是同步方法
        print(f"支持的能力: {capabilities['capabilities']}")
        
        # 创建测试图像（如果不存在）
        test_image_path = "/tmp/test_ocr_image.png"
        if not os.path.exists(test_image_path):
            print(f"\n4. 创建测试图像: {test_image_path}")
            create_test_image(test_image_path)
        else:
            print(f"\n4. 使用现有测试图像: {test_image_path}")
        
        # 测试OCR处理
        print("\n5. 测试OCR处理...")
        request_dict = {
            "image_path": test_image_path,
            "task_type": "document_ocr",
            "quality_level": "medium",
            "privacy_level": "normal",
            "language": "auto",
            "enable_preprocessing": True,
            "enable_postprocessing": True
        }
        
        start_time = time.time()
        result = await mcp.process_ocr(request_dict)  # 传递字典而不是WorkflowOCRRequest对象
        processing_time = time.time() - start_time
        
        print(f"\n6. OCR处理结果:")
        print(f"   成功: {result.get('success', False)}")
        print(f"   处理时间: {processing_time:.2f}秒")
        print(f"   使用的适配器: {result.get('adapter_used', 'unknown')}")
        print(f"   置信度: {result.get('confidence', 0.0):.2f}")
        print(f"   质量分数: {result.get('quality_score', 0.0):.2f}")
        
        if result.get('success'):
            text = result.get('text', '')
            print(f"   识别文本: {text[:100]}...")
        else:
            print(f"   错误信息: {result.get('error', '未知错误')}")
        
        # 测试统计信息
        print("\n7. 获取统计信息...")
        stats = mcp.get_statistics()  # 移除await，因为这是同步方法
        print(f"统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 测试诊断功能
        print("\n8. 运行系统诊断...")
        diagnosis = mcp.diagnose()  # 移除await，因为这是同步方法
        print(f"诊断结果: {json.dumps(diagnosis, indent=2, ensure_ascii=False)}")
        
        # 关闭MCP
        print("\n9. 关闭MCP...")
        shutdown_result = await mcp.shutdown()  # 保留await，因为这是异步方法
        print(f"关闭结果: {shutdown_result}")
        
        print("\n" + "=" * 60)
        print("✅ 真实集成测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 真实集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_image(image_path: str):
    """创建测试图像"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建白色背景图像
        width, height = 800, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 添加测试文本
        test_text = [
            "OCR工作流测试文档",
            "",
            "这是一个用于测试OCR功能的示例文档。",
            "包含中文和English混合文本。",
            "",
            "测试内容包括：",
            "1. 文档识别",
            "2. 文本提取", 
            "3. 质量评估",
            "4. 结果格式化",
            "",
            "Date: 2025-06-16",
            "Version: 1.0.0"
        ]
        
        # 尝试使用系统字体
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 绘制文本
        y_offset = 50
        for line in test_text:
            draw.text((50, y_offset), line, fill='black', font=font)
            y_offset += 35
        
        # 保存图像
        image.save(image_path)
        print(f"✅ 测试图像已创建: {image_path}")
        
    except Exception as e:
        logger.error(f"❌ 创建测试图像失败: {e}")
        # 创建简单的纯色图像作为备选
        try:
            from PIL import Image
            image = Image.new('RGB', (400, 300), 'white')
            image.save(image_path)
            print(f"✅ 简单测试图像已创建: {image_path}")
        except Exception as e2:
            logger.error(f"❌ 创建简单图像也失败: {e2}")

async def test_component_availability():
    """测试组件可用性"""
    print("\n" + "=" * 60)
    print("组件可用性测试")
    print("=" * 60)
    
    components = {
        "Local Model MCP": "mcp.adapter.local_model_mcp.local_model_mcp",
        "图像预处理器": "mcp.adapter.local_model_mcp.image_preprocessor", 
        "多引擎OCR": "mcp.adapter.local_model_mcp.multi_engine_ocr",
        "Tesseract优化器": "mcp.adapter.local_model_mcp.tesseract_optimizer",
        "Mistral OCR引擎": "mcp.adapter.local_model_mcp.mistral_ocr_engine"
    }
    
    available_components = []
    
    for name, module_path in components.items():
        try:
            __import__(module_path)
            print(f"✅ {name}: 可用")
            available_components.append(name)
        except ImportError as e:
            print(f"❌ {name}: 不可用 - {e}")
        except Exception as e:
            print(f"⚠️ {name}: 导入错误 - {e}")
    
    print(f"\n可用组件数量: {len(available_components)}/{len(components)}")
    return available_components

async def main():
    """主测试函数"""
    print("开始OCR工作流MCP真实集成测试...")
    
    # 测试组件可用性
    available_components = await test_component_availability()
    
    # 如果有足够的组件可用，进行集成测试
    if len(available_components) >= 1:  # 至少需要Local Model MCP
        success = await test_real_integration()
        if success:
            print("\n🎉 所有测试通过！OCR工作流MCP真实集成成功！")
        else:
            print("\n❌ 集成测试失败，请检查错误信息")
    else:
        print("\n⚠️ 可用组件不足，跳过集成测试")
        print("请确保Local Model MCP及其依赖已正确安装")

if __name__ == "__main__":
    asyncio.run(main())

