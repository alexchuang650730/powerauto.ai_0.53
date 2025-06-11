#!/usr/bin/env python3
"""
PowerAutomation 一键录制工作流集成器

将一键录制功能集成到自动化测试框架中，作为视觉截图验证的平行功能
专门用于录制Kilo Code智能介入检测结果，生成n8n格式工作流
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# 导入现有的测试框架组件
sys.path.append(str(Path(__file__).parent))
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig
from test_flow_recorder import TestFlowRecorder, TestAction, TestFlow

@dataclass
class WorkflowRecordingConfig:
    """工作流录制配置"""
    recording_mode: str = "kilo_code_detection"  # kilo_code_detection, general_test, ui_validation
    target_version: str = "enterprise"  # enterprise, personal_pro
    enable_visual_verification: bool = True
    enable_screenshot: bool = True
    auto_generate_n8n: bool = True
    recording_quality: str = "high"  # low, medium, high
    max_recording_duration: int = 300  # 最大录制时长（秒）
    screenshot_interval: float = 2.0  # 截图间隔（秒）

@dataclass
class KiloCodeDetectionEvent:
    """Kilo Code检测事件"""
    event_id: str
    timestamp: str
    detection_type: str  # struggle_mode_1-7, intervention_decision, accuracy_check
    detection_data: Dict[str, Any]
    confidence_score: float
    response_time: float
    screenshot_path: Optional[str] = None
    visual_verification: Optional[Dict[str, Any]] = None

class WorkflowRecorder:
    """工作流录制器 - 集成到测试框架"""
    
    def __init__(self, test_framework_dir: str = None):
        # 设置测试框架目录
        if test_framework_dir:
            self.framework_dir = Path(test_framework_dir)
        else:
            self.framework_dir = Path(__file__).parent
        
        # 创建录制专用目录
        self.recording_dir = self.framework_dir / "workflow_recordings"
        self.recording_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录结构
        self.flows_dir = self.recording_dir / "flows"
        self.screenshots_dir = self.recording_dir / "screenshots"
        self.n8n_workflows_dir = self.recording_dir / "n8n_workflows"
        self.visual_data_dir = self.recording_dir / "visual_data"
        self.kilo_code_data_dir = self.recording_dir / "kilo_code_data"
        
        for directory in [self.flows_dir, self.screenshots_dir, self.n8n_workflows_dir, 
                         self.visual_data_dir, self.kilo_code_data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 录制状态
        self.is_recording = False
        self.current_recording_id: Optional[str] = None
        self.current_config: Optional[WorkflowRecordingConfig] = None
        self.current_flow: Optional[TestFlow] = None
        self.kilo_code_events: List[KiloCodeDetectionEvent] = []
        
        # 集成组件
        self.flow_recorder: Optional[TestFlowRecorder] = None
        self.visual_tester: Optional[PowerAutomationVisualTester] = None
        
        # 统计数据
        self.recording_stats = {
            "total_recordings": 0,
            "successful_recordings": 0,
            "failed_recordings": 0,
            "total_kilo_code_events": 0,
            "average_response_time": 0.0
        }
    
    def start_recording(self, recording_name: str, config: WorkflowRecordingConfig = None,
                       description: str = "") -> str:
        """开始一键录制"""
        if self.is_recording:
            raise RuntimeError("已有录制进行中，请先停止当前录制")
        
        # 设置配置
        self.current_config = config or WorkflowRecordingConfig()
        
        # 生成录制ID
        self.current_recording_id = f"recording_{uuid.uuid4().hex[:8]}"
        
        # 初始化流程录制器
        self.flow_recorder = TestFlowRecorder(str(self.recording_dir))
        
        # 启动流程录制
        flow_id = self.flow_recorder.start_recording(
            flow_name=f"{recording_name}_{self.current_config.recording_mode}",
            description=f"{description} | 模式: {self.current_config.recording_mode} | 版本: {self.current_config.target_version}",
            metadata={
                "recording_id": self.current_recording_id,
                "recording_mode": self.current_config.recording_mode,
                "target_version": self.current_config.target_version,
                "config": asdict(self.current_config)
            }
        )
        
        # 初始化视觉测试器（如果启用）
        if self.current_config.enable_visual_verification:
            try:
                visual_config = VisualTestConfig(
                    browser_type="chromium",
                    headless=False,
                    viewport_width=1920,
                    viewport_height=1080,
                    visual_threshold=0.05,
                    auto_update_baseline=True
                )
                
                self.visual_tester = PowerAutomationVisualTester(
                    test_dir=str(self.visual_data_dir),
                    config=visual_config
                )
                
                if self.visual_tester.start_browser():
                    print(f"✅ 视觉验证浏览器已启动")
                else:
                    print(f"⚠️ 视觉验证浏览器启动失败")
                    self.visual_tester = None
                    
            except Exception as e:
                print(f"⚠️ 视觉测试器初始化失败: {e}")
                self.visual_tester = None
        
        self.is_recording = True
        self.kilo_code_events = []
        
        print(f"🎬 开始一键录制: {recording_name}")
        print(f"   录制ID: {self.current_recording_id}")
        print(f"   录制模式: {self.current_config.recording_mode}")
        print(f"   目标版本: {self.current_config.target_version}")
        print(f"   视觉验证: {'启用' if self.current_config.enable_visual_verification else '禁用'}")
        
        return self.current_recording_id
    
    def stop_recording(self) -> Optional[Dict[str, Any]]:
        """停止录制并生成结果"""
        if not self.is_recording:
            print("⚠️ 没有进行中的录制")
            return None
        
        # 停止流程录制
        completed_flow = None
        if self.flow_recorder:
            completed_flow = self.flow_recorder.stop_recording()
        
        # 关闭视觉测试器
        if self.visual_tester:
            try:
                self.visual_tester.stop_browser()
            except Exception as e:
                print(f"⚠️ 关闭视觉测试浏览器失败: {e}")
        
        # 生成录制结果
        recording_result = self._generate_recording_result(completed_flow)
        
        # 生成n8n工作流（如果启用）
        if self.current_config.auto_generate_n8n:
            n8n_workflow = self._generate_n8n_workflow(recording_result)
            recording_result["n8n_workflow"] = n8n_workflow
        
        # 保存录制数据
        self._save_recording_result(recording_result)
        
        # 更新统计
        self._update_recording_stats(recording_result)
        
        print(f"🎬 录制完成: {self.current_recording_id}")
        print(f"   动作数量: {len(recording_result.get('actions', []))}")
        print(f"   Kilo Code事件: {len(self.kilo_code_events)}")
        print(f"   截图数量: {len(recording_result.get('screenshots', []))}")
        
        # 重置状态
        self.is_recording = False
        self.current_recording_id = None
        self.current_config = None
        self.current_flow = None
        self.flow_recorder = None
        self.visual_tester = None
        
        return recording_result
    
    def record_kilo_code_detection(self, detection_type: str, detection_data: Dict[str, Any],
                                  confidence_score: float, response_time: float) -> str:
        """录制Kilo Code检测事件"""
        if not self.is_recording:
            print("⚠️ 没有进行中的录制")
            return ""
        
        event_id = f"kilo_event_{len(self.kilo_code_events) + 1:03d}"
        
        # 创建检测事件
        event = KiloCodeDetectionEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            detection_type=detection_type,
            detection_data=detection_data,
            confidence_score=confidence_score,
            response_time=response_time
        )
        
        # 截图（如果启用）
        if self.current_config.enable_screenshot and self.visual_tester:
            try:
                screenshot_name = f"{self.current_recording_id}_{event_id}"
                screenshot_path = self.visual_tester.take_screenshot(
                    test_name=screenshot_name,
                    test_id=event_id
                )
                if screenshot_path:
                    event.screenshot_path = str(screenshot_path)
            except Exception as e:
                print(f"⚠️ Kilo Code事件截图失败: {e}")
        
        # 视觉验证（如果启用）
        if (self.current_config.enable_visual_verification and 
            self.visual_tester and event.screenshot_path):
            try:
                visual_result = self.visual_tester.compare_visual(
                    test_name=f"{self.current_recording_id}_{event_id}_verification",
                    test_id=f"{event_id}_visual",
                    current_screenshot_path=Path(event.screenshot_path),
                    update_baseline=True
                )
                event.visual_verification = asdict(visual_result)
            except Exception as e:
                print(f"⚠️ Kilo Code事件视觉验证失败: {e}")
        
        # 添加到事件列表
        self.kilo_code_events.append(event)
        
        # 同时录制为测试动作
        if self.flow_recorder:
            self.flow_recorder.record_custom_action(
                action_name="kilo_code_detection",
                action_data={
                    "detection_type": detection_type,
                    "detection_data": detection_data,
                    "confidence_score": confidence_score,
                    "response_time": response_time,
                    "event_id": event_id
                }
            )
        
        print(f"📝 录制Kilo Code事件: {detection_type} (置信度: {confidence_score:.2f}, 响应时间: {response_time:.2f}s)")
        
        return event_id
    
    def record_user_action(self, action_type: str, action_data: Dict[str, Any] = None) -> str:
        """录制用户操作动作"""
        if not self.is_recording or not self.flow_recorder:
            print("⚠️ 没有进行中的录制")
            return ""
        
        action = self.flow_recorder.record_custom_action(
            action_name=f"user_{action_type}",
            action_data=action_data or {}
        )
        
        return action.id if action else ""
    
    def record_ui_interaction(self, interaction_type: str, element_info: Dict[str, Any],
                             interaction_data: Dict[str, Any] = None) -> str:
        """录制UI交互"""
        if not self.is_recording or not self.flow_recorder:
            print("⚠️ 没有进行中的录制")
            return ""
        
        if interaction_type == "click":
            action = self.flow_recorder.record_click(
                element_selector=element_info.get("selector", ""),
                element_text=element_info.get("text", ""),
                coordinates=element_info.get("coordinates")
            )
        elif interaction_type == "input":
            action = self.flow_recorder.record_input(
                element_selector=element_info.get("selector", ""),
                input_text=interaction_data.get("text", ""),
                clear_first=interaction_data.get("clear_first", True)
            )
        elif interaction_type == "navigate":
            action = self.flow_recorder.record_navigation(
                url=interaction_data.get("url", ""),
                wait_time=interaction_data.get("wait_time", 2.0)
            )
        else:
            action = self.flow_recorder.record_custom_action(
                action_name=f"ui_{interaction_type}",
                action_data=interaction_data or {},
                element_info=element_info
            )
        
        return action.id if action else ""
    
    def _generate_recording_result(self, completed_flow: Optional[TestFlow]) -> Dict[str, Any]:
        """生成录制结果"""
        result = {
            "recording_id": self.current_recording_id,
            "recording_name": completed_flow.name if completed_flow else "Unknown",
            "recording_mode": self.current_config.recording_mode,
            "target_version": self.current_config.target_version,
            "start_time": completed_flow.start_time if completed_flow else datetime.now().isoformat(),
            "end_time": completed_flow.end_time if completed_flow else datetime.now().isoformat(),
            "config": asdict(self.current_config),
            "actions": [asdict(action) for action in completed_flow.actions] if completed_flow else [],
            "kilo_code_events": [asdict(event) for event in self.kilo_code_events],
            "screenshots": completed_flow.screenshots if completed_flow else [],
            "visual_verifications": completed_flow.visual_verifications if completed_flow else [],
            "statistics": {
                "total_actions": len(completed_flow.actions) if completed_flow else 0,
                "total_kilo_code_events": len(self.kilo_code_events),
                "total_screenshots": len(completed_flow.screenshots) if completed_flow else 0,
                "average_kilo_code_response_time": self._calculate_average_response_time(),
                "recording_duration": self._calculate_recording_duration(completed_flow)
            }
        }
        
        return result
    
    def _generate_n8n_workflow(self, recording_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成n8n工作流"""
        workflow = {
            "name": f"PowerAutomation_{recording_result['recording_mode']}_{recording_result['recording_id']}",
            "nodes": [],
            "connections": {},
            "active": True,
            "settings": {},
            "staticData": {},
            "meta": {
                "powerautomation_recording_id": recording_result["recording_id"],
                "recording_mode": recording_result["recording_mode"],
                "target_version": recording_result["target_version"],
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # 添加开始节点
        start_node = {
            "parameters": {},
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [240, 300]
        }
        workflow["nodes"].append(start_node)
        
        # 为每个Kilo Code事件创建节点
        node_counter = 1
        previous_node = "Start"
        
        for event in recording_result["kilo_code_events"]:
            node_name = f"KiloCode_{event['detection_type']}_{node_counter}"
            
            kilo_node = {
                "parameters": {
                    "detection_type": event["detection_type"],
                    "detection_data": event["detection_data"],
                    "confidence_score": event["confidence_score"],
                    "response_time": event["response_time"],
                    "expected_response_time": 3.0,  # <3秒要求
                    "expected_confidence": 0.85  # >85%准确率要求
                },
                "name": node_name,
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [240 + node_counter * 200, 300]
            }
            
            workflow["nodes"].append(kilo_node)
            
            # 添加连接
            if previous_node not in workflow["connections"]:
                workflow["connections"][previous_node] = {"main": [[]]}
            
            workflow["connections"][previous_node]["main"][0].append({
                "node": node_name,
                "type": "main",
                "index": 0
            })
            
            previous_node = node_name
            node_counter += 1
        
        # 添加验证节点
        if recording_result["kilo_code_events"]:
            validation_node = {
                "parameters": {
                    "total_events": len(recording_result["kilo_code_events"]),
                    "average_response_time": recording_result["statistics"]["average_kilo_code_response_time"],
                    "validation_criteria": {
                        "max_response_time": 3.0,
                        "min_confidence": 0.85,
                        "required_detection_types": ["struggle_mode_1", "struggle_mode_2", "intervention_decision"]
                    }
                },
                "name": "Validation",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [240 + node_counter * 200, 300]
            }
            
            workflow["nodes"].append(validation_node)
            
            # 连接到验证节点
            if previous_node not in workflow["connections"]:
                workflow["connections"][previous_node] = {"main": [[]]}
            
            workflow["connections"][previous_node]["main"][0].append({
                "node": "Validation",
                "type": "main",
                "index": 0
            })
        
        return workflow
    
    def _save_recording_result(self, recording_result: Dict[str, Any]):
        """保存录制结果"""
        # 保存主要录制数据
        result_path = self.flows_dir / f"{recording_result['recording_id']}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(recording_result, f, indent=2, ensure_ascii=False)
        
        # 保存n8n工作流（如果存在）
        if "n8n_workflow" in recording_result:
            n8n_path = self.n8n_workflows_dir / f"{recording_result['recording_id']}_workflow.json"
            with open(n8n_path, 'w', encoding='utf-8') as f:
                json.dump(recording_result["n8n_workflow"], f, indent=2, ensure_ascii=False)
        
        # 保存Kilo Code事件数据
        kilo_data_path = self.kilo_code_data_dir / f"{recording_result['recording_id']}_kilo_events.json"
        with open(kilo_data_path, 'w', encoding='utf-8') as f:
            json.dump(recording_result["kilo_code_events"], f, indent=2, ensure_ascii=False)
        
        print(f"💾 录制结果已保存:")
        print(f"   主数据: {result_path}")
        if "n8n_workflow" in recording_result:
            print(f"   n8n工作流: {n8n_path}")
        print(f"   Kilo Code数据: {kilo_data_path}")
    
    def _calculate_average_response_time(self) -> float:
        """计算平均响应时间"""
        if not self.kilo_code_events:
            return 0.0
        
        total_time = sum(event.response_time for event in self.kilo_code_events)
        return total_time / len(self.kilo_code_events)
    
    def _calculate_recording_duration(self, completed_flow: Optional[TestFlow]) -> float:
        """计算录制持续时间"""
        if not completed_flow or not completed_flow.start_time or not completed_flow.end_time:
            return 0.0
        
        try:
            start = datetime.fromisoformat(completed_flow.start_time)
            end = datetime.fromisoformat(completed_flow.end_time)
            return (end - start).total_seconds()
        except:
            return 0.0
    
    def _update_recording_stats(self, recording_result: Dict[str, Any]):
        """更新录制统计"""
        self.recording_stats["total_recordings"] += 1
        
        # 判断录制是否成功
        if (recording_result["statistics"]["total_kilo_code_events"] > 0 and
            recording_result["statistics"]["average_kilo_code_response_time"] < 3.0):
            self.recording_stats["successful_recordings"] += 1
        else:
            self.recording_stats["failed_recordings"] += 1
        
        self.recording_stats["total_kilo_code_events"] += recording_result["statistics"]["total_kilo_code_events"]
        
        # 更新平均响应时间
        if self.recording_stats["total_kilo_code_events"] > 0:
            self.recording_stats["average_response_time"] = (
                recording_result["statistics"]["average_kilo_code_response_time"]
            )
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """获取录制统计"""
        return self.recording_stats.copy()
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """列出所有录制"""
        recordings = []
        
        for json_file in self.flows_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    recording_data = json.load(f)
                
                recordings.append({
                    "recording_id": recording_data.get("recording_id"),
                    "recording_name": recording_data.get("recording_name"),
                    "recording_mode": recording_data.get("recording_mode"),
                    "target_version": recording_data.get("target_version"),
                    "start_time": recording_data.get("start_time"),
                    "end_time": recording_data.get("end_time"),
                    "total_actions": recording_data.get("statistics", {}).get("total_actions", 0),
                    "total_kilo_code_events": recording_data.get("statistics", {}).get("total_kilo_code_events", 0),
                    "average_response_time": recording_data.get("statistics", {}).get("average_kilo_code_response_time", 0),
                    "file_path": str(json_file)
                })
                
            except Exception as e:
                print(f"⚠️ 读取录制文件失败 {json_file}: {e}")
        
        return sorted(recordings, key=lambda x: x.get("start_time", ""), reverse=True)
    
    @contextmanager
    def recording_session(self, recording_name: str, config: WorkflowRecordingConfig = None,
                         description: str = ""):
        """录制会话上下文管理器"""
        recording_id = self.start_recording(recording_name, config, description)
        try:
            yield recording_id
        finally:
            self.stop_recording()

# 便捷的录制装饰器
def record_kilo_code_test(recording_name: str, target_version: str = "enterprise",
                         enable_visual: bool = True):
    """Kilo Code测试录制装饰器"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            config = WorkflowRecordingConfig(
                recording_mode="kilo_code_detection",
                target_version=target_version,
                enable_visual_verification=enable_visual,
                enable_screenshot=True,
                auto_generate_n8n=True
            )
            
            recorder = WorkflowRecorder()
            
            with recorder.recording_session(recording_name, config):
                # 将录制器传递给测试函数
                if 'recorder' in test_func.__code__.co_varnames:
                    kwargs['recorder'] = recorder
                
                result = test_func(*args, **kwargs)
                return result
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # 示例使用
    recorder = WorkflowRecorder()
    
    # 配置录制
    config = WorkflowRecordingConfig(
        recording_mode="kilo_code_detection",
        target_version="enterprise",
        enable_visual_verification=True,
        enable_screenshot=True,
        auto_generate_n8n=True
    )
    
    # 示例录制会话
    with recorder.recording_session("Kilo Code智能介入测试", config, "测试7种挣扎模式检测"):
        # 模拟Kilo Code检测事件
        recorder.record_kilo_code_detection(
            detection_type="struggle_mode_1",
            detection_data={"code_complexity": "high", "error_rate": 0.15},
            confidence_score=0.92,
            response_time=1.8
        )
        
        recorder.record_kilo_code_detection(
            detection_type="intervention_decision",
            detection_data={"intervention_type": "code_suggestion", "priority": "high"},
            confidence_score=0.88,
            response_time=2.1
        )
        
        recorder.record_kilo_code_detection(
            detection_type="accuracy_check",
            detection_data={"accuracy_rate": 0.87, "test_coverage": 0.92},
            confidence_score=0.95,
            response_time=1.2
        )
        
        # 模拟用户交互
        recorder.record_ui_interaction(
            interaction_type="click",
            element_info={"selector": ".kilo-code-panel", "text": "智能介入面板"},
            interaction_data={"action": "open_panel"}
        )
        
        recorder.record_ui_interaction(
            interaction_type="input",
            element_info={"selector": "#code-input"},
            interaction_data={"text": "function testKiloCode() { return true; }"}
        )
    
    # 显示录制统计
    stats = recorder.get_recording_stats()
    print(f"\n📊 录制统计:")
    print(f"   总录制数: {stats['total_recordings']}")
    print(f"   成功录制: {stats['successful_recordings']}")
    print(f"   Kilo Code事件总数: {stats['total_kilo_code_events']}")
    print(f"   平均响应时间: {stats['average_response_time']:.2f}s")
    
    # 列出所有录制
    recordings = recorder.list_recordings()
    print(f"\n📋 录制列表:")
    for recording in recordings:
        print(f"   {recording['recording_name']} - {recording['total_kilo_code_events']} 事件")
    
    print("\n🎉 一键录制工作流集成完成！")

