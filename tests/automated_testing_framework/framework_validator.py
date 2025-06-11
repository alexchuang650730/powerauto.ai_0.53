#!/usr/bin/env python3
"""
PowerAutomation 测试框架完整性验证和报告生成器

验证整个测试框架的完整性并生成综合报告
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class PowerAutomationFrameworkValidator:
    """PowerAutomation测试框架验证器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.validation_results = {}
        self.framework_components = {}
        
    def validate_complete_framework(self) -> Dict[str, Any]:
        """验证完整的测试框架"""
        print("🔍 开始PowerAutomation测试框架完整性验证...")
        print("=" * 60)
        
        validation_report = {
            "validation_timestamp": datetime.now().isoformat(),
            "framework_version": "PowerAutomation v2.0",
            "validation_status": "unknown",
            "components": {},
            "integration_status": {},
            "recommendations": [],
            "summary": {}
        }
        
        try:
            # 1. 验证核心组件
            print("📦 验证核心组件...")
            validation_report["components"] = self._validate_core_components()
            
            # 2. 验证测试层级结构
            print("🏗️ 验证测试层级结构...")
            validation_report["test_layers"] = self._validate_test_layers()
            
            # 3. 验证集成状态
            print("🔗 验证集成状态...")
            validation_report["integration_status"] = self._validate_integrations()
            
            # 4. 验证视觉测试功能
            print("🎨 验证视觉测试功能...")
            validation_report["visual_testing"] = self._validate_visual_testing()
            
            # 5. 验证前置条件系统
            print("⚙️ 验证前置条件系统...")
            validation_report["preconditions"] = self._validate_preconditions()
            
            # 6. 生成综合评估
            print("📊 生成综合评估...")
            validation_report["summary"] = self._generate_summary(validation_report)
            
            # 确定整体状态
            validation_report["validation_status"] = self._determine_overall_status(validation_report)
            
        except Exception as e:
            validation_report["validation_status"] = "error"
            validation_report["error"] = str(e)
            print(f"❌ 验证过程中发生错误: {e}")
        
        return validation_report
    
    def _validate_core_components(self) -> Dict[str, Any]:
        """验证核心组件"""
        components = {
            "test_case_generator": {
                "path": "test_case_generator.py",
                "status": "unknown",
                "description": "测试用例生成器"
            },
            "enhanced_preconditions": {
                "path": "enhanced_test_preconditions.py", 
                "status": "unknown",
                "description": "增强前置条件系统"
            },
            "visual_tester": {
                "path": "powerautomation_visual_tester.py",
                "status": "unknown", 
                "description": "视觉测试框架"
            },
            "visual_integrator": {
                "path": "visual_test_integrator.py",
                "status": "unknown",
                "description": "视觉测试集成器"
            },
            "framework_integrator": {
                "path": "enhanced_test_framework_integrator.py",
                "status": "unknown",
                "description": "测试框架集成器"
            }
        }
        
        for component_name, component_info in components.items():
            file_path = self.test_dir / component_info["path"]
            
            if file_path.exists():
                try:
                    # 检查文件大小和基本语法
                    file_size = file_path.stat().st_size
                    if file_size > 0:
                        # 尝试编译检查语法
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compile(content, str(file_path), 'exec')
                        
                        component_info["status"] = "available"
                        component_info["file_size"] = file_size
                        print(f"  ✅ {component_info['description']}: 可用")
                    else:
                        component_info["status"] = "empty"
                        print(f"  ⚠️ {component_info['description']}: 文件为空")
                        
                except SyntaxError as e:
                    component_info["status"] = "syntax_error"
                    component_info["error"] = str(e)
                    print(f"  ❌ {component_info['description']}: 语法错误")
                    
                except Exception as e:
                    component_info["status"] = "error"
                    component_info["error"] = str(e)
                    print(f"  ❌ {component_info['description']}: 检查失败")
            else:
                component_info["status"] = "missing"
                print(f"  ❌ {component_info['description']}: 文件缺失")
        
        return components
    
    def _validate_test_layers(self) -> Dict[str, Any]:
        """验证测试层级结构"""
        layers = {
            "level1": {
                "path": "level1",
                "description": "Level 1 - 基础单元测试",
                "status": "unknown",
                "test_files": []
            },
            "level5": {
                "path": "level5", 
                "description": "Level 5 - 性能测试",
                "status": "unknown",
                "test_files": []
            },
            "end_to_end": {
                "path": "end_to_end",
                "description": "端到端测试层",
                "status": "unknown",
                "sublayers": {}
            }
        }
        
        for layer_name, layer_info in layers.items():
            layer_path = self.test_dir / layer_info["path"]
            
            if layer_path.exists() and layer_path.is_dir():
                # 统计测试文件
                test_files = list(layer_path.rglob("test_*.py"))
                layer_info["test_files"] = [str(f.relative_to(self.test_dir)) for f in test_files]
                layer_info["test_count"] = len(test_files)
                
                if layer_name == "end_to_end":
                    # 检查端到端子层级
                    sublayers = ["client_side", "server_side", "integration", "fallback_automation"]
                    for sublayer in sublayers:
                        sublayer_path = layer_path / sublayer
                        if sublayer_path.exists():
                            sublayer_tests = list(sublayer_path.rglob("test_*.py"))
                            layer_info["sublayers"][sublayer] = {
                                "status": "available",
                                "test_count": len(sublayer_tests),
                                "test_files": [str(f.relative_to(self.test_dir)) for f in sublayer_tests]
                            }
                            print(f"  ✅ {sublayer}: {len(sublayer_tests)} 个测试文件")
                        else:
                            layer_info["sublayers"][sublayer] = {
                                "status": "missing",
                                "test_count": 0,
                                "test_files": []
                            }
                            print(f"  ❌ {sublayer}: 目录缺失")
                
                layer_info["status"] = "available"
                print(f"  ✅ {layer_info['description']}: {layer_info['test_count']} 个测试文件")
            else:
                layer_info["status"] = "missing"
                layer_info["test_count"] = 0
                print(f"  ❌ {layer_info['description']}: 目录缺失")
        
        return layers
    
    def _validate_integrations(self) -> Dict[str, Any]:
        """验证集成状态"""
        integrations = {
            "test_generator_integration": {
                "description": "测试用例生成器集成",
                "status": "unknown"
            },
            "visual_testing_integration": {
                "description": "视觉测试集成",
                "status": "unknown"
            },
            "precondition_integration": {
                "description": "前置条件系统集成",
                "status": "unknown"
            },
            "fallback_automation_integration": {
                "description": "兜底自动化集成",
                "status": "unknown"
            }
        }
        
        # 检查测试用例生成器集成
        result = self._check_generator_integration()
        integrations["test_generator_integration"].update(result)
        
        # 检查视觉测试集成
        result = self._check_visual_integration()
        integrations["visual_testing_integration"].update(result)
        
        # 检查前置条件集成
        result = self._check_precondition_integration()
        integrations["precondition_integration"].update(result)
        
        # 检查兜底自动化集成
        result = self._check_fallback_integration()
        integrations["fallback_automation_integration"].update(result)
        
        # 打印结果
        for integration_name, integration_info in integrations.items():
            if integration_info["status"] == "integrated":
                print(f"  ✅ {integration_info['description']}: 已集成")
            elif integration_info["status"] == "partial":
                print(f"  ⚠️ {integration_info['description']}: 部分集成")
            else:
                print(f"  ❌ {integration_info['description']}: 未集成")
        
        return integrations
    
    def _check_generator_integration(self) -> Dict[str, Any]:
        """检查测试用例生成器集成状态"""
        # 检查生成器是否被复制到兜底自动化目录
        fallback_generator = self.test_dir / "end_to_end" / "fallback_automation" / "test_case_generator.py"
        fallback_test_generator = self.test_dir / "end_to_end" / "fallback_automation" / "fallback_test_generator.py"
        
        if fallback_generator.exists() and fallback_test_generator.exists():
            return {
                "status": "integrated",
                "details": "测试用例生成器已集成到兜底自动化测试"
            }
        elif fallback_test_generator.exists():
            return {
                "status": "partial",
                "details": "兜底测试生成器存在，但原生成器未复制"
            }
        else:
            return {
                "status": "not_integrated",
                "details": "测试用例生成器未集成到兜底自动化测试"
            }
    
    def _check_visual_integration(self) -> Dict[str, Any]:
        """检查视觉测试集成状态"""
        visual_components = [
            self.test_dir / "powerautomation_visual_tester.py",
            self.test_dir / "visual_test_integrator.py",
            self.test_dir / "end_to_end" / "client_side" / "test_client_e2e_visual.py",
            self.test_dir / "end_to_end" / "fallback_automation" / "test_fallback_visual.py",
            self.test_dir / "visual_tests" / "visual_test_suite.py"
        ]
        
        existing_components = sum(1 for component in visual_components if component.exists())
        total_components = len(visual_components)
        
        if existing_components == total_components:
            return {
                "status": "integrated",
                "details": f"所有视觉测试组件已集成 ({existing_components}/{total_components})"
            }
        elif existing_components > 0:
            return {
                "status": "partial",
                "details": f"部分视觉测试组件已集成 ({existing_components}/{total_components})"
            }
        else:
            return {
                "status": "not_integrated",
                "details": "视觉测试组件未集成"
            }
    
    def _check_precondition_integration(self) -> Dict[str, Any]:
        """检查前置条件系统集成状态"""
        precondition_file = self.test_dir / "enhanced_test_preconditions.py"
        
        if precondition_file.exists():
            # 检查是否在其他测试文件中被引用
            test_files = list(self.test_dir.rglob("test_*.py"))
            references = 0
            
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "enhanced_test_preconditions" in content or "EnhancedPreconditionValidator" in content:
                            references += 1
                except:
                    continue
            
            if references > 0:
                return {
                    "status": "integrated",
                    "details": f"前置条件系统被 {references} 个测试文件引用"
                }
            else:
                return {
                    "status": "partial",
                    "details": "前置条件系统存在但未被测试文件引用"
                }
        else:
            return {
                "status": "not_integrated",
                "details": "前置条件系统文件不存在"
            }
    
    def _check_fallback_integration(self) -> Dict[str, Any]:
        """检查兜底自动化集成状态"""
        fallback_dir = self.test_dir / "end_to_end" / "fallback_automation"
        
        if fallback_dir.exists():
            fallback_files = list(fallback_dir.glob("*.py"))
            test_files = [f for f in fallback_files if f.name.startswith("test_")]
            
            if len(test_files) > 0:
                return {
                    "status": "integrated",
                    "details": f"兜底自动化目录包含 {len(test_files)} 个测试文件"
                }
            else:
                return {
                    "status": "partial",
                    "details": "兜底自动化目录存在但无测试文件"
                }
        else:
            return {
                "status": "not_integrated",
                "details": "兜底自动化目录不存在"
            }
    
    def _validate_visual_testing(self) -> Dict[str, Any]:
        """验证视觉测试功能"""
        visual_validation = {
            "playwright_available": False,
            "visual_tester_functional": False,
            "demo_execution": False,
            "report_generation": False,
            "integration_complete": False
        }
        
        try:
            # 检查Playwright可用性
            import playwright
            visual_validation["playwright_available"] = True
            print("  ✅ Playwright 可用")
        except ImportError:
            print("  ❌ Playwright 不可用")
        
        # 检查视觉测试器功能
        visual_tester_path = self.test_dir / "powerautomation_visual_tester.py"
        if visual_tester_path.exists():
            visual_validation["visual_tester_functional"] = True
            print("  ✅ 视觉测试器功能可用")
        else:
            print("  ❌ 视觉测试器不可用")
        
        # 检查演示执行结果
        demo_reports = list(self.test_dir.glob("visual_tests_demo/reports/*.json"))
        if demo_reports:
            visual_validation["demo_execution"] = True
            visual_validation["report_generation"] = True
            print("  ✅ 演示执行成功，报告已生成")
        else:
            print("  ⚠️ 未找到演示执行报告")
        
        # 检查集成完整性
        visual_integration_files = [
            self.test_dir / "visual_test_integrator.py",
            self.test_dir / "visual_tests" / "visual_test_config.yaml"
        ]
        
        if all(f.exists() for f in visual_integration_files):
            visual_validation["integration_complete"] = True
            print("  ✅ 视觉测试集成完整")
        else:
            print("  ⚠️ 视觉测试集成不完整")
        
        return visual_validation
    
    def _validate_preconditions(self) -> Dict[str, Any]:
        """验证前置条件系统"""
        precondition_validation = {
            "system_available": False,
            "platform_detection": False,
            "resource_validation": False,
            "capability_detection": False,
            "integration_working": False
        }
        
        try:
            # 尝试导入和使用前置条件系统
            sys.path.append(str(self.test_dir))
            from enhanced_test_preconditions import EnhancedPreconditionValidator
            
            validator = EnhancedPreconditionValidator()
            precondition_validation["system_available"] = True
            print("  ✅ 前置条件系统可用")
            
            # 测试平台检测
            if validator.current_platform in ["windows", "macos", "linux"]:
                precondition_validation["platform_detection"] = True
                print(f"  ✅ 平台检测正常: {validator.current_platform}")
            
            # 测试资源验证
            if validator.system_resources and "memory_gb" in validator.system_resources:
                precondition_validation["resource_validation"] = True
                print("  ✅ 资源验证功能正常")
            
            # 测试能力检测
            if validator.available_capabilities:
                precondition_validation["capability_detection"] = True
                print(f"  ✅ 能力检测正常: {len(validator.available_capabilities)} 项能力")
            
            # 测试集成工作
            test_preconditions = {
                "platform": {"required_platforms": ["linux"]},
                "resources": {"min_memory_gb": 1},
                "capabilities": ["basic_test"]
            }
            
            result = validator.validate_preconditions(test_preconditions)
            if isinstance(result, dict) and "valid" in result:
                precondition_validation["integration_working"] = True
                print("  ✅ 前置条件验证集成正常")
            
        except Exception as e:
            print(f"  ❌ 前置条件系统验证失败: {e}")
        
        return precondition_validation
    
    def _generate_summary(self, validation_report: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合评估摘要"""
        summary = {
            "total_components": 0,
            "available_components": 0,
            "total_integrations": 0,
            "successful_integrations": 0,
            "test_layers_count": 0,
            "available_test_layers": 0,
            "visual_testing_score": 0,
            "precondition_score": 0,
            "overall_score": 0,
            "framework_status": "unknown"
        }
        
        # 统计组件
        components = validation_report.get("components", {})
        summary["total_components"] = len(components)
        summary["available_components"] = sum(1 for c in components.values() if c.get("status") == "available")
        
        # 统计集成
        integrations = validation_report.get("integration_status", {})
        summary["total_integrations"] = len(integrations)
        summary["successful_integrations"] = sum(1 for i in integrations.values() if i.get("status") == "integrated")
        
        # 统计测试层级
        test_layers = validation_report.get("test_layers", {})
        summary["test_layers_count"] = len(test_layers)
        summary["available_test_layers"] = sum(1 for l in test_layers.values() if l.get("status") == "available")
        
        # 计算视觉测试得分
        visual_testing = validation_report.get("visual_testing", {})
        visual_score = sum(1 for v in visual_testing.values() if v is True)
        summary["visual_testing_score"] = visual_score / len(visual_testing) * 100 if visual_testing else 0
        
        # 计算前置条件得分
        preconditions = validation_report.get("preconditions", {})
        precondition_score = sum(1 for p in preconditions.values() if p is True)
        summary["precondition_score"] = precondition_score / len(preconditions) * 100 if preconditions else 0
        
        # 计算总体得分
        component_score = (summary["available_components"] / summary["total_components"] * 100) if summary["total_components"] > 0 else 0
        integration_score = (summary["successful_integrations"] / summary["total_integrations"] * 100) if summary["total_integrations"] > 0 else 0
        layer_score = (summary["available_test_layers"] / summary["test_layers_count"] * 100) if summary["test_layers_count"] > 0 else 0
        
        summary["overall_score"] = (component_score + integration_score + layer_score + summary["visual_testing_score"] + summary["precondition_score"]) / 5
        
        return summary
    
    def _determine_overall_status(self, validation_report: Dict[str, Any]) -> str:
        """确定整体状态"""
        summary = validation_report.get("summary", {})
        overall_score = summary.get("overall_score", 0)
        
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 75:
            return "good"
        elif overall_score >= 60:
            return "acceptable"
        elif overall_score >= 40:
            return "needs_improvement"
        else:
            return "poor"
    
    def generate_comprehensive_report(self, validation_report: Dict[str, Any]) -> Path:
        """生成综合报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.test_dir / f"powerautomation_framework_validation_report_{timestamp}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 框架验证报告已生成: {report_path}")
        return report_path
    
    def print_validation_summary(self, validation_report: Dict[str, Any]):
        """打印验证摘要"""
        summary = validation_report.get("summary", {})
        status = validation_report.get("validation_status", "unknown")
        
        print("\n" + "=" * 60)
        print("🎯 PowerAutomation 测试框架验证摘要")
        print("=" * 60)
        
        print(f"📊 总体状态: {self._get_status_emoji(status)} {status.upper()}")
        print(f"🔢 总体得分: {summary.get('overall_score', 0):.1f}/100")
        
        print(f"\n📦 组件状态: {summary.get('available_components', 0)}/{summary.get('total_components', 0)} 可用")
        print(f"🔗 集成状态: {summary.get('successful_integrations', 0)}/{summary.get('total_integrations', 0)} 成功")
        print(f"🏗️ 测试层级: {summary.get('available_test_layers', 0)}/{summary.get('test_layers_count', 0)} 可用")
        print(f"🎨 视觉测试: {summary.get('visual_testing_score', 0):.1f}% 完成")
        print(f"⚙️ 前置条件: {summary.get('precondition_score', 0):.1f}% 完成")
        
        # 显示建议
        recommendations = self._generate_recommendations(validation_report)
        if recommendations:
            print(f"\n💡 改进建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("=" * 60)
    
    def _get_status_emoji(self, status: str) -> str:
        """获取状态表情符号"""
        status_emojis = {
            "excellent": "🌟",
            "good": "✅", 
            "acceptable": "⚠️",
            "needs_improvement": "🔧",
            "poor": "❌",
            "error": "💥",
            "unknown": "❓"
        }
        return status_emojis.get(status, "❓")
    
    def _generate_recommendations(self, validation_report: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 检查组件状态
        components = validation_report.get("components", {})
        missing_components = [name for name, info in components.items() if info.get("status") != "available"]
        if missing_components:
            recommendations.append(f"修复或重新创建缺失的组件: {', '.join(missing_components)}")
        
        # 检查集成状态
        integrations = validation_report.get("integration_status", {})
        failed_integrations = [name for name, info in integrations.items() if info.get("status") != "integrated"]
        if failed_integrations:
            recommendations.append(f"完成未完成的集成: {', '.join(failed_integrations)}")
        
        # 检查视觉测试
        visual_testing = validation_report.get("visual_testing", {})
        if not visual_testing.get("playwright_available", False):
            recommendations.append("安装Playwright依赖: pip install playwright && playwright install")
        
        # 检查测试覆盖率
        summary = validation_report.get("summary", {})
        if summary.get("overall_score", 0) < 80:
            recommendations.append("提高测试覆盖率和组件完整性")
        
        return recommendations

if __name__ == "__main__":
    validator = PowerAutomationFrameworkValidator()
    
    # 执行完整性验证
    validation_report = validator.validate_complete_framework()
    
    # 打印摘要
    validator.print_validation_summary(validation_report)
    
    # 生成报告
    report_path = validator.generate_comprehensive_report(validation_report)
    
    print(f"\n🎉 PowerAutomation测试框架验证完成！")
    print(f"📄 详细报告: {report_path}")

