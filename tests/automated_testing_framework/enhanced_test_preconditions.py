#!/usr/bin/env python3
"""
PowerAutomation 增强前置条件系统

集成到测试框架的前置条件验证和管理系统
支持平台选择、资源验证、能力检查等功能
"""

import os
import sys
import json
import yaml
import platform
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TestPreconditions:
    """测试前置条件数据类"""
    platform: Dict[str, List[str]]
    resources: Dict[str, Any]
    capabilities: List[str]
    environment: Dict[str, str]
    dependencies: List[str]

class EnhancedPreconditionValidator:
    """增强前置条件验证器"""
    
    def __init__(self):
        self.current_platform = self._detect_platform()
        self.system_resources = self._get_system_resources()
        self.available_capabilities = self._detect_capabilities()
        self.environment_info = self._get_environment_info()
        
        # 加载测试框架配置
        self.framework_config = self._load_framework_config()
    
    def validate_preconditions(self, preconditions: Dict[str, Any]) -> Dict[str, Any]:
        """验证前置条件"""
        validation_result = {
            "valid": True,
            "reason": "",
            "details": {},
            "recommendations": []
        }
        
        try:
            # 验证平台要求
            platform_valid = self._validate_platform(preconditions.get("platform", {}))
            if not platform_valid["valid"]:
                validation_result["valid"] = False
                validation_result["reason"] = f"平台要求不满足: {platform_valid['reason']}"
                validation_result["recommendations"].extend(platform_valid.get("recommendations", []))
                return validation_result
            
            # 验证资源要求
            resource_valid = self._validate_resources(preconditions.get("resources", {}))
            if not resource_valid["valid"]:
                validation_result["valid"] = False
                validation_result["reason"] = f"资源要求不满足: {resource_valid['reason']}"
                validation_result["recommendations"].extend(resource_valid.get("recommendations", []))
                return validation_result
            
            # 验证能力要求
            capability_valid = self._validate_capabilities(preconditions.get("capabilities", []))
            if not capability_valid["valid"]:
                validation_result["valid"] = False
                validation_result["reason"] = f"能力要求不满足: {capability_valid['reason']}"
                validation_result["recommendations"].extend(capability_valid.get("recommendations", []))
                return validation_result
            
            # 验证环境要求
            environment_valid = self._validate_environment(preconditions.get("environment", {}))
            if not environment_valid["valid"]:
                validation_result["valid"] = False
                validation_result["reason"] = f"环境要求不满足: {environment_valid['reason']}"
                validation_result["recommendations"].extend(environment_valid.get("recommendations", []))
                return validation_result
            
            # 验证依赖要求
            dependency_valid = self._validate_dependencies(preconditions.get("dependencies", []))
            if not dependency_valid["valid"]:
                validation_result["valid"] = False
                validation_result["reason"] = f"依赖要求不满足: {dependency_valid['reason']}"
                validation_result["recommendations"].extend(dependency_valid.get("recommendations", []))
                return validation_result
            
            validation_result["details"] = {
                "platform": platform_valid,
                "resources": resource_valid,
                "capabilities": capability_valid,
                "environment": environment_valid,
                "dependencies": dependency_valid
            }
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["reason"] = f"验证过程中发生错误: {str(e)}"
        
        return validation_result
    
    def get_optimal_platform(self, platform_requirements: Dict[str, List[str]]) -> Optional[str]:
        """获取最优平台选择"""
        required_platforms = platform_requirements.get("required_platforms", [])
        preferred_platforms = platform_requirements.get("preferred_platforms", [])
        excluded_platforms = platform_requirements.get("excluded_platforms", [])
        
        # 检查当前平台是否被排除
        if self.current_platform in excluded_platforms:
            return None
        
        # 检查当前平台是否在必需列表中
        if required_platforms and self.current_platform not in required_platforms:
            return None
        
        # 如果当前平台在首选列表中，返回当前平台
        if preferred_platforms and self.current_platform in preferred_platforms:
            return self.current_platform
        
        # 如果没有首选列表，但满足必需要求，返回当前平台
        if not preferred_platforms and (not required_platforms or self.current_platform in required_platforms):
            return self.current_platform
        
        # 返回首选列表中的第一个可用平台
        for platform in preferred_platforms:
            if platform not in excluded_platforms and (not required_platforms or platform in required_platforms):
                return platform
        
        return None
    
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
        cpu_freq = psutil.cpu_freq()
        disk_usage = psutil.disk_usage('/')
        
        # 检测GPU
        gpu_info = self._get_gpu_info()
        
        return {
            "memory_gb": round(memory_gb, 2),
            "cpu_cores": cpu_cores,
            "cpu_frequency_mhz": cpu_freq.current if cpu_freq else 0,
            "disk_free_gb": round(disk_usage.free / (1024**3), 2),
            "disk_total_gb": round(disk_usage.total / (1024**3), 2),
            "gpu_available": gpu_info["available"],
            "gpu_info": gpu_info
        }
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        gpu_info = {
            "available": False,
            "type": "none",
            "memory_gb": 0,
            "driver_version": ""
        }
        
        try:
            # 尝试检测NVIDIA GPU
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    parts = lines[0].split(', ')
                    if len(parts) >= 3:
                        gpu_info.update({
                            "available": True,
                            "type": "nvidia",
                            "name": parts[0],
                            "memory_gb": round(float(parts[1]) / 1024, 2),
                            "driver_version": parts[2]
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
        
        # 可以添加其他GPU检测逻辑（AMD、Intel等）
        if not gpu_info["available"]:
            # 检查是否有集成显卡
            if self.current_platform == "macos":
                gpu_info.update({
                    "available": True,
                    "type": "integrated",
                    "name": "Apple Integrated GPU"
                })
        
        return gpu_info
    
    def _get_environment_info(self) -> Dict[str, str]:
        """获取环境信息"""
        env_info = {
            "os_name": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }
        
        # 添加特定平台的信息
        if self.current_platform == "linux":
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            env_info["linux_distribution"] = line.split('=')[1].strip().strip('"')
                            break
            except FileNotFoundError:
                pass
        elif self.current_platform == "macos":
            env_info["macos_version"] = platform.mac_ver()[0]
        elif self.current_platform == "windows":
            env_info["windows_version"] = platform.win32_ver()[0]
        
        return env_info
    
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
        if self._check_data_test_capability():
            capabilities.append("data_test")
        
        # 版本测试能力
        capabilities.append("version_test")
        
        # 性能测试能力
        if self._check_performance_test_capability():
            capabilities.append("performance_test")
        
        # API测试能力
        capabilities.append("api_test")
        
        # 集成测试能力
        capabilities.append("integration_test")
        
        # iOS测试能力（仅macOS）
        if self.current_platform == "macos":
            capabilities.append("ios_test")
        
        # 安全测试能力
        if self._check_security_test_capability():
            capabilities.append("security_test")
        
        return capabilities
    
    def _check_ui_test_capability(self) -> bool:
        """检查UI测试能力"""
        if self.current_platform == "linux":
            return os.environ.get("DISPLAY") is not None
        else:
            return True  # Windows和macOS通常有图形界面
    
    def _check_ai_test_capability(self) -> bool:
        """检查AI测试能力"""
        return (self.system_resources["memory_gb"] >= 8 and 
                self.system_resources["cpu_cores"] >= 4)
    
    def _check_data_test_capability(self) -> bool:
        """检查数据测试能力"""
        return (self.system_resources["memory_gb"] >= 4 and
                self.system_resources["disk_free_gb"] >= 10)
    
    def _check_performance_test_capability(self) -> bool:
        """检查性能测试能力"""
        return (self.system_resources["memory_gb"] >= 8 and
                self.system_resources["cpu_cores"] >= 4)
    
    def _check_security_test_capability(self) -> bool:
        """检查安全测试能力"""
        # 检查是否有必要的安全测试工具
        return True  # 基础安全测试能力
    
    def _load_framework_config(self) -> Dict[str, Any]:
        """加载测试框架配置"""
        config_paths = [
            Path(__file__).parent / "test_framework_config.yaml",
            Path(__file__).parent / "end_to_end" / "configs" / "e2e_config.yaml"
        ]
        
        config = {}
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            config.update(file_config)
                except Exception as e:
                    print(f"警告: 无法加载配置文件 {config_path}: {e}")
        
        return config
    
    def _validate_platform(self, platform_req: Dict[str, List[str]]) -> Dict[str, Any]:
        """验证平台要求"""
        required_platforms = platform_req.get("required_platforms", [])
        excluded_platforms = platform_req.get("excluded_platforms", [])
        preferred_platforms = platform_req.get("preferred_platforms", [])
        
        recommendations = []
        
        # 检查是否在排除列表中
        if self.current_platform in excluded_platforms:
            recommendations.append(f"请在以下平台运行: {required_platforms or preferred_platforms}")
            return {
                "valid": False,
                "reason": f"当前平台 {self.current_platform} 在排除列表中",
                "recommendations": recommendations
            }
        
        # 检查是否满足必需平台要求
        if required_platforms and self.current_platform not in required_platforms:
            recommendations.append(f"请切换到支持的平台: {required_platforms}")
            return {
                "valid": False,
                "reason": f"当前平台 {self.current_platform} 不在必需平台列表中: {required_platforms}",
                "recommendations": recommendations
            }
        
        # 检查是否为首选平台
        if preferred_platforms and self.current_platform not in preferred_platforms:
            recommendations.append(f"建议使用首选平台以获得最佳性能: {preferred_platforms}")
        
        return {
            "valid": True, 
            "reason": "平台要求满足",
            "current_platform": self.current_platform,
            "recommendations": recommendations
        }
    
    def _validate_resources(self, resource_req: Dict[str, Any]) -> Dict[str, Any]:
        """验证资源要求"""
        min_memory = resource_req.get("min_memory_gb", 0)
        min_cpu_cores = resource_req.get("min_cpu_cores", 0)
        gpu_required = resource_req.get("gpu_required", False)
        min_disk_space = resource_req.get("min_disk_space_gb", 0)
        
        recommendations = []
        
        # 检查内存
        if self.system_resources["memory_gb"] < min_memory:
            recommendations.append(f"建议升级内存到至少 {min_memory}GB")
            return {
                "valid": False,
                "reason": f"内存不足: 需要 {min_memory}GB，当前 {self.system_resources['memory_gb']}GB",
                "recommendations": recommendations
            }
        
        # 检查CPU核心数
        if self.system_resources["cpu_cores"] < min_cpu_cores:
            recommendations.append(f"建议使用至少 {min_cpu_cores} 核心的CPU")
            return {
                "valid": False,
                "reason": f"CPU核心数不足: 需要 {min_cpu_cores}核，当前 {self.system_resources['cpu_cores']}核",
                "recommendations": recommendations
            }
        
        # 检查GPU
        if gpu_required and not self.system_resources["gpu_available"]:
            recommendations.append("安装支持的GPU驱动程序或使用带有GPU的机器")
            return {
                "valid": False,
                "reason": "需要GPU但系统中未检测到可用GPU",
                "recommendations": recommendations
            }
        
        # 检查磁盘空间
        if min_disk_space > 0 and self.system_resources["disk_free_gb"] < min_disk_space:
            recommendations.append(f"清理磁盘空间，至少需要 {min_disk_space}GB 可用空间")
            return {
                "valid": False,
                "reason": f"磁盘空间不足: 需要 {min_disk_space}GB，当前可用 {self.system_resources['disk_free_gb']}GB",
                "recommendations": recommendations
            }
        
        # 性能建议
        if self.system_resources["memory_gb"] < min_memory * 1.5:
            recommendations.append(f"建议使用 {min_memory * 1.5}GB 内存以获得更好性能")
        
        return {
            "valid": True, 
            "reason": "资源要求满足",
            "current_resources": self.system_resources,
            "recommendations": recommendations
        }
    
    def _validate_capabilities(self, capability_req: List[str]) -> Dict[str, Any]:
        """验证能力要求"""
        missing_capabilities = []
        recommendations = []
        
        for capability in capability_req:
            if capability not in self.available_capabilities:
                missing_capabilities.append(capability)
        
        if missing_capabilities:
            # 为缺失的能力提供建议
            for capability in missing_capabilities:
                if capability == "ui_test":
                    recommendations.append("确保系统有图形界面支持")
                elif capability == "ai_test":
                    recommendations.append("升级到至少8GB内存和4核CPU以支持AI测试")
                elif capability == "ios_test":
                    recommendations.append("iOS测试需要在macOS系统上运行")
                elif capability == "gpu_test":
                    recommendations.append("安装支持的GPU和驱动程序")
                else:
                    recommendations.append(f"安装支持 {capability} 的必要组件")
            
            return {
                "valid": False,
                "reason": f"缺少必需能力: {missing_capabilities}",
                "missing_capabilities": missing_capabilities,
                "recommendations": recommendations
            }
        
        return {
            "valid": True, 
            "reason": "能力要求满足",
            "available_capabilities": self.available_capabilities,
            "recommendations": recommendations
        }
    
    def _validate_environment(self, env_req: Dict[str, str]) -> Dict[str, Any]:
        """验证环境要求"""
        recommendations = []
        
        # 检查操作系统版本
        os_version_req = env_req.get("os_version", "")
        if os_version_req:
            # 这里可以添加具体的版本检查逻辑
            pass
        
        # 检查其他环境要求
        for key, value in env_req.items():
            if key not in ["os_version"]:
                # 检查特定环境要求
                if not self._check_environment_requirement(key, value):
                    recommendations.append(f"确保 {key} 满足要求: {value}")
        
        return {
            "valid": True,  # 暂时总是返回True，可以根据需要添加具体检查
            "reason": "环境要求满足",
            "current_environment": self.environment_info,
            "recommendations": recommendations
        }
    
    def _validate_dependencies(self, deps_req: List[str]) -> Dict[str, Any]:
        """验证依赖要求"""
        missing_dependencies = []
        recommendations = []
        
        for dependency in deps_req:
            if not self._check_dependency_available(dependency):
                missing_dependencies.append(dependency)
                recommendations.append(f"安装或配置依赖: {dependency}")
        
        if missing_dependencies:
            return {
                "valid": False,
                "reason": f"缺少必需依赖: {missing_dependencies}",
                "missing_dependencies": missing_dependencies,
                "recommendations": recommendations
            }
        
        return {
            "valid": True,
            "reason": "依赖要求满足",
            "recommendations": recommendations
        }
    
    def _check_environment_requirement(self, key: str, value: str) -> bool:
        """检查特定环境要求"""
        # 这里可以添加具体的环境检查逻辑
        return True
    
    def _check_dependency_available(self, dependency: str) -> bool:
        """检查依赖是否可用"""
        # 这里可以添加具体的依赖检查逻辑
        # 例如检查特定的软件包、服务或工具是否安装
        return True
    
    def generate_system_report(self) -> Dict[str, Any]:
        """生成系统报告"""
        return {
            "platform": self.current_platform,
            "system_resources": self.system_resources,
            "available_capabilities": self.available_capabilities,
            "environment_info": self.environment_info,
            "framework_config": self.framework_config,
            "timestamp": str(datetime.now())
        }

# 保持向后兼容性的别名
PreconditionValidator = EnhancedPreconditionValidator

if __name__ == "__main__":
    from datetime import datetime
    
    validator = EnhancedPreconditionValidator()
    
    print("🔍 PowerAutomation 前置条件验证器")
    print("=" * 50)
    print(f"当前平台: {validator.current_platform}")
    print(f"系统资源: {validator.system_resources}")
    print(f"可用能力: {validator.available_capabilities}")
    print(f"环境信息: {validator.environment_info}")
    
    # 测试示例前置条件
    test_preconditions = {
        "platform": {
            "required_platforms": ["windows", "macos", "linux"],
            "preferred_platforms": ["linux"],
            "excluded_platforms": []
        },
        "resources": {
            "min_memory_gb": 8,
            "min_cpu_cores": 4,
            "gpu_required": False
        },
        "capabilities": ["ui_test", "automation_test"],
        "environment": {
            "os_version": ">=10.0"
        },
        "dependencies": ["automation_engine"]
    }
    
    print("\n🧪 测试前置条件验证:")
    result = validator.validate_preconditions(test_preconditions)
    print(f"验证结果: {'✅ 通过' if result['valid'] else '❌ 失败'}")
    if not result['valid']:
        print(f"失败原因: {result['reason']}")
    if result.get('recommendations'):
        print(f"建议: {result['recommendations']}")

