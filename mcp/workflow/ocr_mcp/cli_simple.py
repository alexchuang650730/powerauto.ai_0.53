#!/usr/bin/env python3
"""
OCR工作流MCP - 简化命令行接口

提供基本的CLI功能用于测试
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path

# 添加src路径
sys.path.append(str(Path(__file__).parent / "src"))

from ocr_workflow_mcp import OCRWorkflowMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCRWorkflowCLI:
    """OCR工作流命令行接口"""
    
    def __init__(self):
        self.mcp = None
    
    def setup_mcp(self, config_dir: str = None):
        """初始化MCP"""
        try:
            self.mcp = OCRWorkflowMCP(config_dir)
            logger.info("OCR工作流MCP初始化成功")
        except Exception as e:
            logger.error(f"MCP初始化失败: {e}")
            sys.exit(1)
    
    async def process_single_image(self, args) -> dict:
        """处理单个图像"""
        request = {
            "image_path": args.image,
            "task_type": args.task_type,
            "quality_level": args.quality,
            "privacy_level": args.privacy,
            "language": args.language,
            "output_format": args.output_format
        }
        
        logger.info(f"开始处理图像: {args.image}")
        result = await self.mcp.process_ocr(request)
        
        return result
    
    def show_info(self, args):
        """显示MCP信息"""
        info = self.mcp.get_info()
        capabilities = self.mcp.get_capabilities()
        stats = self.mcp.get_statistics()
        
        print("=" * 60)
        print("OCR工作流MCP信息")
        print("=" * 60)
        print(f"名称: {info['name']}")
        print(f"版本: {info['version']}")
        print(f"描述: {info['description']}")
        print()
        
        print("支持的能力:")
        for capability in capabilities['capabilities']:
            print(f"  - {capability}")
        print()
        
        print("支持的格式:")
        for fmt in capabilities['supported_formats']:
            print(f"  - {fmt}")
        print()
        
        print("可用适配器:")
        for adapter in capabilities['adapters']:
            print(f"  - {adapter}")
        print()
        
        print("统计信息:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功请求数: {stats['successful_requests']}")
        print(f"  失败请求数: {stats['failed_requests']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        print(f"  平均处理时间: {stats['average_processing_time']:.2f}秒")
    
    def show_health(self, args):
        """显示健康状态"""
        health = self.mcp.health_check()
        
        print("=" * 60)
        print("OCR工作流MCP健康检查")
        print("=" * 60)
        print(f"整体状态: {health['status']}")
        print(f"执行器状态: {health['executor_status']}")
        print()
        
        print("OCR组件状态:")
        for component, status in health['ocr_components'].items():
            print(f"  {component}: {status}")
        print()
        
        print(f"总请求数: {health['total_requests']}")
        print(f"成功率: {health['success_rate']:.2%}")
    
    def show_diagnosis(self, args):
        """显示诊断信息"""
        diagnosis = self.mcp.diagnose()
        
        print("=" * 60)
        print("OCR工作流MCP系统诊断")
        print("=" * 60)
        print(f"MCP状态: {diagnosis['mcp_status']}")
        print(f"执行器状态: {diagnosis['executor_status']}")
        print()
        
        print("组件状态:")
        for component, info in diagnosis['components'].items():
            print(f"  {component}: {info['status']} ({info['type']})")
        print()
        
        print("配置状态:")
        for config, loaded in diagnosis['configuration'].items():
            status = "已加载" if loaded else "未加载"
            print(f"  {config}: {status}")
        print()
        
        if diagnosis['recommendations']:
            print("建议:")
            for recommendation in diagnosis['recommendations']:
                print(f"  - {recommendation}")
        else:
            print("系统运行正常，无特殊建议")

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="OCR工作流MCP命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 全局参数
    parser.add_argument("--config-dir", help="配置目录路径")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="日志级别")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # process命令 - 处理单个图像
    process_parser = subparsers.add_parser("process", help="处理单个图像")
    process_parser.add_argument("--image", required=True, help="图像文件路径")
    process_parser.add_argument("--task-type", default="document_ocr",
                               choices=["document_ocr", "handwriting_recognition", 
                                       "table_extraction", "form_processing", 
                                       "complex_document", "multi_language_ocr"],
                               help="任务类型")
    process_parser.add_argument("--quality", default="medium",
                               choices=["low", "medium", "high", "ultra_high"],
                               help="质量级别")
    process_parser.add_argument("--privacy", default="normal",
                               choices=["low", "normal", "high"],
                               help="隐私级别")
    process_parser.add_argument("--language", default="auto", help="语言设置")
    process_parser.add_argument("--output-format", default="structured_json",
                               choices=["plain_text", "structured_json"],
                               help="输出格式")
    
    # info命令 - 显示信息
    subparsers.add_parser("info", help="显示MCP信息")
    
    # health命令 - 健康检查
    subparsers.add_parser("health", help="健康检查")
    
    # diagnose命令 - 系统诊断
    subparsers.add_parser("diagnose", help="系统诊断")
    
    return parser

async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 初始化CLI
    cli = OCRWorkflowCLI()
    cli.setup_mcp(args.config_dir)
    
    try:
        # 执行命令
        if args.command == "process":
            result = await cli.process_single_image(args)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == "info":
            cli.show_info(args)
        
        elif args.command == "health":
            cli.show_health(args)
        
        elif args.command == "diagnose":
            cli.show_diagnosis(args)
        
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

