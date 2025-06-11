#!/usr/bin/env python3
"""
PowerAutomation 前置条件验证器

验证测试用例的前置条件是否满足
"""

import os
import sys
import platform
import psutil
import subprocess
from typing import Dict, List, Any, Optional

class PreconditionValidator:
    """前置条件验证器"""
    
    def __init__(self):
        self.current_platform = self._detect_platform()
        self.system_resources = self._get_system_resources()
        self.available_capabilities = self._detect_capabilities()
    
    def validate_preconditions(self, preconditions: Dict[str, Any]) -> Dict[str, Any]:
        """验证前置条件"""
        validation_result = {
            "valid": True,
            "reason": "",
            "details": {}
        }
        
        # 验证平台要求
        platform_valid = self._validate_platform(preconditions.get("platform", {}))
        if not platform_valid["valid"]:
            validation_result["valid"] = False
            validation_result["reason"] = f"平台要求不满足: {platform_valid['reason']}"
            return validation_result
        
        # 验证资源要求
        resource_valid = self._validate_resources(preconditions.get("resources", {}))
        if not resource_valid["valid"]:
            validation_result["valid"] = False
            validation_result["reason"] = f"资源要求不满足: {resource_valid['reason']}"
            return validation_result
        
        # 验证能力要求
        capability_valid = self._validate_capabilities(preconditions.get("capabilities", []))
        if not capability_valid["valid"]:
            validation_result["valid"] = False
            validation_result["reason"] = f"能力要求不满足: {capability_valid['reason']}"
            return validation_result
        
        validation_result["details"] = {
            "platform": platform_valid,
            "resources": resource_valid,
            "capabilities": capability_valid
        }
        
        return validation_result
    
    def _detect_platform(self) -> str:
        """检测当前平台"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源信息"""
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        # 检测GPU
        gpu_available = self._check_gpu_availability()
        
        return {
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
            "gpu_available": gpu_available
        }
    
    def _check_gpu_availability(self) -> bool:
        """检查GPU可用性"""
        try:
            # 尝试检测NVIDIA GPU
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # 可以添加其他GPU检测逻辑（AMD、Intel等）
        return False
    
    def _detect_capabilities(self) -> List[str]:
        """检测可用能力"""
        capabilities = []
        
        # 基础能力
        capabilities.append("basic_test")
        
        # UI测试能力
        if self._check_ui_test_capability():
            capabilities.append("ui_test")
        
        # AI测试能力
        if self._check_ai_test_capability():
            capabilities.append("ai_test")
        
        # 自动化测试能力
        capabilities.append("automation_test")
        
        # 兜底测试能力
        capabilities.append("fallback_test")
        
        # 数据测试能力
        capabilities.append("data_test")
        
        # 版本测试能力
        capabilities.append("version_test")
        
        return capabilities
    
    def _check_ui_test_capability(self) -> bool:
        """检查UI测试能力"""
        # 检查是否有图形界面
        if self.current_platform == "linux":
            return os.environ.get("DISPLAY") is not None
        else:
            return True  # Windows和macOS通常有图形界面
    
    def _check_ai_test_capability(self) -> bool:
        """检查AI测试能力"""
        # 检查是否有足够的资源运行AI测试
        return (self.system_resources["memory_gb"] >= 16 and 
                self.system_resources["cpu_cores"] >= 8)
    
    def _validate_platform(self, platform_req: Dict[str, List[str]]) -> Dict[str, Any]:
        """验证平台要求"""
        required_platforms = platform_req.get("required_platforms", [])
        excluded_platforms = platform_req.get("excluded_platforms", [])
        
        # 检查是否在排除列表中
        if self.current_platform in excluded_platforms:
            return {
                "valid": False,
                "reason": f"当前平台 {self.current_platform} 在排除列表中"
            }
        
        # 检查是否满足必需平台要求
        if required_platforms and self.current_platform not in required_platforms:
            return {
                "valid": False,
                "reason": f"当前平台 {self.current_platform} 不在必需平台列表中: {required_platforms}"
            }
        
        return {"valid": True, "reason": "平台要求满足"}
    
    def _validate_resources(self, resource_req: Dict[str, Any]) -> Dict[str, Any]:
        """验证资源要求"""
        min_memory = resource_req.get("min_memory_gb", 0)
        min_cpu_cores = resource_req.get("min_cpu_cores", 0)
        gpu_required = resource_req.get("gpu_required", False)
        
        # 检查内存
        if self.system_resources["memory_gb"] < min_memory:
            return {
                "valid": False,
                "reason": f"内存不足: 需要 {min_memory}GB，当前 {self.system_resources['memory_gb']:.1f}GB"
            }
        
        # 检查CPU核心数
        if self.system_resources["cpu_cores"] < min_cpu_cores:
            return {
                "valid": False,
                "reason": f"CPU核心数不足: 需要 {min_cpu_cores}核，当前 {self.system_resources['cpu_cores']}核"
            }
        
        # 检查GPU
        if gpu_required and not self.system_resources["gpu_available"]:
            return {
                "valid": False,
                "reason": "需要GPU但系统中未检测到可用GPU"
            }
        
        return {"valid": True, "reason": "资源要求满足"}
    
    def _validate_capabilities(self, capability_req: List[str]) -> Dict[str, Any]:
        """验证能力要求"""
        missing_capabilities = []
        
        for capability in capability_req:
            if capability not in self.available_capabilities:
                missing_capabilities.append(capability)
        
        if missing_capabilities:
            return {
                "valid": False,
                "reason": f"缺少必需能力: {missing_capabilities}"
            }
        
        return {"valid": True, "reason": "能力要求满足"}

if __name__ == "__main__":
    validator = PreconditionValidator()
    print(f"当前平台: {validator.current_platform}")
    print(f"系统资源: {validator.system_resources}")
    print(f"可用能力: {validator.available_capabilities}")
