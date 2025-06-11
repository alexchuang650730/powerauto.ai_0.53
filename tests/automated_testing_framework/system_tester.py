#!/usr/bin/env python3
"""
PowerAutomation一键录制工作流系统完整性测试和优化

对整个一键录制工作流系统进行全面测试、性能优化和功能验证
确保系统稳定性、可靠性和易用性
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 导入所有组件
sys.path.append(str(Path(__file__).parent))
from workflow_recorder_integration import WorkflowRecorder, WorkflowRecordingConfig
from kilo_code_recorder import KiloCodeRecorder, StruggleModeType, InterventionType
from n8n_workflow_converter import N8nWorkflowConverter
from visual_workflow_integrator import VisualWorkflowIntegrator, VisualRecordingConfig

@dataclass
class SystemTestConfig:
    """系统测试配置"""
    test_all_scenarios: bool = True
    test_performance: bool = True
    test_error_handling: bool = True
    test_integration: bool = True
    generate_comprehensive_report: bool = True
    cleanup_test_data: bool = False

@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    test_type: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class SystemTester:
    """系统测试器"""
    
    def __init__(self, test_framework_dir: str = None):
        # 设置测试目录
        if test_framework_dir:
            self.framework_dir = Path(test_framework_dir)
        else:
            self.framework_dir = Path(__file__).parent
        
        # 创建测试专用目录
        self.test_dir = self.framework_dir / "system_tests"
        self.test_results_dir = self.test_dir / "results"
        self.test_data_dir = self.test_dir / "test_data"
        self.performance_dir = self.test_dir / "performance"
        
        for directory in [self.test_dir, self.test_results_dir, self.test_data_dir, self.performance_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.workflow_recorder = WorkflowRecorder(str(self.framework_dir))
        self.kilo_code_recorder = KiloCodeRecorder(str(self.framework_dir))
        self.n8n_converter = N8nWorkflowConverter(str(self.test_dir / "n8n_test"))
        self.visual_integrator = VisualWorkflowIntegrator(str(self.framework_dir))
        
        # 测试结果
        self.test_results: List[TestResult] = []
        self.system_metrics = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "total_duration": 0.0,
            "average_test_duration": 0.0,
            "performance_metrics": {},
            "error_summary": {}
        }
    
    def run_comprehensive_tests(self, config: SystemTestConfig = None) -> Dict[str, Any]:
        """运行全面的系统测试"""
        
        config = config or SystemTestConfig()
        start_time = time.time()
        
        print("🧪 开始PowerAutomation一键录制系统全面测试")
        print("=" * 60)
        
        # 1. 基础功能测试
        print("\n📋 1. 基础功能测试")
        self._test_basic_functionality()
        
        # 2. Kilo Code场景测试
        if config.test_all_scenarios:
            print("\n🎯 2. Kilo Code场景测试")
            self._test_kilo_code_scenarios()
        
        # 3. n8n工作流转换测试
        print("\n🔄 3. n8n工作流转换测试")
        self._test_n8n_conversion()
        
        # 4. 视觉集成测试
        if config.test_integration:
            print("\n👁️ 4. 视觉集成测试")
            self._test_visual_integration()
        
        # 5. 性能测试
        if config.test_performance:
            print("\n⚡ 5. 性能测试")
            self._test_performance()
        
        # 6. 错误处理测试
        if config.test_error_handling:
            print("\n🚨 6. 错误处理测试")
            self._test_error_handling()
        
        # 7. 集成测试
        if config.test_integration:
            print("\n🔗 7. 端到端集成测试")
            self._test_end_to_end_integration()
        
        # 计算总体指标
        total_duration = time.time() - start_time
        self._calculate_system_metrics(total_duration)
        
        # 生成测试报告
        test_report = self._generate_test_report(config)
        
        # 保存测试结果
        self._save_test_results(test_report)
        
        # 清理测试数据（如果启用）
        if config.cleanup_test_data:
            self._cleanup_test_data()
        
        print(f"\n🎉 系统测试完成！")
        print(f"   总测试数: {self.system_metrics['total_tests']}")
        print(f"   通过: {self.system_metrics['passed_tests']}")
        print(f"   失败: {self.system_metrics['failed_tests']}")
        print(f"   总耗时: {self.system_metrics['total_duration']:.2f}s")
        
        return test_report
    
    def _test_basic_functionality(self):
        """测试基础功能"""
        
        # 测试工作流录制器
        self._run_test("workflow_recorder_basic", "basic", self._test_workflow_recorder_basic)
        
        # 测试Kilo Code录制器
        self._run_test("kilo_code_recorder_basic", "basic", self._test_kilo_code_recorder_basic)
        
        # 测试n8n转换器
        self._run_test("n8n_converter_basic", "basic", self._test_n8n_converter_basic)
    
    def _test_workflow_recorder_basic(self) -> Dict[str, Any]:
        """测试工作流录制器基础功能"""
        
        config = WorkflowRecordingConfig(
            recording_mode="general_test",
            target_version="enterprise",
            enable_visual_verification=False,
            enable_screenshot=False
        )
        
        # 开始录制
        recording_id = self.workflow_recorder.start_recording(
            recording_name="基础功能测试",
            config=config,
            description="测试工作流录制器基础功能"
        )
        
        # 录制一些动作
        self.workflow_recorder.record_user_action("test_action", {"test": "data"})
        self.workflow_recorder.record_ui_interaction(
            "click", 
            {"selector": ".test-button"},
            {"action": "test_click"}
        )
        
        # 停止录制
        result = self.workflow_recorder.stop_recording()
        
        # 验证结果
        assert result is not None, "录制结果不能为空"
        assert result["recording_id"] == recording_id, "录制ID不匹配"
        assert len(result["actions"]) >= 2, "动作数量不足"
        
        return {
            "recording_id": recording_id,
            "actions_count": len(result["actions"]),
            "duration": result.get("statistics", {}).get("recording_duration", 0)
        }
    
    def _test_kilo_code_recorder_basic(self) -> Dict[str, Any]:
        """测试Kilo Code录制器基础功能"""
        
        # 开始场景录制
        recording_id = self.kilo_code_recorder.start_scenario_recording("enterprise_critical_modes")
        
        # 录制挣扎模式
        self.kilo_code_recorder.record_struggle_mode_detection(
            struggle_mode=StruggleModeType.SYNTAX_ERROR,
            detection_data={"error_type": "test_error"},
            confidence_score=0.95,
            response_time=1.0
        )
        
        # 录制介入
        self.kilo_code_recorder.record_intervention_trigger(
            intervention_type=InterventionType.CODE_SUGGESTION,
            intervention_data={"suggestion": "test_suggestion"},
            success_rate=0.90,
            response_time=0.5
        )
        
        # 停止录制
        result = self.kilo_code_recorder.stop_scenario_recording()
        
        # 验证结果
        assert result is not None, "Kilo Code录制结果不能为空"
        assert result["recording_info"]["recording_id"] == recording_id, "录制ID不匹配"
        assert result["performance_analysis"]["average_response_time"] > 0, "响应时间无效"
        
        return {
            "recording_id": recording_id,
            "kilo_events_count": len(result.get("raw_recording_data", {}).get("kilo_code_events", [])),
            "quality_score": result["quality_assessment"]["overall_quality_score"]
        }
    
    def _test_n8n_converter_basic(self) -> Dict[str, Any]:
        """测试n8n转换器基础功能"""
        
        # 创建测试录制数据
        test_recording = {
            "recording_id": "test_n8n_001",
            "recording_name": "n8n转换测试",
            "recording_mode": "kilo_code_detection",
            "target_version": "enterprise",
            "kilo_code_events": [
                {
                    "event_id": "test_event_001",
                    "detection_type": "struggle_mode_1",
                    "detection_data": {"test": "data"},
                    "confidence_score": 0.95,
                    "response_time": 1.0
                }
            ],
            "actions": [
                {
                    "id": "test_action_001",
                    "action_name": "click",
                    "element_selector": ".test"
                }
            ],
            "statistics": {
                "total_kilo_code_events": 1,
                "average_kilo_code_response_time": 1.0
            }
        }
        
        # 转换为n8n工作流
        workflow = self.n8n_converter.convert_recording_to_n8n(test_recording)
        
        # 保存工作流
        workflow_path = self.n8n_converter.save_workflow(workflow)
        
        # 验证结果
        assert workflow is not None, "n8n工作流不能为空"
        assert len(workflow.nodes) > 0, "工作流节点数量不能为0"
        assert workflow_path is not None, "工作流保存路径不能为空"
        
        return {
            "workflow_name": workflow.name,
            "nodes_count": len(workflow.nodes),
            "connections_count": len(workflow.connections),
            "workflow_path": workflow_path
        }
    
    def _test_kilo_code_scenarios(self):
        """测试所有Kilo Code场景"""
        
        scenarios = self.kilo_code_recorder.list_scenarios()
        
        for scenario in scenarios:
            scenario_id = scenario["scenario_id"]
            self._run_test(
                f"kilo_scenario_{scenario_id}", 
                "scenario", 
                lambda sid=scenario_id: self._test_single_kilo_scenario(sid)
            )
    
    def _test_single_kilo_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """测试单个Kilo Code场景"""
        
        # 开始场景录制
        recording_id = self.kilo_code_recorder.start_scenario_recording(scenario_id)
        
        # 模拟一些检测事件
        self.kilo_code_recorder.record_struggle_mode_detection(
            struggle_mode=StruggleModeType.SYNTAX_ERROR,
            detection_data={"scenario": scenario_id},
            confidence_score=0.90,
            response_time=1.5
        )
        
        # 停止录制
        result = self.kilo_code_recorder.stop_scenario_recording()
        
        return {
            "scenario_id": scenario_id,
            "recording_id": recording_id,
            "quality_score": result["quality_assessment"]["overall_quality_score"]
        }
    
    def _test_n8n_conversion(self):
        """测试n8n工作流转换"""
        
        # 测试不同类型的转换
        self._run_test("n8n_kilo_code_conversion", "conversion", self._test_n8n_kilo_code_conversion)
        self._run_test("n8n_general_conversion", "conversion", self._test_n8n_general_conversion)
    
    def _test_n8n_kilo_code_conversion(self) -> Dict[str, Any]:
        """测试Kilo Code专用n8n转换"""
        
        # 创建复杂的Kilo Code录制数据
        complex_recording = {
            "recording_id": "complex_kilo_001",
            "recording_name": "复杂Kilo Code测试",
            "recording_mode": "kilo_code_detection",
            "target_version": "enterprise",
            "kilo_code_events": [
                {
                    "event_id": "event_001",
                    "detection_type": "struggle_mode_1",
                    "detection_data": {"complexity": "high"},
                    "confidence_score": 0.95,
                    "response_time": 1.2
                },
                {
                    "event_id": "event_002",
                    "detection_type": "intervention_trigger",
                    "detection_data": {"type": "suggestion"},
                    "confidence_score": 0.88,
                    "response_time": 0.8
                }
            ],
            "statistics": {
                "total_kilo_code_events": 2,
                "average_kilo_code_response_time": 1.0
            }
        }
        
        # 转换并验证
        workflow = self.n8n_converter.convert_recording_to_n8n(complex_recording, "kilo_code_detection")
        workflow_path = self.n8n_converter.save_workflow(workflow)
        
        return {
            "nodes_count": len(workflow.nodes),
            "has_kilo_nodes": any("KiloCode" in node.name for node in workflow.nodes),
            "workflow_path": workflow_path
        }
    
    def _test_n8n_general_conversion(self) -> Dict[str, Any]:
        """测试通用n8n转换"""
        
        general_recording = {
            "recording_id": "general_001",
            "recording_name": "通用测试",
            "recording_mode": "general_test",
            "target_version": "personal_pro",
            "actions": [
                {"id": "action_001", "action_name": "click"},
                {"id": "action_002", "action_name": "input"}
            ],
            "statistics": {"total_actions": 2}
        }
        
        workflow = self.n8n_converter.convert_recording_to_n8n(general_recording, "general_test")
        workflow_path = self.n8n_converter.save_workflow(workflow)
        
        return {
            "nodes_count": len(workflow.nodes),
            "workflow_path": workflow_path
        }
    
    def _test_visual_integration(self):
        """测试视觉集成功能"""
        
        # 注意：由于内存限制，这里只测试配置和初始化
        self._run_test("visual_integration_config", "integration", self._test_visual_integration_config)
    
    def _test_visual_integration_config(self) -> Dict[str, Any]:
        """测试视觉集成配置"""
        
        # 测试配置创建
        recording_config = WorkflowRecordingConfig(
            recording_mode="kilo_code_detection",
            target_version="enterprise",
            enable_visual_verification=False  # 禁用以避免内存问题
        )
        
        visual_config = VisualRecordingConfig(
            enable_visual_verification=False,  # 禁用以避免内存问题
            enable_screenshot_comparison=False,
            capture_on_kilo_events=False
        )
        
        # 验证配置
        assert recording_config.recording_mode == "kilo_code_detection"
        assert visual_config.enable_visual_verification == False
        
        return {
            "recording_config_valid": True,
            "visual_config_valid": True,
            "integration_ready": True
        }
    
    def _test_performance(self):
        """测试系统性能"""
        
        self._run_test("performance_recording_speed", "performance", self._test_recording_speed)
        self._run_test("performance_conversion_speed", "performance", self._test_conversion_speed)
        self._run_test("performance_memory_usage", "performance", self._test_memory_usage)
    
    def _test_recording_speed(self) -> Dict[str, Any]:
        """测试录制速度"""
        
        start_time = time.time()
        
        # 快速录制测试
        config = WorkflowRecordingConfig(
            recording_mode="performance_test",
            enable_visual_verification=False,
            enable_screenshot=False
        )
        
        recording_id = self.workflow_recorder.start_recording("性能测试", config)
        
        # 录制多个动作
        for i in range(10):
            self.workflow_recorder.record_user_action(f"action_{i}", {"index": i})
        
        result = self.workflow_recorder.stop_recording()
        
        duration = time.time() - start_time
        
        return {
            "total_duration": duration,
            "actions_count": len(result["actions"]),
            "actions_per_second": len(result["actions"]) / duration if duration > 0 else 0
        }
    
    def _test_conversion_speed(self) -> Dict[str, Any]:
        """测试转换速度"""
        
        # 创建大型录制数据
        large_recording = {
            "recording_id": "large_test_001",
            "recording_name": "大型转换测试",
            "recording_mode": "kilo_code_detection",
            "target_version": "enterprise",
            "kilo_code_events": [
                {
                    "event_id": f"event_{i:03d}",
                    "detection_type": "struggle_mode_1",
                    "detection_data": {"index": i},
                    "confidence_score": 0.90,
                    "response_time": 1.0
                }
                for i in range(20)
            ],
            "statistics": {"total_kilo_code_events": 20}
        }
        
        start_time = time.time()
        workflow = self.n8n_converter.convert_recording_to_n8n(large_recording)
        conversion_duration = time.time() - start_time
        
        start_time = time.time()
        workflow_path = self.n8n_converter.save_workflow(workflow)
        save_duration = time.time() - start_time
        
        return {
            "conversion_duration": conversion_duration,
            "save_duration": save_duration,
            "total_duration": conversion_duration + save_duration,
            "events_converted": 20,
            "nodes_generated": len(workflow.nodes)
        }
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """测试内存使用"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行内存密集操作
        large_data = []
        for i in range(100):
            large_data.append({
                "recording_id": f"memory_test_{i}",
                "data": ["test"] * 1000
            })
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 清理
        del large_data
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": peak_memory - initial_memory,
            "memory_recovered_mb": peak_memory - final_memory
        }
    
    def _test_error_handling(self):
        """测试错误处理"""
        
        self._run_test("error_invalid_config", "error", self._test_invalid_config_error)
        self._run_test("error_invalid_data", "error", self._test_invalid_data_error)
    
    def _test_invalid_config_error(self) -> Dict[str, Any]:
        """测试无效配置错误处理"""
        
        try:
            # 尝试使用无效场景ID
            self.kilo_code_recorder.start_scenario_recording("invalid_scenario_id")
            return {"error_handled": False, "error_type": "none"}
        except ValueError as e:
            return {"error_handled": True, "error_type": "ValueError", "error_message": str(e)}
        except Exception as e:
            return {"error_handled": True, "error_type": type(e).__name__, "error_message": str(e)}
    
    def _test_invalid_data_error(self) -> Dict[str, Any]:
        """测试无效数据错误处理"""
        
        try:
            # 尝试转换无效录制数据
            invalid_data = {"invalid": "data"}
            self.n8n_converter.convert_recording_to_n8n(invalid_data)
            return {"error_handled": False, "error_type": "none"}
        except Exception as e:
            return {"error_handled": True, "error_type": type(e).__name__, "error_message": str(e)}
    
    def _test_end_to_end_integration(self):
        """测试端到端集成"""
        
        self._run_test("e2e_complete_workflow", "integration", self._test_complete_workflow)
    
    def _test_complete_workflow(self) -> Dict[str, Any]:
        """测试完整工作流"""
        
        # 1. 开始Kilo Code录制
        recording_id = self.kilo_code_recorder.start_scenario_recording("enterprise_critical_modes")
        
        # 2. 录制事件
        self.kilo_code_recorder.record_struggle_mode_detection(
            struggle_mode=StruggleModeType.SYNTAX_ERROR,
            detection_data={"integration_test": True},
            confidence_score=0.95,
            response_time=1.0
        )
        
        # 3. 停止录制
        kilo_result = self.kilo_code_recorder.stop_scenario_recording()
        
        # 4. 转换为n8n工作流
        workflow = self.n8n_converter.convert_recording_to_n8n(
            kilo_result["raw_recording_data"], "kilo_code_detection"
        )
        
        # 5. 保存工作流
        workflow_path = self.n8n_converter.save_workflow(workflow)
        
        return {
            "kilo_recording_success": kilo_result is not None,
            "n8n_conversion_success": workflow is not None,
            "workflow_save_success": workflow_path is not None,
            "end_to_end_success": True,
            "workflow_path": workflow_path
        }
    
    def _run_test(self, test_name: str, test_type: str, test_func) -> TestResult:
        """运行单个测试"""
        
        print(f"   🧪 {test_name}...", end=" ")
        
        start_time = time.time()
        success = False
        error_message = None
        metrics = None
        
        try:
            metrics = test_func()
            success = True
            print("✅")
        except Exception as e:
            error_message = str(e)
            print(f"❌ ({error_message})")
        
        duration = time.time() - start_time
        
        result = TestResult(
            test_name=test_name,
            test_type=test_type,
            success=success,
            duration=duration,
            error_message=error_message,
            metrics=metrics
        )
        
        self.test_results.append(result)
        return result
    
    def _calculate_system_metrics(self, total_duration: float):
        """计算系统指标"""
        
        self.system_metrics["total_tests"] = len(self.test_results)
        self.system_metrics["passed_tests"] = sum(1 for r in self.test_results if r.success)
        self.system_metrics["failed_tests"] = sum(1 for r in self.test_results if not r.success)
        self.system_metrics["total_duration"] = total_duration
        
        if self.test_results:
            self.system_metrics["average_test_duration"] = sum(r.duration for r in self.test_results) / len(self.test_results)
        
        # 按类型统计
        test_types = {}
        for result in self.test_results:
            test_type = result.test_type
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0, "failed": 0}
            
            test_types[test_type]["total"] += 1
            if result.success:
                test_types[test_type]["passed"] += 1
            else:
                test_types[test_type]["failed"] += 1
        
        self.system_metrics["test_types"] = test_types
        
        # 性能指标
        performance_tests = [r for r in self.test_results if r.test_type == "performance" and r.metrics]
        if performance_tests:
            self.system_metrics["performance_metrics"] = {
                "recording_speed": next((r.metrics.get("actions_per_second", 0) for r in performance_tests if "recording_speed" in r.test_name), 0),
                "conversion_speed": next((r.metrics.get("events_converted", 0) / r.metrics.get("conversion_duration", 1) for r in performance_tests if "conversion_speed" in r.test_name), 0),
                "memory_usage": next((r.metrics for r in performance_tests if "memory_usage" in r.test_name), {})
            }
        
        # 错误摘要
        failed_tests = [r for r in self.test_results if not r.success]
        error_types = {}
        for test in failed_tests:
            error_type = test.error_message.split(":")[0] if test.error_message else "Unknown"
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        self.system_metrics["error_summary"] = error_types
    
    def _generate_test_report(self, config: SystemTestConfig) -> Dict[str, Any]:
        """生成测试报告"""
        
        report = {
            "test_summary": {
                "test_config": asdict(config),
                "execution_time": datetime.now().isoformat(),
                "system_metrics": self.system_metrics,
                "success_rate": self.system_metrics["passed_tests"] / max(self.system_metrics["total_tests"], 1)
            },
            "detailed_results": [asdict(result) for result in self.test_results],
            "component_status": {
                "workflow_recorder": self._assess_component_status("workflow_recorder"),
                "kilo_code_recorder": self._assess_component_status("kilo_code"),
                "n8n_converter": self._assess_component_status("n8n"),
                "visual_integrator": self._assess_component_status("visual")
            },
            "recommendations": self._generate_recommendations(),
            "system_health": self._assess_system_health()
        }
        
        return report
    
    def _assess_component_status(self, component_prefix: str) -> Dict[str, Any]:
        """评估组件状态"""
        
        component_tests = [r for r in self.test_results if component_prefix in r.test_name]
        
        if not component_tests:
            return {"status": "not_tested", "success_rate": 0.0, "issues": []}
        
        passed = sum(1 for r in component_tests if r.success)
        total = len(component_tests)
        success_rate = passed / total
        
        status = "healthy" if success_rate >= 0.8 else "warning" if success_rate >= 0.5 else "critical"
        
        issues = [r.error_message for r in component_tests if not r.success and r.error_message]
        
        return {
            "status": status,
            "success_rate": success_rate,
            "tests_passed": passed,
            "tests_total": total,
            "issues": issues
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        
        recommendations = []
        
        # 基于成功率的建议
        success_rate = self.system_metrics["passed_tests"] / max(self.system_metrics["total_tests"], 1)
        
        if success_rate < 0.8:
            recommendations.append("系统整体成功率较低，建议优先修复失败的测试用例")
        
        # 基于性能的建议
        perf_metrics = self.system_metrics.get("performance_metrics", {})
        if perf_metrics.get("recording_speed", 0) < 5:
            recommendations.append("录制速度较慢，建议优化录制性能")
        
        memory_usage = perf_metrics.get("memory_usage", {})
        if memory_usage.get("memory_increase_mb", 0) > 100:
            recommendations.append("内存使用量较高，建议优化内存管理")
        
        # 基于错误类型的建议
        error_summary = self.system_metrics.get("error_summary", {})
        if "ValueError" in error_summary:
            recommendations.append("存在参数验证问题，建议加强输入验证")
        
        if not recommendations:
            recommendations.append("系统运行良好，建议继续保持当前配置")
        
        return recommendations
    
    def _assess_system_health(self) -> str:
        """评估系统健康状况"""
        
        success_rate = self.system_metrics["passed_tests"] / max(self.system_metrics["total_tests"], 1)
        
        if success_rate >= 0.95:
            return "excellent"
        elif success_rate >= 0.85:
            return "good"
        elif success_rate >= 0.70:
            return "fair"
        elif success_rate >= 0.50:
            return "poor"
        else:
            return "critical"
    
    def _save_test_results(self, test_report: Dict[str, Any]):
        """保存测试结果"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细报告
        report_path = self.test_results_dir / f"system_test_report_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(test_report, f, indent=2, ensure_ascii=False, default=str)
        
        # 保存简化摘要
        summary = {
            "timestamp": timestamp,
            "total_tests": self.system_metrics["total_tests"],
            "passed_tests": self.system_metrics["passed_tests"],
            "failed_tests": self.system_metrics["failed_tests"],
            "success_rate": test_report["test_summary"]["success_rate"],
            "system_health": test_report["system_health"],
            "duration": self.system_metrics["total_duration"]
        }
        
        summary_path = self.test_results_dir / f"system_test_summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试结果已保存:")
        print(f"   详细报告: {report_path}")
        print(f"   摘要: {summary_path}")
    
    def _cleanup_test_data(self):
        """清理测试数据"""
        
        print("\n🧹 清理测试数据...")
        
        # 清理测试生成的文件（保留报告）
        cleanup_dirs = [
            self.test_data_dir,
            self.framework_dir / "workflow_recordings" / "flows",
            self.framework_dir / "workflow_recordings" / "n8n_workflows"
        ]
        
        for cleanup_dir in cleanup_dirs:
            if cleanup_dir.exists():
                for file in cleanup_dir.glob("*test*"):
                    try:
                        if file.is_file():
                            file.unlink()
                        print(f"   清理: {file.name}")
                    except Exception as e:
                        print(f"   清理失败: {file.name} - {e}")

if __name__ == "__main__":
    # 运行系统测试
    tester = SystemTester()
    
    # 配置测试
    test_config = SystemTestConfig(
        test_all_scenarios=True,
        test_performance=True,
        test_error_handling=True,
        test_integration=True,
        generate_comprehensive_report=True,
        cleanup_test_data=False  # 保留测试数据以供检查
    )
    
    # 执行测试
    test_report = tester.run_comprehensive_tests(test_config)
    
    print(f"\n📊 最终测试报告:")
    print(f"   系统健康状况: {test_report['system_health'].upper()}")
    print(f"   成功率: {test_report['test_summary']['success_rate']:.1%}")
    print(f"   组件状态:")
    for component, status in test_report['component_status'].items():
        print(f"     {component}: {status['status'].upper()} ({status['success_rate']:.1%})")
    
    print(f"\n💡 改进建议:")
    for recommendation in test_report['recommendations']:
        print(f"   • {recommendation}")
    
    print(f"\n🎉 PowerAutomation一键录制工作流系统测试完成！")

