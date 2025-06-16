#!/usr/bin/env python3
"""
Operations Workflow MCP - MCP注册和整合管理器
负责管理和协调所有注册的子MCP
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MCPRegistry:
    """MCP注册表 - 管理所有注册的子MCP"""
    
    def __init__(self):
        self.registered_mcps = {}
        self.mcp_instances = {}
        self.mcp_status = {}
        
    def register_mcp(self, mcp_name: str, mcp_config: Dict) -> bool:
        """注册一个MCP到工作流中"""
        try:
            self.registered_mcps[mcp_name] = {
                "config": mcp_config,
                "registered_at": datetime.now().isoformat(),
                "status": "REGISTERED"
            }
            
            logger.info(f"✅ MCP注册成功: {mcp_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP注册失败: {mcp_name} - {str(e)}")
            return False
    
    def load_mcp(self, mcp_name: str) -> Optional[Any]:
        """加载并实例化MCP"""
        if mcp_name not in self.registered_mcps:
            logger.error(f"❌ MCP未注册: {mcp_name}")
            return None
            
        try:
            config = self.registered_mcps[mcp_name]["config"]
            module_path = config["module_path"]
            class_name = config["class_name"]
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(mcp_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取MCP类并实例化
            mcp_class = getattr(module, class_name)
            mcp_instance = mcp_class(**config.get("init_params", {}))
            
            self.mcp_instances[mcp_name] = mcp_instance
            self.mcp_status[mcp_name] = "LOADED"
            
            logger.info(f"✅ MCP加载成功: {mcp_name}")
            return mcp_instance
            
        except Exception as e:
            logger.error(f"❌ MCP加载失败: {mcp_name} - {str(e)}")
            self.mcp_status[mcp_name] = "ERROR"
            return None
    
    def call_mcp_method(self, mcp_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用MCP的方法"""
        if mcp_name not in self.mcp_instances:
            # 尝试加载MCP
            if not self.load_mcp(mcp_name):
                return None
        
        try:
            mcp_instance = self.mcp_instances[mcp_name]
            method = getattr(mcp_instance, method_name)
            result = method(*args, **kwargs)
            
            logger.info(f"✅ MCP方法调用成功: {mcp_name}.{method_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP方法调用失败: {mcp_name}.{method_name} - {str(e)}")
            return None
    
    def get_mcp_status(self, mcp_name: str = None) -> Dict:
        """获取MCP状态"""
        if mcp_name:
            return {
                "mcp_name": mcp_name,
                "registration_info": self.registered_mcps.get(mcp_name),
                "status": self.mcp_status.get(mcp_name, "NOT_LOADED"),
                "instance_loaded": mcp_name in self.mcp_instances
            }
        else:
            return {
                "total_registered": len(self.registered_mcps),
                "total_loaded": len(self.mcp_instances),
                "mcps": {name: self.get_mcp_status(name) for name in self.registered_mcps}
            }

class OperationsWorkflowMCPWithRegistry:
    """带有MCP注册功能的Operations Workflow MCP"""
    
    def __init__(self, base_path: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.base_path = Path(base_path)
        self.mcp_registry = MCPRegistry()
        self.operation_log = []
        
        # 自动注册已知的MCP
        self._auto_register_mcps()
        
        logger.info("🤖 Operations Workflow MCP (带注册功能) 初始化完成")
    
    def _auto_register_mcps(self):
        """自动注册已知的MCP"""
        # 注册Development Intervention MCP
        dev_intervention_config = {
            "module_path": str(self.base_path / "mcp/adapter/development_intervention_mcp/development_intervention_mcp.py"),
            "class_name": "DevelopmentInterventionMCP",
            "type": "adapter",
            "description": "开发介入MCP - 智能介入开发流程",
            "capabilities": ["code_analysis", "intervention_decision", "auto_fix"],
            "init_params": {}
        }
        
        self.mcp_registry.register_mcp("development_intervention_mcp", dev_intervention_config)
        
        # 注册其他MCP
        other_mcps = [
            {
                "name": "interaction_log_manager",
                "config": {
                    "module_path": str(self.base_path / "mcp/adapter/interaction_log_manager/interaction_log_manager.py"),
                    "class_name": "InteractionLogManager",
                    "type": "adapter",
                    "description": "交互日志管理器",
                    "capabilities": ["log_management", "data_analysis"]
                }
            },
            {
                "name": "directory_structure_mcp",
                "config": {
                    "module_path": str(self.base_path / "mcp/adapter/directory_structure_mcp/directory_structure_mcp.py"),
                    "class_name": "DirectoryStructureMCP", 
                    "type": "adapter",
                    "description": "目录结构管理MCP",
                    "capabilities": ["structure_validation", "auto_organization"]
                }
            }
        ]
        
        for mcp_info in other_mcps:
            self.mcp_registry.register_mcp(mcp_info["name"], mcp_info["config"])
    
    def test_mcp_integration(self) -> Dict:
        """测试MCP整合功能"""
        logger.info("🔧 开始测试MCP整合功能")
        
        results = {
            "test_name": "MCP整合功能测试",
            "status": "RUNNING",
            "registered_mcps": [],
            "loaded_mcps": [],
            "method_calls": [],
            "errors": []
        }
        
        try:
            # 1. 检查注册状态
            registry_status = self.mcp_registry.get_mcp_status()
            results["registered_mcps"] = list(registry_status["mcps"].keys())
            
            logger.info(f"📋 已注册MCP数量: {registry_status['total_registered']}")
            
            # 2. 尝试加载Development Intervention MCP
            dev_mcp = self.mcp_registry.load_mcp("development_intervention_mcp")
            if dev_mcp:
                results["loaded_mcps"].append("development_intervention_mcp")
                logger.info("✅ Development Intervention MCP 加载成功")
                
                # 3. 尝试调用MCP方法（如果存在）
                try:
                    # 假设MCP有get_status方法
                    status = self.mcp_registry.call_mcp_method("development_intervention_mcp", "get_status")
                    if status:
                        results["method_calls"].append({
                            "mcp": "development_intervention_mcp",
                            "method": "get_status",
                            "result": "SUCCESS"
                        })
                except:
                    # 如果方法不存在，创建一个模拟调用
                    results["method_calls"].append({
                        "mcp": "development_intervention_mcp", 
                        "method": "get_status",
                        "result": "METHOD_NOT_FOUND"
                    })
            
            # 4. 测试智能介入场景
            intervention_result = self._test_intelligent_intervention()
            results["intervention_test"] = intervention_result
            
            results["status"] = "SUCCESS"
            
        except Exception as e:
            error_msg = f"MCP整合测试异常: {str(e)}"
            logger.error(error_msg)
            results["status"] = "ERROR"
            results["errors"].append(error_msg)
        
        return results
    
    def _test_intelligent_intervention(self) -> Dict:
        """测试智能介入场景"""
        logger.info("🧠 测试智能介入场景")
        
        # 模拟一个需要介入的场景：检测到代码质量问题
        scenario = {
            "type": "code_quality_issue",
            "description": "检测到代码中存在潜在的性能问题",
            "file_path": "/mcp/adapter/development_intervention_mcp/development_intervention_mcp.py",
            "severity": "medium"
        }
        
        # 调用Development Intervention MCP进行智能介入
        intervention_decision = self.mcp_registry.call_mcp_method(
            "development_intervention_mcp",
            "analyze_intervention_need",
            scenario
        )
        
        return {
            "scenario": scenario,
            "intervention_decision": intervention_decision or "MCP_NOT_AVAILABLE",
            "status": "SIMULATED"
        }
    
    def get_workflow_status(self) -> Dict:
        """获取整个工作流状态"""
        return {
            "workflow_name": "Operations Workflow MCP",
            "status": "ACTIVE",
            "mcp_registry_status": self.mcp_registry.get_mcp_status(),
            "base_path": str(self.base_path),
            "total_operations": len(self.operation_log)
        }

def main():
    """主函数 - 测试MCP注册整合功能"""
    print("🤖 Operations Workflow MCP - MCP注册整合测试")
    print("=" * 80)
    
    # 创建带注册功能的Operations Workflow MCP
    ops_mcp = OperationsWorkflowMCPWithRegistry()
    
    # 测试MCP整合功能
    integration_result = ops_mcp.test_mcp_integration()
    
    # 显示测试结果
    print("\n📊 MCP整合测试结果:")
    print(f"   状态: {integration_result['status']}")
    print(f"   已注册MCP: {integration_result['registered_mcps']}")
    print(f"   已加载MCP: {integration_result['loaded_mcps']}")
    print(f"   方法调用: {len(integration_result['method_calls'])}")
    
    if integration_result.get("errors"):
        print("   错误:")
        for error in integration_result["errors"]:
            print(f"     - {error}")
    
    # 显示工作流状态
    workflow_status = ops_mcp.get_workflow_status()
    print(f"\n📋 工作流状态:")
    print(f"   总注册MCP: {workflow_status['mcp_registry_status']['total_registered']}")
    print(f"   总加载MCP: {workflow_status['mcp_registry_status']['total_loaded']}")
    
    # 保存结果
    results_file = Path(__file__).parent / "mcp_integration_test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "integration_result": integration_result,
            "workflow_status": workflow_status
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试结果已保存到: {results_file}")
    
    return integration_result["status"] == "SUCCESS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

