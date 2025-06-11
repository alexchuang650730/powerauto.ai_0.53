#!/usr/bin/env python3
"""
PowerAutomation 测试流程录制引擎

一键录制工作流的核心引擎，支持：
- 测试动作录制
- 视觉验证集成
- 实时流程捕获
- 元数据收集
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# 导入视觉测试组件
sys.path.append(str(Path(__file__).parent))
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig

@dataclass
class TestAction:
    """测试动作数据类"""
    id: str
    type: str  # click, input, navigate, wait, verify, screenshot
    timestamp: str
    element_info: Dict[str, Any]
    action_data: Dict[str, Any]
    screenshot_path: Optional[str] = None
    visual_verification: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TestFlow:
    """测试流程数据类"""
    id: str
    name: str
    description: str
    start_time: str
    end_time: Optional[str]
    actions: List[TestAction]
    screenshots: List[str]
    visual_verifications: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    status: str  # recording, completed, failed

class TestFlowRecorder:
    """测试流程录制器"""
    
    def __init__(self, output_dir: str = None):
        # 设置输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent / "recorded_flows"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.flows_dir = self.output_dir / "flows"
        self.screenshots_dir = self.output_dir / "screenshots"
        self.visual_data_dir = self.output_dir / "visual_data"
        
        for directory in [self.flows_dir, self.screenshots_dir, self.visual_data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 录制状态
        self.is_recording = False
        self.current_flow: Optional[TestFlow] = None
        self.action_counter = 0
        
        # 视觉测试器
        self.visual_tester = None
        self.visual_config = VisualTestConfig(
            browser_type="chromium",
            headless=False,  # 录制时显示浏览器
            viewport_width=1920,
            viewport_height=1080,
            visual_threshold=0.05,
            auto_update_baseline=False
        )
        
        # 回调函数
        self.action_callbacks: List[Callable] = []
        self.flow_callbacks: List[Callable] = []
    
    def start_recording(self, flow_name: str, description: str = "", 
                       metadata: Dict[str, Any] = None) -> str:
        """开始录制测试流程"""
        if self.is_recording:
            raise RuntimeError("已有录制进行中，请先停止当前录制")
        
        flow_id = f"flow_{uuid.uuid4().hex[:8]}"
        
        self.current_flow = TestFlow(
            id=flow_id,
            name=flow_name,
            description=description,
            start_time=datetime.now().isoformat(),
            end_time=None,
            actions=[],
            screenshots=[],
            visual_verifications=[],
            metadata=metadata or {},
            status="recording"
        )
        
        self.is_recording = True
        self.action_counter = 0
        
        # 初始化视觉测试器
        try:
            self.visual_tester = PowerAutomationVisualTester(
                test_dir=str(self.visual_data_dir),
                config=self.visual_config
            )
            if self.visual_tester.start_browser():
                print(f"✅ 视觉测试浏览器已启动")
            else:
                print(f"⚠️ 视觉测试浏览器启动失败，将跳过视觉验证")
                self.visual_tester = None
        except Exception as e:
            print(f"⚠️ 视觉测试器初始化失败: {e}")
            self.visual_tester = None
        
        print(f"🎬 开始录制测试流程: {flow_name} (ID: {flow_id})")
        
        # 触发流程开始回调
        for callback in self.flow_callbacks:
            try:
                callback("flow_started", self.current_flow)
            except Exception as e:
                print(f"⚠️ 流程回调执行失败: {e}")
        
        return flow_id
    
    def stop_recording(self) -> Optional[TestFlow]:
        """停止录制测试流程"""
        if not self.is_recording or not self.current_flow:
            print("⚠️ 没有进行中的录制")
            return None
        
        self.current_flow.end_time = datetime.now().isoformat()
        self.current_flow.status = "completed"
        self.is_recording = False
        
        # 关闭视觉测试器
        if self.visual_tester:
            try:
                self.visual_tester.stop_browser()
            except Exception as e:
                print(f"⚠️ 关闭视觉测试浏览器失败: {e}")
        
        # 保存流程数据
        flow_data = self._save_flow(self.current_flow)
        
        print(f"🎬 录制完成: {self.current_flow.name}")
        print(f"   动作数量: {len(self.current_flow.actions)}")
        print(f"   截图数量: {len(self.current_flow.screenshots)}")
        print(f"   视觉验证: {len(self.current_flow.visual_verifications)}")
        
        # 触发流程完成回调
        for callback in self.flow_callbacks:
            try:
                callback("flow_completed", self.current_flow)
            except Exception as e:
                print(f"⚠️ 流程回调执行失败: {e}")
        
        completed_flow = self.current_flow
        self.current_flow = None
        
        return completed_flow
    
    def record_action(self, action_type: str, element_info: Dict[str, Any] = None,
                     action_data: Dict[str, Any] = None, 
                     take_screenshot: bool = True,
                     visual_verification: bool = False) -> Optional[TestAction]:
        """录制单个测试动作"""
        if not self.is_recording or not self.current_flow:
            print("⚠️ 没有进行中的录制")
            return None
        
        self.action_counter += 1
        action_id = f"action_{self.action_counter:03d}"
        
        action = TestAction(
            id=action_id,
            type=action_type,
            timestamp=datetime.now().isoformat(),
            element_info=element_info or {},
            action_data=action_data or {},
            metadata={}
        )
        
        # 截图
        if take_screenshot and self.visual_tester:
            try:
                screenshot_name = f"{self.current_flow.id}_{action_id}"
                screenshot_path = self.visual_tester.take_screenshot(
                    test_name=screenshot_name,
                    test_id=action_id
                )
                if screenshot_path:
                    action.screenshot_path = str(screenshot_path)
                    self.current_flow.screenshots.append(str(screenshot_path))
            except Exception as e:
                print(f"⚠️ 截图失败: {e}")
        
        # 视觉验证
        if visual_verification and self.visual_tester and action.screenshot_path:
            try:
                visual_result = self.visual_tester.compare_visual(
                    test_name=f"{self.current_flow.id}_{action_id}_verification",
                    test_id=f"{action_id}_visual",
                    current_screenshot_path=Path(action.screenshot_path),
                    update_baseline=True
                )
                
                action.visual_verification = asdict(visual_result)
                self.current_flow.visual_verifications.append(asdict(visual_result))
                
            except Exception as e:
                print(f"⚠️ 视觉验证失败: {e}")
        
        # 添加到流程
        self.current_flow.actions.append(action)
        
        print(f"📝 录制动作: {action_type} (ID: {action_id})")
        
        # 触发动作回调
        for callback in self.action_callbacks:
            try:
                callback("action_recorded", action)
            except Exception as e:
                print(f"⚠️ 动作回调执行失败: {e}")
        
        return action
    
    def record_navigation(self, url: str, wait_time: float = 2.0) -> Optional[TestAction]:
        """录制页面导航动作"""
        action_data = {
            "url": url,
            "wait_time": wait_time
        }
        
        # 如果有视觉测试器，执行实际导航
        if self.visual_tester:
            try:
                success = self.visual_tester.navigate_to(url)
                action_data["navigation_success"] = success
                if wait_time > 0:
                    time.sleep(wait_time)
            except Exception as e:
                action_data["navigation_error"] = str(e)
        
        return self.record_action(
            action_type="navigate",
            action_data=action_data,
            take_screenshot=True,
            visual_verification=True
        )
    
    def record_click(self, element_selector: str, element_text: str = "",
                    coordinates: tuple = None) -> Optional[TestAction]:
        """录制点击动作"""
        element_info = {
            "selector": element_selector,
            "text": element_text,
            "coordinates": coordinates
        }
        
        action_data = {
            "click_type": "element" if element_selector else "coordinate"
        }
        
        return self.record_action(
            action_type="click",
            element_info=element_info,
            action_data=action_data,
            take_screenshot=True
        )
    
    def record_input(self, element_selector: str, input_text: str,
                    clear_first: bool = True) -> Optional[TestAction]:
        """录制输入动作"""
        element_info = {
            "selector": element_selector
        }
        
        action_data = {
            "text": input_text,
            "clear_first": clear_first
        }
        
        return self.record_action(
            action_type="input",
            element_info=element_info,
            action_data=action_data,
            take_screenshot=True
        )
    
    def record_wait(self, wait_type: str, wait_value: Any, timeout: float = 10.0) -> Optional[TestAction]:
        """录制等待动作"""
        action_data = {
            "wait_type": wait_type,  # time, element, condition
            "wait_value": wait_value,
            "timeout": timeout
        }
        
        # 执行实际等待
        if wait_type == "time":
            time.sleep(float(wait_value))
        elif wait_type == "element" and self.visual_tester:
            try:
                self.visual_tester.wait_for_element(str(wait_value), int(timeout * 1000))
            except Exception as e:
                action_data["wait_error"] = str(e)
        
        return self.record_action(
            action_type="wait",
            action_data=action_data,
            take_screenshot=False
        )
    
    def record_verification(self, verification_type: str, expected_value: Any,
                          element_selector: str = None) -> Optional[TestAction]:
        """录制验证动作"""
        element_info = {
            "selector": element_selector
        } if element_selector else {}
        
        action_data = {
            "verification_type": verification_type,  # text, element_present, url, title
            "expected_value": expected_value
        }
        
        return self.record_action(
            action_type="verify",
            element_info=element_info,
            action_data=action_data,
            take_screenshot=True,
            visual_verification=True
        )
    
    def record_custom_action(self, action_name: str, action_data: Dict[str, Any],
                           element_info: Dict[str, Any] = None) -> Optional[TestAction]:
        """录制自定义动作"""
        return self.record_action(
            action_type=f"custom_{action_name}",
            element_info=element_info or {},
            action_data=action_data,
            take_screenshot=True
        )
    
    def _save_flow(self, flow: TestFlow) -> Dict[str, Any]:
        """保存流程数据"""
        flow_data = asdict(flow)
        
        # 保存JSON格式
        json_path = self.flows_dir / f"{flow.id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 流程数据已保存: {json_path}")
        return flow_data
    
    def load_flow(self, flow_id: str) -> Optional[TestFlow]:
        """加载流程数据"""
        json_path = self.flows_dir / f"{flow_id}.json"
        
        if not json_path.exists():
            print(f"❌ 流程文件不存在: {json_path}")
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
            
            # 重构TestAction对象
            actions = []
            for action_data in flow_data.get("actions", []):
                action = TestAction(**action_data)
                actions.append(action)
            
            flow_data["actions"] = actions
            flow = TestFlow(**flow_data)
            
            print(f"📂 流程数据已加载: {flow.name}")
            return flow
            
        except Exception as e:
            print(f"❌ 加载流程数据失败: {e}")
            return None
    
    def list_flows(self) -> List[Dict[str, Any]]:
        """列出所有录制的流程"""
        flows = []
        
        for json_file in self.flows_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    flow_data = json.load(f)
                
                flows.append({
                    "id": flow_data.get("id"),
                    "name": flow_data.get("name"),
                    "description": flow_data.get("description"),
                    "start_time": flow_data.get("start_time"),
                    "end_time": flow_data.get("end_time"),
                    "status": flow_data.get("status"),
                    "action_count": len(flow_data.get("actions", [])),
                    "screenshot_count": len(flow_data.get("screenshots", [])),
                    "file_path": str(json_file)
                })
                
            except Exception as e:
                print(f"⚠️ 读取流程文件失败 {json_file}: {e}")
        
        return sorted(flows, key=lambda x: x.get("start_time", ""), reverse=True)
    
    def add_action_callback(self, callback: Callable):
        """添加动作回调函数"""
        self.action_callbacks.append(callback)
    
    def add_flow_callback(self, callback: Callable):
        """添加流程回调函数"""
        self.flow_callbacks.append(callback)
    
    @contextmanager
    def recording_session(self, flow_name: str, description: str = "",
                         metadata: Dict[str, Any] = None):
        """录制会话上下文管理器"""
        flow_id = self.start_recording(flow_name, description, metadata)
        try:
            yield flow_id
        finally:
            self.stop_recording()

# 便捷的录制装饰器
def record_test_flow(flow_name: str, description: str = "", 
                    output_dir: str = None):
    """测试流程录制装饰器"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            recorder = TestFlowRecorder(output_dir)
            
            with recorder.recording_session(flow_name, description):
                # 将录制器传递给测试函数
                if 'recorder' in test_func.__code__.co_varnames:
                    kwargs['recorder'] = recorder
                
                result = test_func(*args, **kwargs)
                return result
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # 示例使用
    recorder = TestFlowRecorder()
    
    # 示例录制会话
    with recorder.recording_session("示例测试流程", "演示录制功能"):
        # 录制导航
        recorder.record_navigation("https://www.google.com")
        
        # 录制等待
        recorder.record_wait("time", 2.0)
        
        # 录制点击
        recorder.record_click("input[name='q']", "搜索框")
        
        # 录制输入
        recorder.record_input("input[name='q']", "PowerAutomation")
        
        # 录制验证
        recorder.record_verification("element_present", True, "input[name='q']")
        
        # 录制自定义动作
        recorder.record_custom_action("search_submit", {
            "method": "enter_key",
            "search_term": "PowerAutomation"
        })
    
    # 列出所有流程
    flows = recorder.list_flows()
    print(f"\n📋 录制的流程数量: {len(flows)}")
    for flow in flows:
        print(f"   {flow['name']} ({flow['action_count']} 动作)")
    
    print("\n🎉 测试流程录制引擎演示完成！")

