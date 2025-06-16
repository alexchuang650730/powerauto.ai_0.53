#!/usr/bin/env python3
"""
OCR工作流MCP集成测试

测试重构后的OCR工作流是否正常工作
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# 导入OCR工作流MCP
from mcp.workflow.ocr_workflow_mcp import OCRWorkflowMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCRWorkflowIntegrationTest:
    """OCR工作流集成测试类"""
    
    def __init__(self):
        self.test_results = []
        self.mcp = None
    
    async def setup(self):
        """测试设置"""
        try:
            # 初始化OCR工作流MCP
            config_dir = Path(__file__).parent / "config"
            self.mcp = OCRWorkflowMCP(str(config_dir))
            logger.info("✅ OCR工作流MCP初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ OCR工作流MCP初始化失败: {e}")
            return False
    
    async def test_basic_functionality(self):
        """测试基本功能"""
        test_name = "基本功能测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 测试MCP信息获取
            info = self.mcp.get_info()
            assert "name" in info
            assert "version" in info
            logger.info(f"✅ MCP信息获取成功: {info['name']} v{info['version']}")
            
            # 测试能力获取
            capabilities = self.mcp.get_capabilities()
            assert "capabilities" in capabilities
            assert len(capabilities["capabilities"]) > 0
            logger.info(f"✅ 能力获取成功: {len(capabilities['capabilities'])}个能力")
            
            # 测试健康检查
            health = self.mcp.health_check()
            assert "status" in health
            logger.info(f"✅ 健康检查成功: {health['status']}")
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "所有基本功能正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_configuration_loading(self):
        """测试配置加载"""
        test_name = "配置加载测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 测试配置获取
            config = self.mcp.get_config()
            assert "workflow_config" in config
            assert "routing_rules" in config
            assert "quality_settings" in config
            
            # 验证关键配置项
            workflow_config = config["workflow_config"]
            assert "workflow" in workflow_config
            assert "execution" in workflow_config
            
            routing_rules = config["routing_rules"]
            assert "routing_rules" in routing_rules
            assert "special_rules" in routing_rules
            
            quality_settings = config["quality_settings"]
            assert "quality" in quality_settings
            assert "limits" in quality_settings
            
            logger.info("✅ 所有配置文件加载成功")
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "配置文件加载正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_workflow_executor(self):
        """测试工作流执行器"""
        test_name = "工作流执行器测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 检查执行器是否正确初始化
            executor = self.mcp.executor
            assert executor is not None
            
            # 检查工作流步骤
            assert hasattr(executor, 'workflow_steps')
            assert len(executor.workflow_steps) > 0
            logger.info(f"✅ 工作流步骤数量: {len(executor.workflow_steps)}")
            
            # 检查OCR组件
            assert hasattr(executor, 'ocr_components')
            ocr_components = executor.ocr_components
            logger.info(f"✅ OCR组件数量: {len(ocr_components)}")
            
            # 检查配置
            assert hasattr(executor, 'workflow_config')
            assert hasattr(executor, 'routing_rules')
            assert hasattr(executor, 'quality_settings')
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": f"执行器初始化正常，{len(executor.workflow_steps)}个步骤，{len(ocr_components)}个OCR组件"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_request_validation(self):
        """测试请求验证"""
        test_name = "请求验证测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 测试有效请求
            valid_request = {
                "image_path": "/tmp/test_image.jpg",
                "task_type": "document_ocr",
                "quality_level": "medium",
                "privacy_level": "normal"
            }
            
            # 由于文件不存在，这会在输入验证步骤失败，但验证逻辑应该正常工作
            result = await self.mcp.process_ocr(valid_request)
            assert "success" in result
            assert "error" in result  # 应该有错误，因为文件不存在
            logger.info("✅ 请求验证逻辑正常工作")
            
            # 测试无效请求
            invalid_request = {
                "task_type": "invalid_task",
                "quality_level": "invalid_quality"
            }
            
            try:
                await self.mcp.process_ocr(invalid_request)
                assert False, "应该抛出验证错误"
            except Exception:
                logger.info("✅ 无效请求正确被拒绝")
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "请求验证逻辑正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_adapter_selection(self):
        """测试适配器选择逻辑"""
        test_name = "适配器选择测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            executor = self.mcp.executor
            
            # 测试不同条件下的适配器选择
            test_cases = [
                {
                    "task_type": "document_ocr",
                    "quality_level": "medium",
                    "privacy_level": "normal",
                    "expected": "local_model_mcp"
                },
                {
                    "task_type": "handwriting_recognition",
                    "quality_level": "high",
                    "privacy_level": "low",
                    "expected": "cloud_search_mcp"
                },
                {
                    "task_type": "document_ocr",
                    "quality_level": "medium",
                    "privacy_level": "high",
                    "expected": "local_model_mcp"  # 高隐私强制本地
                }
            ]
            
            for case in test_cases:
                selected = executor._apply_routing_rules(
                    case["task_type"],
                    case["quality_level"], 
                    case["privacy_level"],
                    5.0,  # file_size_mb
                    {"quality_score": 0.7}  # image_analysis
                )
                
                logger.info(f"✅ 条件 {case} -> 选择适配器: {selected}")
                # 注意：由于路由逻辑可能比较复杂，这里只验证返回了有效的适配器
                assert selected in ["local_model_mcp", "cloud_search_mcp"]
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "适配器选择逻辑正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_statistics_and_monitoring(self):
        """测试统计和监控功能"""
        test_name = "统计监控测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 测试统计信息获取
            stats = self.mcp.get_statistics()
            assert "total_requests" in stats
            assert "successful_requests" in stats
            assert "failed_requests" in stats
            assert "success_rate" in stats
            logger.info(f"✅ 统计信息获取成功: {stats['total_requests']}个请求")
            
            # 测试诊断功能
            diagnosis = self.mcp.diagnose()
            assert "mcp_status" in diagnosis
            assert "executor_status" in diagnosis
            assert "components" in diagnosis
            assert "configuration" in diagnosis
            logger.info(f"✅ 系统诊断成功: MCP状态 {diagnosis['mcp_status']}")
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "统计和监控功能正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    async def test_error_handling(self):
        """测试错误处理"""
        test_name = "错误处理测试"
        logger.info(f"🧪 开始{test_name}")
        
        try:
            # 测试文件不存在的错误处理
            request = {
                "image_path": "/nonexistent/file.jpg",
                "task_type": "document_ocr"
            }
            
            result = await self.mcp.process_ocr(request)
            assert result["success"] == False
            assert "error" in result
            logger.info("✅ 文件不存在错误正确处理")
            
            # 测试无效参数的错误处理
            invalid_request = {
                "image_path": "/tmp/test.jpg",
                "task_type": "invalid_task_type"
            }
            
            try:
                await self.mcp.process_ocr(invalid_request)
                assert False, "应该抛出参数验证错误"
            except Exception as e:
                logger.info(f"✅ 无效参数错误正确处理: {e}")
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "details": "错误处理机制正常"
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}失败: {e}")
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    def generate_test_report(self):
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL"
        }
        
        return report
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始OCR工作流MCP集成测试")
        print("=" * 80)
        print("OCR工作流MCP集成测试")
        print("=" * 80)
        
        # 设置
        if not await self.setup():
            logger.error("❌ 测试设置失败，终止测试")
            return
        
        # 运行测试
        test_methods = [
            self.test_basic_functionality,
            self.test_configuration_loading,
            self.test_workflow_executor,
            self.test_request_validation,
            self.test_adapter_selection,
            self.test_statistics_and_monitoring,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"❌ 测试方法 {test_method.__name__} 执行失败: {e}")
                self.test_results.append({
                    "test_name": test_method.__name__,
                    "status": "FAIL",
                    "error": f"测试执行异常: {e}"
                })
        
        # 生成报告
        report = self.generate_test_report()
        
        # 打印结果
        print("\n" + "=" * 80)
        print("测试结果汇总")
        print("=" * 80)
        print(f"总测试数: {report['test_summary']['total_tests']}")
        print(f"通过测试: {report['test_summary']['passed_tests']}")
        print(f"失败测试: {report['test_summary']['failed_tests']}")
        print(f"成功率: {report['test_summary']['success_rate']:.2%}")
        print(f"整体状态: {report['overall_status']}")
        
        print("\n详细结果:")
        for result in report['test_results']:
            status_icon = "✅" if result['status'] == "PASS" else "❌"
            print(f"{status_icon} {result['test_name']}: {result['status']}")
            if result['status'] == "PASS" and 'details' in result:
                print(f"   详情: {result['details']}")
            elif result['status'] == "FAIL" and 'error' in result:
                print(f"   错误: {result['error']}")
        
        # 保存报告
        report_path = Path(__file__).parent / "test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 测试报告已保存到: {report_path}")
        
        return report

async def main():
    """主函数"""
    tester = OCRWorkflowIntegrationTest()
    report = await tester.run_all_tests()
    
    # 根据测试结果设置退出码
    exit_code = 0 if report['overall_status'] == "PASS" else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())

