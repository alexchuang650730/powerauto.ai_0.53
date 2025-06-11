#!/usr/bin/env python3
"""
视觉验证与录制工作流协同集成器

将一键录制工作流功能与现有的视觉截图验证功能深度集成
实现录制过程中的自动视觉验证、截图对比、回归测试等功能
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# 导入现有组件
sys.path.append(str(Path(__file__).parent))
from workflow_recorder_integration import WorkflowRecorder, WorkflowRecordingConfig
from kilo_code_recorder import KiloCodeRecorder, StruggleModeType, InterventionType
from n8n_workflow_converter import N8nWorkflowConverter
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig, VisualTestResult

@dataclass
class VisualRecordingConfig:
    """视觉录制配置"""
    enable_visual_verification: bool = True
    enable_screenshot_comparison: bool = True
    enable_regression_testing: bool = True
    screenshot_interval: float = 2.0
    visual_threshold: float = 0.05
    auto_update_baseline: bool = False
    capture_on_kilo_events: bool = True
    capture_on_ui_interactions: bool = True
    generate_visual_report: bool = True

@dataclass
class VisualRecordingEvent:
    """视觉录制事件"""
    event_id: str
    event_type: str  # kilo_code, ui_interaction, manual_capture
    timestamp: str
    screenshot_path: Optional[str] = None
    baseline_path: Optional[str] = None
    comparison_result: Optional[VisualTestResult] = None
    visual_metadata: Optional[Dict[str, Any]] = None

class VisualWorkflowIntegrator:
    """视觉工作流集成器"""
    
    def __init__(self, test_framework_dir: str = None):
        # 设置基础目录
        if test_framework_dir:
            self.framework_dir = Path(test_framework_dir)
        else:
            self.framework_dir = Path(__file__).parent
        
        # 创建集成专用目录
        self.integration_dir = self.framework_dir / "visual_workflow_integration"
        self.visual_recordings_dir = self.integration_dir / "visual_recordings"
        self.baselines_dir = self.integration_dir / "baselines"
        self.comparisons_dir = self.integration_dir / "comparisons"
        self.reports_dir = self.integration_dir / "reports"
        
        for directory in [self.integration_dir, self.visual_recordings_dir, 
                         self.baselines_dir, self.comparisons_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.workflow_recorder = WorkflowRecorder(str(self.framework_dir))
        self.kilo_code_recorder = KiloCodeRecorder(str(self.framework_dir))
        self.n8n_converter = N8nWorkflowConverter(str(self.integration_dir / "n8n_workflows"))
        self.visual_tester: Optional[PowerAutomationVisualTester] = None
        
        # 当前会话状态
        self.current_session_id: Optional[str] = None
        self.current_config: Optional[VisualRecordingConfig] = None
        self.visual_events: List[VisualRecordingEvent] = []
        self.session_metadata: Dict[str, Any] = {}
        
        # 性能统计
        self.integration_stats = {
            "total_sessions": 0,
            "successful_sessions": 0,
            "total_visual_events": 0,
            "visual_regression_detected": 0,
            "average_visual_processing_time": 0.0
        }
    
    def start_visual_recording_session(self, session_name: str, 
                                     recording_config: WorkflowRecordingConfig = None,
                                     visual_config: VisualRecordingConfig = None,
                                     kilo_scenario_id: str = None) -> str:
        """开始视觉录制会话"""
        
        # 生成会话ID
        self.current_session_id = f"visual_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 设置配置
        self.current_config = visual_config or VisualRecordingConfig()
        recording_config = recording_config or WorkflowRecordingConfig()
        
        # 初始化视觉测试器
        if self.current_config.enable_visual_verification:
            try:
                visual_test_config = VisualTestConfig(
                    browser_type="chromium",
                    headless=False,
                    viewport_width=1920,
                    viewport_height=1080,
                    visual_threshold=self.current_config.visual_threshold,
                    auto_update_baseline=self.current_config.auto_update_baseline
                )
                
                self.visual_tester = PowerAutomationVisualTester(
                    test_dir=str(self.visual_recordings_dir),
                    config=visual_test_config
                )
                
                if self.visual_tester.start_browser():
                    print(f"✅ 视觉验证浏览器已启动")
                else:
                    print(f"⚠️ 视觉验证浏览器启动失败，将跳过视觉功能")
                    self.visual_tester = None
                    
            except Exception as e:
                print(f"⚠️ 视觉测试器初始化失败: {e}")
                self.visual_tester = None
        
        # 开始工作流录制
        workflow_recording_id = self.workflow_recorder.start_recording(
            recording_name=f"Visual_{session_name}",
            config=recording_config,
            description=f"视觉集成录制会话: {session_name}"
        )
        
        # 开始Kilo Code场景录制（如果指定）
        kilo_recording_id = None
        if kilo_scenario_id:
            try:
                kilo_recording_id = self.kilo_code_recorder.start_scenario_recording(kilo_scenario_id)
            except Exception as e:
                print(f"⚠️ Kilo Code场景录制启动失败: {e}")
        
        # 设置会话元数据
        self.session_metadata = {
            "session_id": self.current_session_id,
            "session_name": session_name,
            "start_time": datetime.now().isoformat(),
            "workflow_recording_id": workflow_recording_id,
            "kilo_recording_id": kilo_recording_id,
            "kilo_scenario_id": kilo_scenario_id,
            "recording_config": asdict(recording_config),
            "visual_config": asdict(self.current_config)
        }
        
        # 重置事件列表
        self.visual_events = []
        
        print(f"🎬 开始视觉录制会话: {session_name}")
        print(f"   会话ID: {self.current_session_id}")
        print(f"   工作流录制ID: {workflow_recording_id}")
        if kilo_recording_id:
            print(f"   Kilo Code录制ID: {kilo_recording_id}")
        print(f"   视觉验证: {'启用' if self.current_config.enable_visual_verification else '禁用'}")
        
        return self.current_session_id
    
    def record_kilo_code_with_visual(self, struggle_mode: StruggleModeType,
                                   detection_data: Dict[str, Any],
                                   confidence_score: float,
                                   response_time: float,
                                   capture_screenshot: bool = None) -> str:
        """录制Kilo Code事件并进行视觉验证"""
        
        if not self.current_session_id:
            raise RuntimeError("没有活跃的视觉录制会话")
        
        # 录制Kilo Code事件
        kilo_event_id = self.kilo_code_recorder.record_struggle_mode_detection(
            struggle_mode=struggle_mode,
            detection_data=detection_data,
            confidence_score=confidence_score,
            response_time=response_time
        )
        
        # 决定是否截图
        should_capture = (capture_screenshot if capture_screenshot is not None 
                         else self.current_config.capture_on_kilo_events)
        
        visual_event = None
        if should_capture and self.visual_tester:
            visual_event = self._capture_and_verify_visual(
                event_type="kilo_code",
                event_context={
                    "kilo_event_id": kilo_event_id,
                    "struggle_mode": struggle_mode.value,
                    "confidence_score": confidence_score,
                    "response_time": response_time
                }
            )
        
        print(f"📝 Kilo Code事件已录制: {struggle_mode.name} (视觉验证: {'✅' if visual_event else '❌'})")
        
        return kilo_event_id
    
    def record_intervention_with_visual(self, intervention_type: InterventionType,
                                      intervention_data: Dict[str, Any],
                                      success_rate: float,
                                      response_time: float,
                                      capture_screenshot: bool = None) -> str:
        """录制智能介入事件并进行视觉验证"""
        
        if not self.current_session_id:
            raise RuntimeError("没有活跃的视觉录制会话")
        
        # 录制介入事件
        intervention_event_id = self.kilo_code_recorder.record_intervention_trigger(
            intervention_type=intervention_type,
            intervention_data=intervention_data,
            success_rate=success_rate,
            response_time=response_time
        )
        
        # 决定是否截图
        should_capture = (capture_screenshot if capture_screenshot is not None 
                         else self.current_config.capture_on_kilo_events)
        
        visual_event = None
        if should_capture and self.visual_tester:
            visual_event = self._capture_and_verify_visual(
                event_type="intervention",
                event_context={
                    "intervention_event_id": intervention_event_id,
                    "intervention_type": intervention_type.value,
                    "success_rate": success_rate,
                    "response_time": response_time
                }
            )
        
        print(f"🤖 智能介入已录制: {intervention_type.name} (视觉验证: {'✅' if visual_event else '❌'})")
        
        return intervention_event_id
    
    def record_ui_interaction_with_visual(self, interaction_type: str,
                                        element_info: Dict[str, Any],
                                        interaction_data: Dict[str, Any] = None,
                                        capture_before: bool = True,
                                        capture_after: bool = True) -> str:
        """录制UI交互并进行视觉验证"""
        
        if not self.current_session_id:
            raise RuntimeError("没有活跃的视觉录制会话")
        
        # 交互前截图
        before_visual_event = None
        if capture_before and self.visual_tester and self.current_config.capture_on_ui_interactions:
            before_visual_event = self._capture_and_verify_visual(
                event_type="ui_before",
                event_context={
                    "interaction_type": interaction_type,
                    "element_info": element_info,
                    "stage": "before"
                }
            )
        
        # 录制UI交互
        ui_action_id = self.workflow_recorder.record_ui_interaction(
            interaction_type=interaction_type,
            element_info=element_info,
            interaction_data=interaction_data
        )
        
        # 交互后截图
        after_visual_event = None
        if capture_after and self.visual_tester and self.current_config.capture_on_ui_interactions:
            # 等待UI更新
            import time
            time.sleep(0.5)
            
            after_visual_event = self._capture_and_verify_visual(
                event_type="ui_after",
                event_context={
                    "interaction_type": interaction_type,
                    "element_info": element_info,
                    "ui_action_id": ui_action_id,
                    "stage": "after"
                }
            )
        
        print(f"🖱️ UI交互已录制: {interaction_type} (前: {'✅' if before_visual_event else '❌'}, 后: {'✅' if after_visual_event else '❌'})")
        
        return ui_action_id
    
    def _capture_and_verify_visual(self, event_type: str, event_context: Dict[str, Any]) -> Optional[VisualRecordingEvent]:
        """捕获并验证视觉效果"""
        
        if not self.visual_tester:
            return None
        
        try:
            # 生成事件ID
            event_id = f"visual_{len(self.visual_events) + 1:03d}_{event_type}"
            
            # 截图
            screenshot_name = f"{self.current_session_id}_{event_id}"
            screenshot_path = self.visual_tester.take_screenshot(
                test_name=screenshot_name,
                test_id=event_id
            )
            
            if not screenshot_path:
                print(f"⚠️ 截图失败: {event_id}")
                return None
            
            # 视觉对比（如果启用）
            comparison_result = None
            baseline_path = None
            
            if self.current_config.enable_screenshot_comparison:
                # 查找基线图片
                baseline_name = f"{event_type}_baseline"
                baseline_path = self.baselines_dir / f"{baseline_name}.png"
                
                if baseline_path.exists():
                    # 执行对比
                    comparison_result = self.visual_tester.compare_visual(
                        test_name=f"{screenshot_name}_comparison",
                        test_id=f"{event_id}_compare",
                        current_screenshot_path=Path(screenshot_path),
                        baseline_screenshot_path=baseline_path,
                        update_baseline=self.current_config.auto_update_baseline
                    )
                    
                    # 检查回归
                    if (comparison_result and 
                        comparison_result.similarity_score < (1.0 - self.current_config.visual_threshold)):
                        print(f"⚠️ 检测到视觉回归: {event_id} (相似度: {comparison_result.similarity_score:.3f})")
                        self.integration_stats["visual_regression_detected"] += 1
                
                else:
                    # 创建基线
                    if self.current_config.auto_update_baseline:
                        import shutil
                        shutil.copy2(screenshot_path, baseline_path)
                        print(f"📸 创建基线图片: {baseline_name}")
            
            # 创建视觉事件
            visual_event = VisualRecordingEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now().isoformat(),
                screenshot_path=str(screenshot_path),
                baseline_path=str(baseline_path) if baseline_path and baseline_path.exists() else None,
                comparison_result=comparison_result,
                visual_metadata={
                    "session_id": self.current_session_id,
                    "event_context": event_context,
                    "screenshot_size": self._get_image_size(screenshot_path),
                    "capture_settings": {
                        "threshold": self.current_config.visual_threshold,
                        "auto_update_baseline": self.current_config.auto_update_baseline
                    }
                }
            )
            
            # 添加到事件列表
            self.visual_events.append(visual_event)
            self.integration_stats["total_visual_events"] += 1
            
            return visual_event
            
        except Exception as e:
            print(f"⚠️ 视觉验证失败: {e}")
            return None
    
    def _get_image_size(self, image_path: str) -> Dict[str, int]:
        """获取图片尺寸"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                return {"width": img.width, "height": img.height}
        except:
            return {"width": 0, "height": 0}
    
    def stop_visual_recording_session(self) -> Dict[str, Any]:
        """停止视觉录制会话并生成报告"""
        
        if not self.current_session_id:
            raise RuntimeError("没有活跃的视觉录制会话")
        
        # 停止工作流录制
        workflow_result = self.workflow_recorder.stop_recording()
        
        # 停止Kilo Code录制（如果有）
        kilo_result = None
        if self.session_metadata.get("kilo_recording_id"):
            try:
                kilo_result = self.kilo_code_recorder.stop_scenario_recording()
            except Exception as e:
                print(f"⚠️ 停止Kilo Code录制失败: {e}")
        
        # 关闭视觉测试器
        if self.visual_tester:
            try:
                self.visual_tester.stop_browser()
            except Exception as e:
                print(f"⚠️ 关闭视觉测试浏览器失败: {e}")
        
        # 生成集成报告
        integration_report = self._generate_integration_report(workflow_result, kilo_result)
        
        # 生成n8n工作流
        n8n_workflow_path = None
        if workflow_result:
            try:
                n8n_workflow = self.n8n_converter.convert_recording_to_n8n(
                    workflow_result, "kilo_code_detection"
                )
                n8n_workflow_path = self.n8n_converter.save_workflow(n8n_workflow)
                integration_report["n8n_workflow_path"] = n8n_workflow_path
            except Exception as e:
                print(f"⚠️ 生成n8n工作流失败: {e}")
        
        # 保存集成报告
        self._save_integration_report(integration_report)
        
        # 更新统计
        self._update_integration_stats(integration_report)
        
        print(f"🎬 视觉录制会话完成: {self.session_metadata['session_name']}")
        print(f"   会话ID: {self.current_session_id}")
        print(f"   视觉事件: {len(self.visual_events)}")
        print(f"   视觉回归: {integration_report.get('visual_analysis', {}).get('regressions_detected', 0)}")
        if n8n_workflow_path:
            print(f"   n8n工作流: {n8n_workflow_path}")
        
        # 重置状态
        session_id = self.current_session_id
        self.current_session_id = None
        self.current_config = None
        self.visual_events = []
        self.session_metadata = {}
        self.visual_tester = None
        
        return integration_report
    
    def _generate_integration_report(self, workflow_result: Dict[str, Any], 
                                   kilo_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成集成报告"""
        
        # 视觉分析
        visual_analysis = {
            "total_visual_events": len(self.visual_events),
            "events_by_type": {},
            "regressions_detected": 0,
            "screenshots_captured": 0,
            "comparisons_performed": 0,
            "baselines_created": 0
        }
        
        for event in self.visual_events:
            # 按类型统计
            event_type = event.event_type
            if event_type not in visual_analysis["events_by_type"]:
                visual_analysis["events_by_type"][event_type] = 0
            visual_analysis["events_by_type"][event_type] += 1
            
            # 统计截图
            if event.screenshot_path:
                visual_analysis["screenshots_captured"] += 1
            
            # 统计对比
            if event.comparison_result:
                visual_analysis["comparisons_performed"] += 1
                
                # 检查回归
                if (event.comparison_result.similarity_score < 
                    (1.0 - self.current_config.visual_threshold)):
                    visual_analysis["regressions_detected"] += 1
            
            # 统计基线
            if event.baseline_path:
                visual_analysis["baselines_created"] += 1
        
        # 性能分析
        performance_analysis = {
            "session_duration": 0.0,
            "average_visual_processing_time": 0.0,
            "workflow_performance": workflow_result.get("statistics", {}) if workflow_result else {},
            "kilo_code_performance": kilo_result.get("performance_analysis", {}) if kilo_result else {}
        }
        
        # 计算会话持续时间
        if self.session_metadata.get("start_time"):
            try:
                start_time = datetime.fromisoformat(self.session_metadata["start_time"])
                end_time = datetime.now()
                performance_analysis["session_duration"] = (end_time - start_time).total_seconds()
            except:
                pass
        
        # 质量评估
        quality_assessment = {
            "visual_quality_score": self._calculate_visual_quality_score(visual_analysis),
            "integration_completeness": self._calculate_integration_completeness(workflow_result, kilo_result),
            "overall_success_rate": 0.0,
            "recommendations": self._generate_integration_recommendations(visual_analysis, performance_analysis)
        }
        
        # 计算总体成功率
        success_factors = []
        if workflow_result:
            success_factors.append(1.0)
        if kilo_result:
            success_factors.append(1.0)
        if visual_analysis["screenshots_captured"] > 0:
            success_factors.append(1.0)
        if visual_analysis["regressions_detected"] == 0:
            success_factors.append(1.0)
        
        quality_assessment["overall_success_rate"] = sum(success_factors) / max(len(success_factors), 1)
        
        # 生成完整报告
        report = {
            "session_metadata": self.session_metadata,
            "visual_analysis": visual_analysis,
            "performance_analysis": performance_analysis,
            "quality_assessment": quality_assessment,
            "visual_events": [asdict(event) for event in self.visual_events],
            "workflow_result": workflow_result,
            "kilo_code_result": kilo_result,
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _calculate_visual_quality_score(self, visual_analysis: Dict[str, Any]) -> float:
        """计算视觉质量评分"""
        score = 0.0
        
        # 基础分数：有视觉事件
        if visual_analysis["total_visual_events"] > 0:
            score += 0.3
        
        # 截图覆盖率
        if visual_analysis["screenshots_captured"] > 0:
            score += 0.3
        
        # 对比执行率
        if visual_analysis["comparisons_performed"] > 0:
            score += 0.2
        
        # 回归检测（无回归加分）
        if visual_analysis["regressions_detected"] == 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_integration_completeness(self, workflow_result: Dict[str, Any], 
                                          kilo_result: Dict[str, Any]) -> float:
        """计算集成完整性"""
        completeness = 0.0
        
        # 工作流录制完整性
        if workflow_result and workflow_result.get("statistics", {}).get("total_actions", 0) > 0:
            completeness += 0.4
        
        # Kilo Code录制完整性
        if kilo_result and kilo_result.get("statistics", {}).get("total_kilo_code_events", 0) > 0:
            completeness += 0.4
        
        # 视觉验证完整性
        if len(self.visual_events) > 0:
            completeness += 0.2
        
        return completeness
    
    def _generate_integration_recommendations(self, visual_analysis: Dict[str, Any], 
                                            performance_analysis: Dict[str, Any]) -> List[str]:
        """生成集成建议"""
        recommendations = []
        
        # 视觉相关建议
        if visual_analysis["total_visual_events"] == 0:
            recommendations.append("建议启用视觉验证功能以提高测试覆盖率")
        
        if visual_analysis["regressions_detected"] > 0:
            recommendations.append(f"检测到 {visual_analysis['regressions_detected']} 个视觉回归，建议检查UI变更")
        
        if visual_analysis["comparisons_performed"] == 0:
            recommendations.append("建议启用截图对比功能以检测视觉回归")
        
        # 性能相关建议
        if performance_analysis["session_duration"] > 300:  # 5分钟
            recommendations.append("录制会话时间较长，建议优化测试流程")
        
        # Kilo Code相关建议
        kilo_perf = performance_analysis.get("kilo_code_performance", {})
        if kilo_perf.get("average_response_time", 0) > 3.0:
            recommendations.append("Kilo Code响应时间超标，建议优化检测算法")
        
        if not recommendations:
            recommendations.append("集成测试表现良好，建议继续保持当前配置")
        
        return recommendations
    
    def _save_integration_report(self, report: Dict[str, Any]):
        """保存集成报告"""
        
        # 保存详细报告
        report_filename = f"{self.current_session_id}_integration_report.json"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # 保存简化摘要
        summary = {
            "session_id": self.current_session_id,
            "session_name": self.session_metadata.get("session_name"),
            "timestamp": datetime.now().isoformat(),
            "visual_events_count": len(self.visual_events),
            "regressions_detected": report["visual_analysis"]["regressions_detected"],
            "quality_score": report["quality_assessment"]["visual_quality_score"],
            "overall_success_rate": report["quality_assessment"]["overall_success_rate"],
            "session_duration": report["performance_analysis"]["session_duration"]
        }
        
        summary_filename = f"{self.current_session_id}_summary.json"
        summary_path = self.reports_dir / summary_filename
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 集成报告已保存:")
        print(f"   详细报告: {report_path}")
        print(f"   摘要: {summary_path}")
    
    def _update_integration_stats(self, report: Dict[str, Any]):
        """更新集成统计"""
        self.integration_stats["total_sessions"] += 1
        
        if report["quality_assessment"]["overall_success_rate"] > 0.8:
            self.integration_stats["successful_sessions"] += 1
        
        self.integration_stats["total_visual_events"] += len(self.visual_events)
        self.integration_stats["visual_regression_detected"] += report["visual_analysis"]["regressions_detected"]
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """获取集成统计"""
        return self.integration_stats.copy()

if __name__ == "__main__":
    # 示例使用
    integrator = VisualWorkflowIntegrator()
    
    # 配置
    recording_config = WorkflowRecordingConfig(
        recording_mode="kilo_code_detection",
        target_version="enterprise",
        enable_visual_verification=True,
        enable_screenshot=True
    )
    
    visual_config = VisualRecordingConfig(
        enable_visual_verification=True,
        enable_screenshot_comparison=True,
        enable_regression_testing=True,
        capture_on_kilo_events=True,
        capture_on_ui_interactions=True,
        auto_update_baseline=True
    )
    
    # 开始集成录制会话
    session_id = integrator.start_visual_recording_session(
        session_name="Kilo Code企业版视觉集成测试",
        recording_config=recording_config,
        visual_config=visual_config,
        kilo_scenario_id="enterprise_critical_modes"
    )
    
    # 模拟录制过程
    try:
        # 录制Kilo Code事件
        integrator.record_kilo_code_with_visual(
            struggle_mode=StruggleModeType.SYNTAX_ERROR,
            detection_data={"error_type": "missing_semicolon", "line": 42},
            confidence_score=0.95,
            response_time=1.2
        )
        
        # 录制UI交互
        integrator.record_ui_interaction_with_visual(
            interaction_type="click",
            element_info={"selector": ".kilo-code-panel", "text": "智能介入面板"},
            interaction_data={"action": "open_panel"}
        )
        
        # 录制智能介入
        integrator.record_intervention_with_visual(
            intervention_type=InterventionType.CODE_SUGGESTION,
            intervention_data={"suggestion": "添加分号", "confidence": 0.95},
            success_rate=0.90,
            response_time=0.8
        )
        
    except Exception as e:
        print(f"⚠️ 录制过程中出现错误: {e}")
    
    # 停止会话
    integration_report = integrator.stop_visual_recording_session()
    
    # 显示结果
    print(f"\n📊 视觉集成测试报告:")
    print(f"   质量评分: {integration_report['quality_assessment']['visual_quality_score']:.2f}")
    print(f"   成功率: {integration_report['quality_assessment']['overall_success_rate']:.2f}")
    print(f"   视觉事件: {integration_report['visual_analysis']['total_visual_events']}")
    print(f"   视觉回归: {integration_report['visual_analysis']['regressions_detected']}")
    
    # 显示统计
    stats = integrator.get_integration_stats()
    print(f"\n📈 集成统计:")
    print(f"   总会话数: {stats['total_sessions']}")
    print(f"   成功会话: {stats['successful_sessions']}")
    print(f"   总视觉事件: {stats['total_visual_events']}")
    
    print(f"\n🎉 视觉工作流集成演示完成！")

