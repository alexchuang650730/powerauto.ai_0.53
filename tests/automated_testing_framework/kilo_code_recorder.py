#!/usr/bin/env python3
"""
Kilo Code智能介入检测专用录制器

专门用于录制和验证Kilo Code引擎的7种挣扎模式检测、智能介入决策等功能
支持企业版和个人专业版的不同测试场景
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# 导入集成的录制器
sys.path.append(str(Path(__file__).parent))
from workflow_recorder_integration import WorkflowRecorder, WorkflowRecordingConfig, KiloCodeDetectionEvent

class StruggleModeType(Enum):
    """7种挣扎模式类型"""
    SYNTAX_ERROR = "struggle_mode_1"  # 语法错误挣扎
    LOGIC_ERROR = "struggle_mode_2"   # 逻辑错误挣扎
    PERFORMANCE_ISSUE = "struggle_mode_3"  # 性能问题挣扎
    API_CONFUSION = "struggle_mode_4"  # API使用困惑
    DESIGN_PATTERN = "struggle_mode_5"  # 设计模式挣扎
    DEBUGGING_STUCK = "struggle_mode_6"  # 调试卡住
    TESTING_DIFFICULTY = "struggle_mode_7"  # 测试困难

class InterventionType(Enum):
    """介入类型"""
    CODE_SUGGESTION = "code_suggestion"  # 代码建议
    ERROR_FIX = "error_fix"  # 错误修复
    REFACTOR_ADVICE = "refactor_advice"  # 重构建议
    PERFORMANCE_TIP = "performance_tip"  # 性能提示
    BEST_PRACTICE = "best_practice"  # 最佳实践
    DOCUMENTATION = "documentation"  # 文档引导
    TESTING_GUIDE = "testing_guide"  # 测试指导

@dataclass
class KiloCodeTestScenario:
    """Kilo Code测试场景"""
    scenario_id: str
    scenario_name: str
    target_version: str  # enterprise, personal_pro
    struggle_modes: List[StruggleModeType]
    expected_interventions: List[InterventionType]
    performance_requirements: Dict[str, float]  # response_time, accuracy_rate
    test_data: Dict[str, Any]

class KiloCodeRecorder:
    """Kilo Code专用录制器"""
    
    def __init__(self, test_framework_dir: str = None):
        # 初始化基础录制器
        self.workflow_recorder = WorkflowRecorder(test_framework_dir)
        
        # Kilo Code专用目录
        self.kilo_code_dir = self.workflow_recorder.recording_dir / "kilo_code_specialized"
        self.scenarios_dir = self.kilo_code_dir / "scenarios"
        self.results_dir = self.kilo_code_dir / "results"
        self.templates_dir = self.kilo_code_dir / "templates"
        
        for directory in [self.kilo_code_dir, self.scenarios_dir, self.results_dir, self.templates_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 预定义测试场景
        self.test_scenarios = self._load_predefined_scenarios()
        
        # 当前录制状态
        self.current_scenario: Optional[KiloCodeTestScenario] = None
        self.current_recording_id: Optional[str] = None
        self.detected_struggle_modes: List[str] = []
        self.triggered_interventions: List[str] = []
        
        # 性能监控
        self.performance_metrics = {
            "response_times": [],
            "accuracy_scores": [],
            "intervention_success_rate": 0.0
        }
    
    def _load_predefined_scenarios(self) -> Dict[str, KiloCodeTestScenario]:
        """加载预定义测试场景"""
        scenarios = {}
        
        # 企业版场景
        scenarios["enterprise_full_detection"] = KiloCodeTestScenario(
            scenario_id="enterprise_full_detection",
            scenario_name="企业版完整检测测试",
            target_version="enterprise",
            struggle_modes=[mode for mode in StruggleModeType],
            expected_interventions=[intervention for intervention in InterventionType],
            performance_requirements={
                "max_response_time": 3.0,
                "min_accuracy_rate": 0.85,
                "min_intervention_success_rate": 0.80
            },
            test_data={
                "code_complexity": "high",
                "team_size": "large",
                "project_type": "enterprise_application"
            }
        )
        
        scenarios["enterprise_critical_modes"] = KiloCodeTestScenario(
            scenario_id="enterprise_critical_modes",
            scenario_name="企业版关键模式测试",
            target_version="enterprise",
            struggle_modes=[
                StruggleModeType.SYNTAX_ERROR,
                StruggleModeType.LOGIC_ERROR,
                StruggleModeType.PERFORMANCE_ISSUE
            ],
            expected_interventions=[
                InterventionType.CODE_SUGGESTION,
                InterventionType.ERROR_FIX,
                InterventionType.PERFORMANCE_TIP
            ],
            performance_requirements={
                "max_response_time": 2.5,
                "min_accuracy_rate": 0.90,
                "min_intervention_success_rate": 0.85
            },
            test_data={
                "priority": "critical",
                "environment": "production"
            }
        )
        
        # 个人专业版场景
        scenarios["personal_pro_basic"] = KiloCodeTestScenario(
            scenario_id="personal_pro_basic",
            scenario_name="个人专业版基础测试",
            target_version="personal_pro",
            struggle_modes=[
                StruggleModeType.SYNTAX_ERROR,
                StruggleModeType.API_CONFUSION,
                StruggleModeType.DEBUGGING_STUCK
            ],
            expected_interventions=[
                InterventionType.CODE_SUGGESTION,
                InterventionType.DOCUMENTATION,
                InterventionType.BEST_PRACTICE
            ],
            performance_requirements={
                "max_response_time": 3.5,
                "min_accuracy_rate": 0.80,
                "min_intervention_success_rate": 0.75
            },
            test_data={
                "user_level": "intermediate",
                "project_type": "personal_project"
            }
        )
        
        scenarios["personal_pro_learning"] = KiloCodeTestScenario(
            scenario_id="personal_pro_learning",
            scenario_name="个人专业版学习场景",
            target_version="personal_pro",
            struggle_modes=[
                StruggleModeType.DESIGN_PATTERN,
                StruggleModeType.TESTING_DIFFICULTY
            ],
            expected_interventions=[
                InterventionType.BEST_PRACTICE,
                InterventionType.TESTING_GUIDE,
                InterventionType.DOCUMENTATION
            ],
            performance_requirements={
                "max_response_time": 4.0,
                "min_accuracy_rate": 0.75,
                "min_intervention_success_rate": 0.70
            },
            test_data={
                "user_level": "beginner",
                "learning_focus": "best_practices"
            }
        )
        
        return scenarios
    
    def start_scenario_recording(self, scenario_id: str, custom_config: Dict[str, Any] = None) -> str:
        """开始场景录制"""
        if scenario_id not in self.test_scenarios:
            raise ValueError(f"未知的测试场景: {scenario_id}")
        
        self.current_scenario = self.test_scenarios[scenario_id]
        
        # 配置录制参数
        config = WorkflowRecordingConfig(
            recording_mode="kilo_code_detection",
            target_version=self.current_scenario.target_version,
            enable_visual_verification=True,
            enable_screenshot=True,
            auto_generate_n8n=True,
            recording_quality="high"
        )
        
        # 应用自定义配置
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # 开始录制
        self.current_recording_id = self.workflow_recorder.start_recording(
            recording_name=f"KiloCode_{self.current_scenario.scenario_name}",
            config=config,
            description=f"Kilo Code场景测试: {self.current_scenario.scenario_name}"
        )
        
        # 重置状态
        self.detected_struggle_modes = []
        self.triggered_interventions = []
        self.performance_metrics = {
            "response_times": [],
            "accuracy_scores": [],
            "intervention_success_rate": 0.0
        }
        
        print(f"🎬 开始Kilo Code场景录制: {self.current_scenario.scenario_name}")
        print(f"   场景ID: {scenario_id}")
        print(f"   目标版本: {self.current_scenario.target_version}")
        print(f"   预期挣扎模式: {len(self.current_scenario.struggle_modes)} 种")
        print(f"   预期介入类型: {len(self.current_scenario.expected_interventions)} 种")
        
        return self.current_recording_id
    
    def record_struggle_mode_detection(self, struggle_mode: StruggleModeType, 
                                     detection_data: Dict[str, Any],
                                     confidence_score: float,
                                     response_time: float) -> str:
        """录制挣扎模式检测"""
        if not self.current_recording_id:
            raise RuntimeError("没有活跃的录制会话")
        
        # 记录检测事件
        event_id = self.workflow_recorder.record_kilo_code_detection(
            detection_type=struggle_mode.value,
            detection_data=detection_data,
            confidence_score=confidence_score,
            response_time=response_time
        )
        
        # 更新状态
        self.detected_struggle_modes.append(struggle_mode.value)
        self.performance_metrics["response_times"].append(response_time)
        self.performance_metrics["accuracy_scores"].append(confidence_score)
        
        # 验证性能要求
        self._validate_performance_requirements(response_time, confidence_score)
        
        print(f"📝 检测到挣扎模式: {struggle_mode.name} (置信度: {confidence_score:.2f}, 响应时间: {response_time:.2f}s)")
        
        return event_id
    
    def record_intervention_trigger(self, intervention_type: InterventionType,
                                  intervention_data: Dict[str, Any],
                                  success_rate: float,
                                  response_time: float) -> str:
        """录制智能介入触发"""
        if not self.current_recording_id:
            raise RuntimeError("没有活跃的录制会话")
        
        # 记录介入事件
        event_id = self.workflow_recorder.record_kilo_code_detection(
            detection_type="intervention_trigger",
            detection_data={
                "intervention_type": intervention_type.value,
                "intervention_data": intervention_data,
                "success_rate": success_rate
            },
            confidence_score=success_rate,
            response_time=response_time
        )
        
        # 更新状态
        self.triggered_interventions.append(intervention_type.value)
        self.performance_metrics["response_times"].append(response_time)
        
        print(f"🤖 触发智能介入: {intervention_type.name} (成功率: {success_rate:.2f}, 响应时间: {response_time:.2f}s)")
        
        return event_id
    
    def record_accuracy_validation(self, validation_data: Dict[str, Any]) -> str:
        """录制准确率验证"""
        if not self.current_recording_id:
            raise RuntimeError("没有活跃的录制会话")
        
        # 计算整体准确率
        overall_accuracy = self._calculate_overall_accuracy(validation_data)
        
        # 记录验证事件
        event_id = self.workflow_recorder.record_kilo_code_detection(
            detection_type="accuracy_validation",
            detection_data=validation_data,
            confidence_score=overall_accuracy,
            response_time=0.1  # 验证通常很快
        )
        
        print(f"✅ 准确率验证: {overall_accuracy:.2f}")
        
        return event_id
    
    def stop_scenario_recording(self) -> Dict[str, Any]:
        """停止场景录制并生成分析报告"""
        if not self.current_recording_id:
            raise RuntimeError("没有活跃的录制会话")
        
        # 停止基础录制
        recording_result = self.workflow_recorder.stop_recording()
        
        # 生成场景分析报告
        scenario_report = self._generate_scenario_report(recording_result)
        
        # 保存场景结果
        self._save_scenario_result(scenario_report)
        
        print(f"🎬 场景录制完成: {self.current_scenario.scenario_name}")
        print(f"   检测到挣扎模式: {len(self.detected_struggle_modes)}/{len(self.current_scenario.struggle_modes)}")
        print(f"   触发介入: {len(self.triggered_interventions)}")
        print(f"   平均响应时间: {scenario_report['performance_analysis']['average_response_time']:.2f}s")
        print(f"   平均准确率: {scenario_report['performance_analysis']['average_accuracy']:.2f}")
        
        # 重置状态
        self.current_scenario = None
        self.current_recording_id = None
        
        return scenario_report
    
    def _validate_performance_requirements(self, response_time: float, confidence_score: float):
        """验证性能要求"""
        if not self.current_scenario:
            return
        
        requirements = self.current_scenario.performance_requirements
        
        # 检查响应时间
        if response_time > requirements.get("max_response_time", 3.0):
            print(f"⚠️ 响应时间超标: {response_time:.2f}s > {requirements['max_response_time']}s")
        
        # 检查准确率
        if confidence_score < requirements.get("min_accuracy_rate", 0.85):
            print(f"⚠️ 准确率不足: {confidence_score:.2f} < {requirements['min_accuracy_rate']}")
    
    def _calculate_overall_accuracy(self, validation_data: Dict[str, Any]) -> float:
        """计算整体准确率"""
        if not self.performance_metrics["accuracy_scores"]:
            return 0.0
        
        return sum(self.performance_metrics["accuracy_scores"]) / len(self.performance_metrics["accuracy_scores"])
    
    def _generate_scenario_report(self, recording_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成场景分析报告"""
        if not self.current_scenario:
            return {}
        
        # 性能分析
        performance_analysis = {
            "average_response_time": sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0,
            "max_response_time": max(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0,
            "min_response_time": min(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0,
            "average_accuracy": sum(self.performance_metrics["accuracy_scores"]) / len(self.performance_metrics["accuracy_scores"]) if self.performance_metrics["accuracy_scores"] else 0,
            "response_time_compliance": sum(1 for rt in self.performance_metrics["response_times"] if rt <= self.current_scenario.performance_requirements.get("max_response_time", 3.0)) / len(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0,
            "accuracy_compliance": sum(1 for acc in self.performance_metrics["accuracy_scores"] if acc >= self.current_scenario.performance_requirements.get("min_accuracy_rate", 0.85)) / len(self.performance_metrics["accuracy_scores"]) if self.performance_metrics["accuracy_scores"] else 0
        }
        
        # 覆盖率分析
        coverage_analysis = {
            "struggle_mode_coverage": len(set(self.detected_struggle_modes)) / len(self.current_scenario.struggle_modes),
            "intervention_coverage": len(set(self.triggered_interventions)) / len(self.current_scenario.expected_interventions),
            "detected_struggle_modes": list(set(self.detected_struggle_modes)),
            "triggered_interventions": list(set(self.triggered_interventions)),
            "missing_struggle_modes": [mode.value for mode in self.current_scenario.struggle_modes if mode.value not in self.detected_struggle_modes],
            "missing_interventions": [intervention.value for intervention in self.current_scenario.expected_interventions if intervention.value not in self.triggered_interventions]
        }
        
        # 质量评估
        quality_score = (
            performance_analysis["response_time_compliance"] * 0.3 +
            performance_analysis["accuracy_compliance"] * 0.4 +
            coverage_analysis["struggle_mode_coverage"] * 0.2 +
            coverage_analysis["intervention_coverage"] * 0.1
        )
        
        report = {
            "scenario_info": asdict(self.current_scenario),
            "recording_info": {
                "recording_id": self.current_recording_id,
                "start_time": recording_result.get("start_time"),
                "end_time": recording_result.get("end_time"),
                "duration": recording_result.get("statistics", {}).get("recording_duration", 0)
            },
            "performance_analysis": performance_analysis,
            "coverage_analysis": coverage_analysis,
            "quality_assessment": {
                "overall_quality_score": quality_score,
                "performance_grade": self._get_performance_grade(performance_analysis),
                "coverage_grade": self._get_coverage_grade(coverage_analysis),
                "recommendations": self._generate_recommendations(performance_analysis, coverage_analysis)
            },
            "raw_recording_data": recording_result
        }
        
        return report
    
    def _get_performance_grade(self, performance_analysis: Dict[str, Any]) -> str:
        """获取性能等级"""
        compliance_avg = (performance_analysis["response_time_compliance"] + performance_analysis["accuracy_compliance"]) / 2
        
        if compliance_avg >= 0.95:
            return "A+"
        elif compliance_avg >= 0.90:
            return "A"
        elif compliance_avg >= 0.85:
            return "B+"
        elif compliance_avg >= 0.80:
            return "B"
        elif compliance_avg >= 0.70:
            return "C"
        else:
            return "D"
    
    def _get_coverage_grade(self, coverage_analysis: Dict[str, Any]) -> str:
        """获取覆盖率等级"""
        coverage_avg = (coverage_analysis["struggle_mode_coverage"] + coverage_analysis["intervention_coverage"]) / 2
        
        if coverage_avg >= 0.95:
            return "A+"
        elif coverage_avg >= 0.90:
            return "A"
        elif coverage_avg >= 0.85:
            return "B+"
        elif coverage_avg >= 0.80:
            return "B"
        elif coverage_avg >= 0.70:
            return "C"
        else:
            return "D"
    
    def _generate_recommendations(self, performance_analysis: Dict[str, Any], 
                                coverage_analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 性能建议
        if performance_analysis["response_time_compliance"] < 0.85:
            recommendations.append("建议优化Kilo Code引擎响应时间，当前响应时间超标率较高")
        
        if performance_analysis["accuracy_compliance"] < 0.85:
            recommendations.append("建议提升检测准确率，当前准确率未达到85%要求")
        
        # 覆盖率建议
        if coverage_analysis["struggle_mode_coverage"] < 0.90:
            missing_modes = coverage_analysis["missing_struggle_modes"]
            recommendations.append(f"建议增强以下挣扎模式的检测能力: {', '.join(missing_modes)}")
        
        if coverage_analysis["intervention_coverage"] < 0.80:
            missing_interventions = coverage_analysis["missing_interventions"]
            recommendations.append(f"建议完善以下介入类型的触发机制: {', '.join(missing_interventions)}")
        
        # 版本特定建议
        if self.current_scenario and self.current_scenario.target_version == "enterprise":
            if performance_analysis["average_response_time"] > 2.0:
                recommendations.append("企业版应优化到2秒内响应，以满足企业级性能要求")
        
        if not recommendations:
            recommendations.append("当前测试表现良好，建议继续保持并定期验证")
        
        return recommendations
    
    def _save_scenario_result(self, scenario_report: Dict[str, Any]):
        """保存场景结果"""
        if not self.current_scenario:
            return
        
        # 转换枚举类型为字符串以支持JSON序列化
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, (StruggleModeType, InterventionType)):
                return obj.value
            else:
                return obj
        
        serializable_report = convert_enums(scenario_report)
        
        # 保存详细报告
        report_path = self.results_dir / f"{self.current_scenario.scenario_id}_{self.current_recording_id}_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)
        
        # 保存简化摘要
        summary = {
            "scenario_id": self.current_scenario.scenario_id,
            "recording_id": self.current_recording_id,
            "timestamp": datetime.now().isoformat(),
            "quality_score": scenario_report["quality_assessment"]["overall_quality_score"],
            "performance_grade": scenario_report["quality_assessment"]["performance_grade"],
            "coverage_grade": scenario_report["quality_assessment"]["coverage_grade"],
            "average_response_time": scenario_report["performance_analysis"]["average_response_time"],
            "average_accuracy": scenario_report["performance_analysis"]["average_accuracy"]
        }
        
        summary_path = self.results_dir / f"{self.current_scenario.scenario_id}_{self.current_recording_id}_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 场景结果已保存:")
        print(f"   详细报告: {report_path}")
        print(f"   摘要: {summary_path}")
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """列出所有可用场景"""
        scenarios = []
        for scenario_id, scenario in self.test_scenarios.items():
            scenarios.append({
                "scenario_id": scenario_id,
                "scenario_name": scenario.scenario_name,
                "target_version": scenario.target_version,
                "struggle_modes_count": len(scenario.struggle_modes),
                "expected_interventions_count": len(scenario.expected_interventions),
                "max_response_time": scenario.performance_requirements.get("max_response_time", 0),
                "min_accuracy_rate": scenario.performance_requirements.get("min_accuracy_rate", 0)
            })
        
        return scenarios
    
    def get_scenario_history(self, scenario_id: str) -> List[Dict[str, Any]]:
        """获取场景历史记录"""
        history = []
        
        for summary_file in self.results_dir.glob(f"{scenario_id}_*_summary.json"):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                    history.append(summary)
            except Exception as e:
                print(f"⚠️ 读取历史记录失败 {summary_file}: {e}")
        
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)

if __name__ == "__main__":
    # 示例使用
    kilo_recorder = KiloCodeRecorder()
    
    # 列出可用场景
    scenarios = kilo_recorder.list_scenarios()
    print("📋 可用的Kilo Code测试场景:")
    for scenario in scenarios:
        print(f"   {scenario['scenario_id']}: {scenario['scenario_name']} ({scenario['target_version']})")
    
    # 执行企业版关键模式测试
    print(f"\n🎬 开始执行企业版关键模式测试...")
    
    recording_id = kilo_recorder.start_scenario_recording("enterprise_critical_modes")
    
    # 模拟挣扎模式检测
    kilo_recorder.record_struggle_mode_detection(
        struggle_mode=StruggleModeType.SYNTAX_ERROR,
        detection_data={"error_type": "missing_semicolon", "line": 42},
        confidence_score=0.95,
        response_time=1.2
    )
    
    kilo_recorder.record_struggle_mode_detection(
        struggle_mode=StruggleModeType.LOGIC_ERROR,
        detection_data={"error_type": "infinite_loop", "complexity": "medium"},
        confidence_score=0.88,
        response_time=2.1
    )
    
    kilo_recorder.record_struggle_mode_detection(
        struggle_mode=StruggleModeType.PERFORMANCE_ISSUE,
        detection_data={"issue_type": "memory_leak", "severity": "high"},
        confidence_score=0.92,
        response_time=1.8
    )
    
    # 模拟智能介入
    kilo_recorder.record_intervention_trigger(
        intervention_type=InterventionType.CODE_SUGGESTION,
        intervention_data={"suggestion": "添加分号", "confidence": 0.95},
        success_rate=0.90,
        response_time=0.8
    )
    
    kilo_recorder.record_intervention_trigger(
        intervention_type=InterventionType.ERROR_FIX,
        intervention_data={"fix_type": "loop_condition", "auto_fix": True},
        success_rate=0.85,
        response_time=1.5
    )
    
    # 验证准确率
    kilo_recorder.record_accuracy_validation({
        "total_detections": 3,
        "correct_detections": 3,
        "false_positives": 0,
        "false_negatives": 0
    })
    
    # 停止录制并生成报告
    scenario_report = kilo_recorder.stop_scenario_recording()
    
    print(f"\n📊 场景测试报告:")
    print(f"   质量评分: {scenario_report['quality_assessment']['overall_quality_score']:.2f}")
    print(f"   性能等级: {scenario_report['quality_assessment']['performance_grade']}")
    print(f"   覆盖率等级: {scenario_report['quality_assessment']['coverage_grade']}")
    
    print(f"\n🎉 Kilo Code专用录制器演示完成！")

