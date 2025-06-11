#!/usr/bin/env python3
"""
n8n工作流转换器增强版

专门用于将PowerAutomation测试录制数据转换为标准n8n工作流格式
支持Kilo Code智能介入检测的专业化转换，生成可执行的自动化测试工作流
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

# 导入录制器组件
sys.path.append(str(Path(__file__).parent))
from workflow_recorder_integration import WorkflowRecorder
from kilo_code_recorder import KiloCodeRecorder, StruggleModeType, InterventionType

@dataclass
class N8nNode:
    """n8n节点定义"""
    id: str
    name: str
    type: str
    typeVersion: int
    position: List[int]
    parameters: Dict[str, Any]
    credentials: Optional[Dict[str, Any]] = None
    webhookId: Optional[str] = None
    disabled: bool = False

@dataclass
class N8nConnection:
    """n8n连接定义"""
    node: str
    type: str
    index: int

@dataclass
class N8nWorkflow:
    """n8n工作流定义"""
    id: str
    name: str
    active: bool
    nodes: List[N8nNode]
    connections: Dict[str, Dict[str, List[List[N8nConnection]]]]
    settings: Dict[str, Any]
    staticData: Dict[str, Any]
    tags: List[str]
    meta: Dict[str, Any]
    pinData: Optional[Dict[str, Any]] = None
    versionId: Optional[str] = None

class N8nWorkflowConverter:
    """n8n工作流转换器"""
    
    def __init__(self, output_dir: str = None):
        # 设置输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent / "n8n_workflows_enhanced"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录结构
        self.kilo_code_workflows_dir = self.output_dir / "kilo_code"
        self.general_workflows_dir = self.output_dir / "general"
        self.templates_dir = self.output_dir / "templates"
        self.exports_dir = self.output_dir / "exports"
        
        for directory in [self.kilo_code_workflows_dir, self.general_workflows_dir, 
                         self.templates_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 节点类型映射
        self.node_type_mapping = {
            "kilo_code_detection": "n8n-nodes-base.function",
            "struggle_mode": "n8n-nodes-base.httpRequest",
            "intervention_trigger": "n8n-nodes-base.webhook",
            "accuracy_validation": "n8n-nodes-base.set",
            "ui_interaction": "n8n-nodes-base.httpRequest",
            "user_action": "n8n-nodes-base.function",
            "visual_verification": "n8n-nodes-base.httpRequest"
        }
        
        # 预定义模板
        self.workflow_templates = self._load_workflow_templates()
    
    def _load_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载工作流模板"""
        templates = {}
        
        # Kilo Code检测模板
        templates["kilo_code_detection"] = {
            "name_pattern": "PowerAutomation_KiloCode_{scenario}_{version}",
            "description": "Kilo Code智能介入检测自动化测试工作流",
            "tags": ["powerautomation", "kilo-code", "testing", "automation"],
            "default_settings": {
                "executionOrder": "v1",
                "saveManualExecutions": True,
                "callerPolicy": "workflowsFromSameOwner",
                "errorWorkflow": "",
                "timezone": "Asia/Shanghai"
            },
            "required_credentials": ["powerautomation_api", "test_environment"],
            "webhook_settings": {
                "httpMethod": "POST",
                "responseMode": "onReceived",
                "path": "kilo-code-test"
            }
        }
        
        # 通用测试模板
        templates["general_test"] = {
            "name_pattern": "PowerAutomation_Test_{test_type}_{timestamp}",
            "description": "PowerAutomation通用自动化测试工作流",
            "tags": ["powerautomation", "testing", "automation"],
            "default_settings": {
                "executionOrder": "v1",
                "saveManualExecutions": True,
                "callerPolicy": "workflowsFromSameOwner"
            },
            "required_credentials": ["powerautomation_api"],
            "webhook_settings": {
                "httpMethod": "POST",
                "responseMode": "onReceived",
                "path": "general-test"
            }
        }
        
        return templates
    
    def convert_recording_to_n8n(self, recording_data: Dict[str, Any], 
                                workflow_type: str = "kilo_code_detection") -> N8nWorkflow:
        """将录制数据转换为n8n工作流"""
        
        # 获取模板
        template = self.workflow_templates.get(workflow_type, self.workflow_templates["general_test"])
        
        # 生成工作流基本信息
        workflow_id = str(uuid.uuid4())
        workflow_name = self._generate_workflow_name(recording_data, template)
        
        # 创建节点列表
        nodes = []
        connections = {}
        
        # 添加开始节点
        start_node = self._create_start_node()
        nodes.append(start_node)
        
        # 添加Webhook触发节点（如果需要）
        if workflow_type == "kilo_code_detection":
            webhook_node = self._create_webhook_node(template["webhook_settings"])
            nodes.append(webhook_node)
            connections[start_node.name] = {"main": [[N8nConnection(webhook_node.name, "main", 0)]]}
            previous_node = webhook_node.name
        else:
            previous_node = start_node.name
        
        # 处理Kilo Code事件
        if "kilo_code_events" in recording_data:
            kilo_nodes, kilo_connections = self._convert_kilo_code_events(
                recording_data["kilo_code_events"], 
                previous_node,
                len(nodes)
            )
            nodes.extend(kilo_nodes)
            connections.update(kilo_connections)
            if kilo_nodes:
                previous_node = kilo_nodes[-1].name
        
        # 处理一般动作
        if "actions" in recording_data:
            action_nodes, action_connections = self._convert_actions(
                recording_data["actions"],
                previous_node,
                len(nodes)
            )
            nodes.extend(action_nodes)
            connections.update(action_connections)
            if action_nodes:
                previous_node = action_nodes[-1].name
        
        # 添加验证节点
        validation_node = self._create_validation_node(recording_data, len(nodes))
        nodes.append(validation_node)
        if previous_node not in connections:
            connections[previous_node] = {"main": [[]]}
        connections[previous_node]["main"][0].append(N8nConnection(validation_node.name, "main", 0))
        
        # 添加结果输出节点
        output_node = self._create_output_node(recording_data, len(nodes))
        nodes.append(output_node)
        connections[validation_node.name] = {"main": [[N8nConnection(output_node.name, "main", 0)]]}
        
        # 创建工作流对象
        workflow = N8nWorkflow(
            id=workflow_id,
            name=workflow_name,
            active=True,
            nodes=nodes,
            connections=self._format_connections(connections),
            settings=template["default_settings"],
            staticData={},
            tags=template["tags"],
            meta={
                "powerautomation_recording_id": recording_data.get("recording_id"),
                "recording_mode": recording_data.get("recording_mode"),
                "target_version": recording_data.get("target_version"),
                "generated_at": datetime.now().isoformat(),
                "converter_version": "1.0.0",
                "template_type": workflow_type
            }
        )
        
        return workflow
    
    def _generate_workflow_name(self, recording_data: Dict[str, Any], template: Dict[str, Any]) -> str:
        """生成工作流名称"""
        pattern = template["name_pattern"]
        
        # 替换占位符
        replacements = {
            "scenario": recording_data.get("recording_name", "Unknown").replace(" ", "_"),
            "version": recording_data.get("target_version", "unknown"),
            "test_type": recording_data.get("recording_mode", "general"),
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        name = pattern
        for placeholder, value in replacements.items():
            name = name.replace(f"{{{placeholder}}}", str(value))
        
        return name
    
    def _create_start_node(self) -> N8nNode:
        """创建开始节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name="Start",
            type="n8n-nodes-base.start",
            typeVersion=1,
            position=[240, 300],
            parameters={}
        )
    
    def _create_webhook_node(self, webhook_settings: Dict[str, Any]) -> N8nNode:
        """创建Webhook节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name="Webhook_Trigger",
            type="n8n-nodes-base.webhook",
            typeVersion=1,
            position=[440, 300],
            parameters={
                "httpMethod": webhook_settings.get("httpMethod", "POST"),
                "path": webhook_settings.get("path", "test-trigger"),
                "responseMode": webhook_settings.get("responseMode", "onReceived"),
                "options": {}
            },
            webhookId=str(uuid.uuid4())
        )
    
    def _convert_kilo_code_events(self, kilo_events: List[Dict[str, Any]], 
                                 previous_node: str, start_position: int) -> tuple:
        """转换Kilo Code事件为n8n节点"""
        nodes = []
        connections = {}
        
        for i, event in enumerate(kilo_events):
            node_position = [240 + (start_position + i) * 200, 300]
            
            if event["detection_type"].startswith("struggle_mode"):
                node = self._create_struggle_mode_node(event, node_position)
            elif event["detection_type"] == "intervention_trigger":
                node = self._create_intervention_node(event, node_position)
            elif event["detection_type"] == "accuracy_validation":
                node = self._create_accuracy_node(event, node_position)
            else:
                node = self._create_generic_kilo_node(event, node_position)
            
            nodes.append(node)
            
            # 创建连接
            if previous_node not in connections:
                connections[previous_node] = {"main": [[]]}
            connections[previous_node]["main"][0].append(N8nConnection(node.name, "main", 0))
            
            previous_node = node.name
        
        return nodes, connections
    
    def _create_struggle_mode_node(self, event: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建挣扎模式检测节点"""
        struggle_mode = event["detection_type"]
        
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Detect_{struggle_mode}",
            type="n8n-nodes-base.function",
            typeVersion=1,
            position=position,
            parameters={
                "functionCode": f"""
// Kilo Code挣扎模式检测: {struggle_mode}
const detectionData = {json.dumps(event["detection_data"], indent=2)};
const confidenceScore = {event["confidence_score"]};
const responseTime = {event["response_time"]};

// 验证检测结果
const isValid = confidenceScore >= 0.85 && responseTime <= 3.0;

// 记录检测事件
const result = {{
  event_id: "{event["event_id"]}",
  detection_type: "{struggle_mode}",
  detection_data: detectionData,
  confidence_score: confidenceScore,
  response_time: responseTime,
  timestamp: new Date().toISOString(),
  validation_passed: isValid,
  performance_metrics: {{
    accuracy_threshold: 0.85,
    response_time_threshold: 3.0,
    accuracy_status: confidenceScore >= 0.85 ? "PASS" : "FAIL",
    response_time_status: responseTime <= 3.0 ? "PASS" : "FAIL"
  }}
}};

return [result];
""",
                "options": {}
            }
        )
    
    def _create_intervention_node(self, event: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建智能介入节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Intervention_{event['event_id']}",
            type="n8n-nodes-base.httpRequest",
            typeVersion=3,
            position=position,
            parameters={
                "method": "POST",
                "url": "{{$env.POWERAUTOMATION_API_URL}}/kilo-code/intervention",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "powerautomationApi",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "X-Test-Mode", "value": "true"}
                    ]
                },
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "intervention_data", "value": json.dumps(event["detection_data"])},
                        {"name": "confidence_score", "value": str(event["confidence_score"])},
                        {"name": "response_time", "value": str(event["response_time"])},
                        {"name": "event_id", "value": event["event_id"]}
                    ]
                },
                "options": {
                    "timeout": 10000,
                    "retry": {
                        "enabled": True,
                        "maxTries": 3
                    }
                }
            }
        )
    
    def _create_accuracy_node(self, event: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建准确率验证节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Accuracy_Check_{event['event_id']}",
            type="n8n-nodes-base.set",
            typeVersion=1,
            position=position,
            parameters={
                "values": {
                    "values": [
                        {
                            "name": "accuracy_score",
                            "type": "number",
                            "value": event["confidence_score"]
                        },
                        {
                            "name": "response_time",
                            "type": "number", 
                            "value": event["response_time"]
                        },
                        {
                            "name": "validation_data",
                            "type": "object",
                            "value": json.dumps(event["detection_data"])
                        },
                        {
                            "name": "accuracy_passed",
                            "type": "boolean",
                            "value": event["confidence_score"] >= 0.85
                        },
                        {
                            "name": "performance_passed",
                            "type": "boolean",
                            "value": event["response_time"] <= 3.0
                        }
                    ]
                },
                "options": {}
            }
        )
    
    def _create_generic_kilo_node(self, event: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建通用Kilo Code节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"KiloCode_{event['event_id']}",
            type="n8n-nodes-base.function",
            typeVersion=1,
            position=position,
            parameters={
                "functionCode": f"""
// Kilo Code通用事件处理
const eventData = {json.dumps(event, indent=2)};

// 处理事件数据
const result = {{
  ...eventData,
  processed_at: new Date().toISOString(),
  node_type: "generic_kilo_code"
}};

return [result];
""",
                "options": {}
            }
        )
    
    def _convert_actions(self, actions: List[Dict[str, Any]], 
                        previous_node: str, start_position: int) -> tuple:
        """转换一般动作为n8n节点"""
        nodes = []
        connections = {}
        
        for i, action in enumerate(actions):
            if action.get("action_name", "").startswith("kilo_code"):
                continue  # Kilo Code事件已经处理过了
            
            node_position = [240 + (start_position + i) * 200, 400]
            
            if action.get("action_name") == "click":
                node = self._create_click_node(action, node_position)
            elif action.get("action_name") == "input":
                node = self._create_input_node(action, node_position)
            elif action.get("action_name") == "navigation":
                node = self._create_navigation_node(action, node_position)
            else:
                node = self._create_generic_action_node(action, node_position)
            
            nodes.append(node)
            
            # 创建连接
            if previous_node not in connections:
                connections[previous_node] = {"main": [[]]}
            connections[previous_node]["main"][0].append(N8nConnection(node.name, "main", 0))
            
            previous_node = node.name
        
        return nodes, connections
    
    def _create_click_node(self, action: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建点击动作节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Click_{action['id']}",
            type="n8n-nodes-base.httpRequest",
            typeVersion=3,
            position=position,
            parameters={
                "method": "POST",
                "url": "{{$env.POWERAUTOMATION_API_URL}}/ui/click",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "element_selector", "value": action.get("element_selector", "")},
                        {"name": "element_text", "value": action.get("element_text", "")},
                        {"name": "coordinates", "value": json.dumps(action.get("coordinates", {}))},
                        {"name": "action_id", "value": action["id"]}
                    ]
                }
            }
        )
    
    def _create_input_node(self, action: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建输入动作节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Input_{action['id']}",
            type="n8n-nodes-base.httpRequest",
            typeVersion=3,
            position=position,
            parameters={
                "method": "POST",
                "url": "{{$env.POWERAUTOMATION_API_URL}}/ui/input",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "element_selector", "value": action.get("element_selector", "")},
                        {"name": "input_text", "value": action.get("input_text", "")},
                        {"name": "clear_first", "value": str(action.get("clear_first", True))},
                        {"name": "action_id", "value": action["id"]}
                    ]
                }
            }
        )
    
    def _create_navigation_node(self, action: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建导航动作节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Navigate_{action['id']}",
            type="n8n-nodes-base.httpRequest",
            typeVersion=3,
            position=position,
            parameters={
                "method": "POST",
                "url": "{{$env.POWERAUTOMATION_API_URL}}/ui/navigate",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "url", "value": action.get("url", "")},
                        {"name": "wait_time", "value": str(action.get("wait_time", 2.0))},
                        {"name": "action_id", "value": action["id"]}
                    ]
                }
            }
        )
    
    def _create_generic_action_node(self, action: Dict[str, Any], position: List[int]) -> N8nNode:
        """创建通用动作节点"""
        return N8nNode(
            id=str(uuid.uuid4()),
            name=f"Action_{action['id']}",
            type="n8n-nodes-base.function",
            typeVersion=1,
            position=position,
            parameters={
                "functionCode": f"""
// 通用动作处理
const actionData = {json.dumps(action, indent=2)};

// 处理动作数据
const result = {{
  ...actionData,
  processed_at: new Date().toISOString(),
  node_type: "generic_action"
}};

return [result];
""",
                "options": {}
            }
        )
    
    def _create_validation_node(self, recording_data: Dict[str, Any], position_index: int) -> N8nNode:
        """创建验证节点"""
        position = [240 + position_index * 200, 300]
        
        return N8nNode(
            id=str(uuid.uuid4()),
            name="Final_Validation",
            type="n8n-nodes-base.function",
            typeVersion=1,
            position=position,
            parameters={
                "functionCode": f"""
// 最终验证逻辑
const recordingStats = {json.dumps(recording_data.get("statistics", {}), indent=2)};
const kiloCodeEvents = {len(recording_data.get("kilo_code_events", []))};
const totalActions = {len(recording_data.get("actions", []))};

// 验证标准
const validationCriteria = {{
  min_kilo_code_events: 1,
  max_average_response_time: 3.0,
  min_accuracy_rate: 0.85
}};

// 执行验证
const avgResponseTime = recordingStats.average_kilo_code_response_time || 0;
const avgAccuracy = recordingStats.average_accuracy || 0;

const validationResult = {{
  recording_id: "{recording_data.get('recording_id', '')}",
  validation_timestamp: new Date().toISOString(),
  kilo_code_events_count: kiloCodeEvents,
  total_actions_count: totalActions,
  average_response_time: avgResponseTime,
  average_accuracy: avgAccuracy,
  validations: {{
    kilo_code_events_sufficient: kiloCodeEvents >= validationCriteria.min_kilo_code_events,
    response_time_acceptable: avgResponseTime <= validationCriteria.max_average_response_time,
    accuracy_acceptable: avgAccuracy >= validationCriteria.min_accuracy_rate
  }},
  overall_status: "UNKNOWN"
}};

// 计算总体状态
const allValidationsPassed = Object.values(validationResult.validations).every(v => v === true);
validationResult.overall_status = allValidationsPassed ? "PASS" : "FAIL";

return [validationResult];
""",
                "options": {}
            }
        )
    
    def _create_output_node(self, recording_data: Dict[str, Any], position_index: int) -> N8nNode:
        """创建输出节点"""
        position = [240 + position_index * 200, 300]
        
        return N8nNode(
            id=str(uuid.uuid4()),
            name="Test_Results_Output",
            type="n8n-nodes-base.httpRequest",
            typeVersion=3,
            position=position,
            parameters={
                "method": "POST",
                "url": "{{$env.POWERAUTOMATION_API_URL}}/test-results",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "powerautomationApi",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Content-Type", "value": "application/json"}
                    ]
                },
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "recording_id", "value": recording_data.get("recording_id", "")},
                        {"name": "test_results", "value": "{{JSON.stringify($json)}}"},
                        {"name": "timestamp", "value": "{{new Date().toISOString()}}"}
                    ]
                },
                "options": {
                    "timeout": 10000
                }
            }
        )
    
    def _format_connections(self, connections: Dict[str, Any]) -> Dict[str, Dict[str, List[List[Dict[str, Any]]]]]:
        """格式化连接为n8n格式"""
        formatted = {}
        
        for source_node, connection_data in connections.items():
            formatted[source_node] = {}
            for connection_type, connection_list in connection_data.items():
                formatted[source_node][connection_type] = []
                for connection_group in connection_list:
                    formatted_group = []
                    for connection in connection_group:
                        formatted_group.append({
                            "node": connection.node,
                            "type": connection.type,
                            "index": connection.index
                        })
                    formatted[source_node][connection_type].append(formatted_group)
        
        return formatted
    
    def save_workflow(self, workflow: N8nWorkflow, filename: str = None) -> str:
        """保存工作流到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{workflow.name}_{timestamp}.json"
        
        # 确定保存目录
        if "kilo" in workflow.name.lower():
            save_dir = self.kilo_code_workflows_dir
        else:
            save_dir = self.general_workflows_dir
        
        file_path = save_dir / filename
        
        # 转换为字典格式
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "active": workflow.active,
            "nodes": [asdict(node) for node in workflow.nodes],
            "connections": workflow.connections,
            "settings": workflow.settings,
            "staticData": workflow.staticData,
            "tags": workflow.tags,
            "meta": workflow.meta
        }
        
        if workflow.pinData:
            workflow_dict["pinData"] = workflow.pinData
        if workflow.versionId:
            workflow_dict["versionId"] = workflow.versionId
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 n8n工作流已保存: {file_path}")
        return str(file_path)
    
    def export_for_n8n_import(self, workflow: N8nWorkflow) -> str:
        """导出为n8n导入格式"""
        export_data = {
            "name": workflow.name,
            "nodes": [asdict(node) for node in workflow.nodes],
            "connections": workflow.connections,
            "active": workflow.active,
            "settings": workflow.settings,
            "staticData": workflow.staticData,
            "tags": workflow.tags,
            "meta": workflow.meta
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"{workflow.name}_export_{timestamp}.json"
        export_path = self.exports_dir / export_filename
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📤 n8n导入文件已生成: {export_path}")
        return str(export_path)
    
    def convert_kilo_code_recording(self, recording_file: str) -> str:
        """转换Kilo Code录制文件为n8n工作流"""
        # 读取录制数据
        with open(recording_file, 'r', encoding='utf-8') as f:
            recording_data = json.load(f)
        
        # 转换为n8n工作流
        workflow = self.convert_recording_to_n8n(recording_data, "kilo_code_detection")
        
        # 保存工作流
        workflow_path = self.save_workflow(workflow)
        
        # 生成导出文件
        export_path = self.export_for_n8n_import(workflow)
        
        return workflow_path

if __name__ == "__main__":
    # 示例使用
    converter = N8nWorkflowConverter()
    
    # 模拟录制数据
    sample_recording = {
        "recording_id": "recording_sample_001",
        "recording_name": "Kilo Code企业版测试",
        "recording_mode": "kilo_code_detection",
        "target_version": "enterprise",
        "start_time": "2025-01-11T10:00:00Z",
        "end_time": "2025-01-11T10:05:00Z",
        "kilo_code_events": [
            {
                "event_id": "kilo_event_001",
                "timestamp": "2025-01-11T10:01:00Z",
                "detection_type": "struggle_mode_1",
                "detection_data": {"error_type": "syntax_error", "line": 42},
                "confidence_score": 0.95,
                "response_time": 1.2
            },
            {
                "event_id": "kilo_event_002",
                "timestamp": "2025-01-11T10:02:00Z",
                "detection_type": "intervention_trigger",
                "detection_data": {"intervention_type": "code_suggestion", "suggestion": "添加分号"},
                "confidence_score": 0.90,
                "response_time": 0.8
            },
            {
                "event_id": "kilo_event_003",
                "timestamp": "2025-01-11T10:03:00Z",
                "detection_type": "accuracy_validation",
                "detection_data": {"total_detections": 2, "correct_detections": 2},
                "confidence_score": 1.0,
                "response_time": 0.1
            }
        ],
        "actions": [
            {
                "id": "action_001",
                "action_name": "click",
                "element_selector": ".kilo-code-panel",
                "element_text": "智能介入面板",
                "timestamp": "2025-01-11T10:01:30Z"
            },
            {
                "id": "action_002",
                "action_name": "input",
                "element_selector": "#code-input",
                "input_text": "function test() { return true }",
                "timestamp": "2025-01-11T10:02:30Z"
            }
        ],
        "statistics": {
            "total_kilo_code_events": 3,
            "average_kilo_code_response_time": 0.7,
            "average_accuracy": 0.95
        }
    }
    
    # 转换为n8n工作流
    workflow = converter.convert_recording_to_n8n(sample_recording, "kilo_code_detection")
    
    # 保存工作流
    workflow_path = converter.save_workflow(workflow)
    
    # 生成导出文件
    export_path = converter.export_for_n8n_import(workflow)
    
    print(f"\n🎉 n8n工作流转换完成!")
    print(f"   工作流名称: {workflow.name}")
    print(f"   节点数量: {len(workflow.nodes)}")
    print(f"   连接数量: {len(workflow.connections)}")
    print(f"   保存路径: {workflow_path}")
    print(f"   导出路径: {export_path}")

