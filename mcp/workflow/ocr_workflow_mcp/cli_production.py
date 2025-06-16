#!/usr/bin/env python3
"""
OCR工作流MCP简化CLI - 生产就绪版本

提供简洁易用的命令行接口
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OCR工作流MCP - 智能OCR处理系统")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='显示MCP信息')
    
    # health命令
    health_parser = subparsers.add_parser('health', help='检查系统健康状态')
    
    # diagnose命令
    diagnose_parser = subparsers.add_parser('diagnose', help='运行系统诊断')
    
    # stats命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    # process命令
    process_parser = subparsers.add_parser('process', help='处理OCR请求')
    process_parser.add_argument('--image', required=True, help='图像文件路径')
    process_parser.add_argument('--task-type', default='document_ocr', 
                               choices=['document_ocr', 'handwriting_recognition', 'table_extraction', 
                                       'form_processing', 'complex_document', 'multi_language_ocr'],
                               help='任务类型')
    process_parser.add_argument('--quality', default='medium',
                               choices=['low', 'medium', 'high', 'ultra_high'],
                               help='质量级别')
    process_parser.add_argument('--privacy', default='normal',
                               choices=['low', 'normal', 'high'],
                               help='隐私级别')
    process_parser.add_argument('--language', default='auto', help='语言设置')
    process_parser.add_argument('--output', help='输出文件路径')
    
    # test命令
    test_parser = subparsers.add_parser('test', help='运行集成测试')
    test_parser.add_argument('--quick', action='store_true', help='快速测试模式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    if args.command == 'info':
        show_info()
    elif args.command == 'health':
        check_health()
    elif args.command == 'diagnose':
        run_diagnose()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'process':
        asyncio.run(process_ocr(args))
    elif args.command == 'test':
        asyncio.run(run_test(args.quick))

def show_info():
    """显示MCP信息"""
    try:
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        mcp = OCRWorkflowMCP()
        info = mcp.get_info()
        
        print("=" * 60)
        print("OCR工作流MCP信息")
        print("=" * 60)
        print(f"名称: {info['name']}")
        print(f"版本: {info['version']}")
        print(f"描述: {info['description']}")
        print(f"\n支持的能力:")
        for capability in info['capabilities']:
            print(f"  • {capability}")
        print(f"\n支持的格式:")
        for format_type in info['supported_formats']:
            print(f"  • {format_type}")
        print(f"\n可用适配器:")
        for adapter in info['adapters']:
            print(f"  • {adapter}")
        
    except Exception as e:
        print(f"❌ 获取信息失败: {e}")

def check_health():
    """检查健康状态"""
    try:
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        mcp = OCRWorkflowMCP()
        health = mcp.health_check()
        
        print("=" * 60)
        print("系统健康检查")
        print("=" * 60)
        
        status = health.get('status', 'unknown')
        if status == 'healthy':
            print("✅ 系统状态: 健康")
        else:
            print("❌ 系统状态: 不健康")
        
        print(f"执行器状态: {health.get('executor_status', 'unknown')}")
        print(f"总请求数: {health.get('total_requests', 0)}")
        print(f"成功率: {health.get('success_rate', 0.0):.2%}")
        
        print("\nOCR组件状态:")
        components = health.get('ocr_components', {})
        for name, status in components.items():
            status_icon = "✅" if status == "available" else "❌"
            print(f"  {status_icon} {name}: {status}")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

def run_diagnose():
    """运行系统诊断"""
    try:
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        mcp = OCRWorkflowMCP()
        diagnosis = mcp.diagnose()
        
        print("=" * 60)
        print("系统诊断报告")
        print("=" * 60)
        
        print(f"MCP状态: {diagnosis.get('mcp_status', 'unknown')}")
        print(f"执行器状态: {diagnosis.get('executor_status', 'unknown')}")
        
        print("\n组件状态:")
        components = diagnosis.get('components', {})
        for name, info in components.items():
            status_icon = "✅" if info.get('status') == 'available' else "❌"
            print(f"  {status_icon} {name}: {info.get('status', 'unknown')} ({info.get('type', 'unknown')})")
        
        print("\n配置状态:")
        config = diagnosis.get('configuration', {})
        for key, value in config.items():
            status_icon = "✅" if value else "❌"
            print(f"  {status_icon} {key}: {'已加载' if value else '未加载'}")
        
        recommendations = diagnosis.get('recommendations', [])
        if recommendations:
            print("\n建议:")
            for rec in recommendations:
                print(f"  💡 {rec}")
        
    except Exception as e:
        print(f"❌ 系统诊断失败: {e}")

def show_stats():
    """显示统计信息"""
    try:
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        mcp = OCRWorkflowMCP()
        stats = mcp.get_statistics()
        
        print("=" * 60)
        print("统计信息")
        print("=" * 60)
        
        print(f"总请求数: {stats.get('total_requests', 0)}")
        print(f"成功请求: {stats.get('successful_requests', 0)}")
        print(f"失败请求: {stats.get('failed_requests', 0)}")
        print(f"成功率: {stats.get('success_rate', 0.0):.2%}")
        print(f"平均处理时间: {stats.get('average_processing_time', 0.0):.2f}秒")
        
        print("\n适配器使用分布:")
        adapter_dist = stats.get('adapter_distribution', {})
        for adapter, percentage in adapter_dist.items():
            print(f"  • {adapter}: {percentage:.2%}")
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")

async def process_ocr(args):
    """处理OCR请求"""
    try:
        from src.ocr_workflow_mcp import OCRWorkflowMCP
        
        # 检查图像文件
        if not os.path.exists(args.image):
            print(f"❌ 图像文件不存在: {args.image}")
            return
        
        print("=" * 60)
        print("OCR处理")
        print("=" * 60)
        print(f"图像文件: {args.image}")
        print(f"任务类型: {args.task_type}")
        print(f"质量级别: {args.quality}")
        print(f"隐私级别: {args.privacy}")
        print(f"语言设置: {args.language}")
        print()
        
        # 初始化MCP
        mcp = OCRWorkflowMCP()
        await mcp.initialize()
        
        # 创建请求
        request = {
            "image_path": args.image,
            "task_type": args.task_type,
            "quality_level": args.quality,
            "privacy_level": args.privacy,
            "language": args.language,
            "enable_preprocessing": True,
            "enable_postprocessing": True
        }
        
        # 处理OCR
        print("🔄 正在处理...")
        result = await mcp.process_ocr(request)
        
        # 显示结果
        if result.get('success'):
            print("✅ 处理成功!")
            print(f"处理时间: {result.get('processing_time', 0.0):.2f}秒")
            print(f"使用适配器: {result.get('adapter_used', 'unknown')}")
            print(f"置信度: {result.get('confidence', 0.0):.2f}")
            print(f"质量分数: {result.get('quality_score', 0.0):.2f}")
            
            text = result.get('text', '')
            if text:
                print(f"\n识别文本:")
                print("-" * 40)
                print(text)
                print("-" * 40)
                
                # 保存到文件
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"\n✅ 结果已保存到: {args.output}")
            else:
                print("\n⚠️ 未识别到文本内容")
        else:
            print("❌ 处理失败!")
            print(f"错误信息: {result.get('error', '未知错误')}")
        
        # 关闭MCP
        await mcp.shutdown()
        
    except Exception as e:
        print(f"❌ OCR处理失败: {e}")

async def run_test(quick_mode=False):
    """运行集成测试"""
    try:
        print("=" * 60)
        print("OCR工作流MCP集成测试")
        print("=" * 60)
        
        if quick_mode:
            print("🚀 快速测试模式")
            # 导入并运行简化测试
            from test_real_integration import test_component_availability
            available = await test_component_availability()
            
            if len(available) >= 3:
                print("✅ 快速测试通过!")
            else:
                print("❌ 快速测试失败，组件不足")
        else:
            print("🔍 完整测试模式")
            # 导入并运行完整测试
            from test_real_integration import test_real_integration
            success = await test_real_integration()
            
            if success:
                print("✅ 完整测试通过!")
            else:
                print("❌ 完整测试失败")
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

if __name__ == "__main__":
    main()

