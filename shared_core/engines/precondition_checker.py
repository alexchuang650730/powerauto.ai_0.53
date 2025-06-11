#!/usr/bin/env python3
"""
PowerAutomation 前置條件檢查模組 - 極簡版
遵循"最小前置，最大進化"設計理念

作者: PowerAutomation團隊
版本: 0.576
日期: 2025-06-11
"""

import asyncio
import json
import time
import logging
import platform
import os
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """平台類型枚舉"""
    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"
    UNKNOWN = "unknown"

class CheckStatus(Enum):
    """檢查狀態枚舉"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class CheckResult:
    """檢查結果數據類"""
    status: CheckStatus
    message: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class PreconditionChecker:
    """
    前置條件檢查模組 - 極簡版
    
    遵循"最小前置，最大進化"設計理念:
    1. 僅針對測試驗證意圖進行前置條件檢查
    2. 最小化必要檢查項目
    3. 提供清晰的錯誤反饋
    4. 支持從失敗中學習
    5. 與分布式協調器集成
    """
    
    def __init__(self):
        """初始化前置條件檢查器"""
        self.learning_db_path = Path.home() / ".powerauto" / "learning" / "precondition_checks.json"
        self.template_dir = Path.home() / ".powerauto" / "templates" / "test_cases"
        
        # 確保學習數據目錄存在
        os.makedirs(self.learning_db_path.parent, exist_ok=True)
        
        # 確保模板目錄存在
        os.makedirs(self.template_dir, exist_ok=True)
        
        logger.info("前置條件檢查模組初始化完成")
    
    async def should_check_preconditions(self, request: Dict[str, Any]) -> bool:
        """
        判斷是否應該進行前置條件檢查
        
        僅針對測試驗證意圖進行檢查，其他意圖直接跳過
        """
        intention = request.get('intention', '').lower()
        return intention == 'testing_verification'
    
    async def check_all_preconditions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        檢查所有前置條件
        
        僅針對測試驗證意圖進行檢查，其他意圖直接返回跳過
        """
        # 檢查是否需要進行前置條件檢查
        should_check = await self.should_check_preconditions(request)
        if not should_check:
            return {
                'overall_status': CheckStatus.SKIPPED,
                'message': "非測試驗證意圖，跳過前置條件檢查",
                'passed_checks': [],
                'warning_checks': [],
                'failed_checks': [],
                'skipped': True
            }
        
        # 執行所有檢查
        results = {}
        passed_checks = []
        warning_checks = []
        failed_checks = []
        
        # 1. 檢查請求格式
        results['request_format'] = await self.check_request_format(request)
        
        # 2. 檢查平台兼容性
        results['platform_compatibility'] = await self.check_platform_compatibility(request)
        
        # 3. 檢查模板可用性
        results['template_availability'] = await self.check_template_availability(request)
        
        # 4. 檢查環境準備
        results['environment'] = await self.check_environment(request)
        
        # 5. 檢查分布式協調器
        results['distributed_coordinator'] = await self.check_distributed_coordinator(request)
        
        # 6. 檢查插件智能介入
        results['plugin_intervention'] = await self.check_plugin_intervention(request)
        
        # 7. 檢查Gaia兼容性
        results['gaia_compatibility'] = await self.check_gaia_compatibility(request)
        
        # 8. 檢查雲環境
        results['cloud_environment'] = await self.check_cloud_environment(request)
        
        # 9. 檢查學習進度
        results['learning_progress'] = await self.check_learning_progress(request)
        
        # 分類結果
        for key, result in results.items():
            if result.status == CheckStatus.PASSED:
                passed_checks.append(key)
            elif result.status == CheckStatus.WARNING:
                warning_checks.append(key)
            elif result.status == CheckStatus.FAILED:
                failed_checks.append(key)
        
        # 確定整體狀態
        overall_status = CheckStatus.PASSED
        if len(failed_checks) > 0:
            overall_status = CheckStatus.FAILED
        elif len(warning_checks) > 0:
            overall_status = CheckStatus.WARNING
        
        # 記錄學習數據
        await self._record_check_results(request, results, overall_status)
        
        return {
            'overall_status': overall_status,
            'message': f"前置條件檢查完成: {len(passed_checks)}通過, {len(warning_checks)}警告, {len(failed_checks)}失敗",
            'results': results,
            'passed_checks': passed_checks,
            'warning_checks': warning_checks,
            'failed_checks': failed_checks,
            'skipped': False
        }
    
    async def check_request_format(self, request: Dict[str, Any]) -> CheckResult:
        """檢查請求格式"""
        # 檢查必要字段
        required_fields = ['intention', 'content']
        missing_fields = [field for field in required_fields if field not in request]
        
        if missing_fields:
            return CheckResult(
                status=CheckStatus.FAILED,
                message=f"請求缺少必要字段: {', '.join(missing_fields)}",
                details={
                    'missing_fields': missing_fields,
                    'suggestion': "請確保請求包含intention和content字段"
                }
            )
        
        # 檢查context字段
        if 'context' not in request:
            return CheckResult(
                status=CheckStatus.WARNING,
                message="請求缺少context字段，將使用默認上下文",
                details={
                    'suggestion': "添加context字段可以提供更多上下文信息",
                    'default_context_used': True
                }
            )
        
        return CheckResult(
            status=CheckStatus.PASSED,
            message="請求格式正確",
            details={
                'fields_present': list(request.keys())
            }
        )
    
    async def check_platform_compatibility(self, request: Dict[str, Any]) -> CheckResult:
        """檢查平台兼容性"""
        platform_type = await self._detect_platform()
        
        # 所有平台都支持，但提供不同的詳細信息
        if platform_type == PlatformType.WINDOWS:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="Windows平台兼容性檢查通過",
                details={
                    'platform': 'Windows',
                    'supports_distributed_testing': True,
                    'supports_gui_testing': True
                }
            )
        elif platform_type == PlatformType.MAC:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="Mac平台兼容性檢查通過",
                details={
                    'platform': 'macOS',
                    'supports_distributed_testing': True,
                    'supports_gui_testing': True
                }
            )
        elif platform_type == PlatformType.LINUX:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="Linux平台兼容性檢查通過",
                details={
                    'platform': 'Linux',
                    'supports_distributed_testing': True,
                    'supports_gui_testing': 'X11' in os.environ.get('DISPLAY', '')
                }
            )
        else:
            return CheckResult(
                status=CheckStatus.WARNING,
                message="未知平台，部分功能可能不可用",
                details={
                    'platform': 'Unknown',
                    'supports_distributed_testing': False,
                    'supports_gui_testing': False,
                    'suggestion': "請在Windows、Mac或Linux平台上運行以獲得完整功能支持"
                }
            )
    
    async def check_template_availability(self, request: Dict[str, Any]) -> CheckResult:
        """檢查模板可用性"""
        # 從請求中獲取測試類型
        context = request.get('context', {})
        test_type = context.get('test_type', 'unit_test')
        
        # 檢查模板是否存在
        template_exists = await self._check_template_exists(test_type)
        
        if template_exists:
            return CheckResult(
                status=CheckStatus.PASSED,
                message=f"{test_type}模板可用",
                details={
                    'template_type': test_type,
                    'template_path': str(self.template_dir / f"{test_type}_template.py")
                }
            )
        
        # 檢查是否可以創建模板
        can_create = await self._can_create_template(test_type)
        
        if can_create:
            return CheckResult(
                status=CheckStatus.WARNING,
                message=f"{test_type}模板不存在，但可以自動創建",
                details={
                    'template_type': test_type,
                    'can_create_template': True,
                    'suggestion': f"將自動創建{test_type}模板"
                }
            )
        
        return CheckResult(
            status=CheckStatus.FAILED,
            message=f"{test_type}模板不存在且無法創建",
            details={
                'template_type': test_type,
                'can_create_template': False,
                'suggestion': f"請手動創建{test_type}模板或選擇其他測試類型"
            }
        )
    
    async def check_environment(self, request: Dict[str, Any]) -> CheckResult:
        """檢查環境準備"""
        # 從請求中獲取測試類型
        context = request.get('context', {})
        test_type = context.get('test_type', 'unit_test')
        
        # 檢查環境準備情況
        is_ready, details = await self._check_environment_readiness(test_type)
        
        if is_ready:
            return CheckResult(
                status=CheckStatus.PASSED,
                message=f"{test_type}環境準備就緒",
                details=details
            )
        
        # 環境不完全就緒，但可以繼續
        return CheckResult(
            status=CheckStatus.WARNING,
            message=f"{test_type}環境不完全就緒，但可以繼續",
            details={
                **details,
                'suggestion': "可以繼續，但某些功能可能受限"
            }
        )
    
    async def check_distributed_coordinator(self, request: Dict[str, Any]) -> CheckResult:
        """檢查分布式協調器"""
        # 檢查是否需要分布式協調器
        coordinator_required = await self._is_coordinator_required(request)
        
        if not coordinator_required:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="不需要分布式協調器",
                details={
                    'coordinator_required': False
                }
            )
        
        # 檢查分布式協調器狀態
        try:
            # 導入分布式協調器
            from shared_core.engines.distributed_coordinator.distributed_coordinator import (
                DistributedCoordinator, CoordinatorStatus
            )
            
            # 初始化協調器
            coordinator = DistributedCoordinator()
            status = await coordinator.get_status()
            
            if status == CoordinatorStatus.RUNNING:
                return CheckResult(
                    status=CheckStatus.PASSED,
                    message="分布式協調器運行中",
                    details={
                        'coordinator_status': status.value,
                        'coordinator_required': True
                    }
                )
            elif status == CoordinatorStatus.STARTING:
                return CheckResult(
                    status=CheckStatus.WARNING,
                    message="分布式協調器正在啟動",
                    details={
                        'coordinator_status': status.value,
                        'coordinator_required': True,
                        'suggestion': "請稍等片刻，協調器正在啟動"
                    }
                )
            else:
                return CheckResult(
                    status=CheckStatus.WARNING,
                    message=f"分布式協調器狀態異常: {status.value}",
                    details={
                        'coordinator_status': status.value,
                        'coordinator_required': True,
                        'suggestion': "將嘗試在本地執行，部分功能可能受限"
                    }
                )
                
        except ImportError:
            return CheckResult(
                status=CheckStatus.WARNING,
                message="分布式協調器模塊不可用",
                details={
                    'coordinator_required': True,
                    'suggestion': "將嘗試在本地執行，部分功能可能受限"
                }
            )
        except Exception as e:
            return CheckResult(
                status=CheckStatus.WARNING,
                message=f"檢查分布式協調器時出錯: {str(e)}",
                details={
                    'coordinator_required': True,
                    'error': str(e),
                    'suggestion': "將嘗試在本地執行，部分功能可能受限"
                }
            )
    
    async def check_plugin_intervention(self, request: Dict[str, Any]) -> CheckResult:
        """檢查插件智能介入"""
        # 檢查是否需要智能介入
        needs_intervention = await self._needs_intervention(request)
        
        if not needs_intervention:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="不需要插件智能介入",
                details={
                    'intervention_triggered': False
                }
            )
        
        # 需要智能介入
        return CheckResult(
            status=CheckStatus.WARNING,
            message="觸發插件智能介入",
            details={
                'intervention_triggered': True,
                'intervention_type': 'quality_enhancement',
                'suggestion': "插件將自動介入優化測試用例生成"
            }
        )
    
    async def check_gaia_compatibility(self, request: Dict[str, Any]) -> CheckResult:
        """檢查Gaia兼容性"""
        # 檢查是否為Gaia環境
        is_gaia = await self._is_gaia_environment()
        
        if is_gaia:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="Gaia兼容性檢查通過",
                details={
                    'gaia_compatible': True,
                    'gaia_version': os.environ.get('GAIA_VERSION', 'unknown')
                }
            )
        
        # 非Gaia環境，但仍然兼容
        return CheckResult(
            status=CheckStatus.PASSED,
            message="非Gaia環境，但兼容",
            details={
                'gaia_compatible': True,
                'is_gaia_environment': False
            }
        )
    
    async def check_cloud_environment(self, request: Dict[str, Any]) -> CheckResult:
        """檢查雲環境"""
        # 檢查是否為Amazon環境
        is_amazon = await self._is_amazon_environment()
        
        if is_amazon:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="Amazon環境檢查通過",
                details={
                    'environment': 'amazon',
                    'distributed_testing_supported': True,
                    'cloud_resources_available': True
                }
            )
        
        # 非雲環境
        return CheckResult(
            status=CheckStatus.PASSED,
            message="本地環境檢查通過",
            details={
                'environment': 'local',
                'distributed_testing_supported': False,
                'suggestion': "在Amazon環境中可獲得分布式測試支持"
            }
        )
    
    async def check_learning_progress(self, request: Dict[str, Any]) -> CheckResult:
        """檢查學習進度"""
        # 獲取學習記錄
        learning_record = await self._get_learning_record()
        
        if not learning_record:
            return CheckResult(
                status=CheckStatus.PASSED,
                message="首次執行，尚無學習記錄",
                details={
                    'first_run': True
                }
            )
        
        # 分析學習進度
        improvement_rate = learning_record.get('improvement_rate', 0)
        learned_patterns = learning_record.get('learned_patterns', [])
        
        return CheckResult(
            status=CheckStatus.PASSED,
            message=f"學習進度良好，改進率: {improvement_rate:.2f}",
            details={
                'improvement_rate': improvement_rate,
                'learned_patterns': learned_patterns,
                'learning_sessions': learning_record.get('learning_sessions', 0)
            }
        )
    
    async def _detect_platform(self) -> PlatformType:
        """檢測平台類型"""
        system = platform.system().lower()
        
        if 'windows' in system:
            return PlatformType.WINDOWS
        elif 'darwin' in system:
            return PlatformType.MAC
        elif 'linux' in system:
            return PlatformType.LINUX
        else:
            return PlatformType.UNKNOWN
    
    async def _check_template_exists(self, test_type: str) -> bool:
        """檢查模板是否存在"""
        template_path = self.template_dir / f"{test_type}_template.py"
        return template_path.exists()
    
    async def _can_create_template(self, test_type: str) -> bool:
        """檢查是否可以創建模板"""
        # 檢查是否有寫入權限
        try:
            if not self.template_dir.exists():
                os.makedirs(self.template_dir, exist_ok=True)
            
            # 嘗試創建臨時文件
            temp_file = self.template_dir / f"temp_{int(time.time())}.txt"
            with open(temp_file, 'w') as f:
                f.write("test")
            
            # 刪除臨時文件
            os.remove(temp_file)
            
            return True
        except Exception:
            return False
    
    async def _check_environment_readiness(self, test_type: str) -> Tuple[bool, Dict[str, Any]]:
        """檢查環境準備情況"""
        details = {
            'test_type': test_type,
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
        
        # 檢查Python版本
        python_version = tuple(map(int, platform.python_version().split('.')))
        if python_version < (3, 8):
            details['python_version_compatible'] = False
            details['suggestion'] = "建議使用Python 3.8或更高版本"
            return False, details
        
        details['python_version_compatible'] = True
        
        # 檢查測試框架
        if test_type == 'unit_test':
            try:
                import unittest
                details['unittest_available'] = True
            except ImportError:
                details['unittest_available'] = False
                details['suggestion'] = "unittest模塊不可用"
                return False, details
        elif test_type == 'pytest':
            try:
                import pytest
                details['pytest_available'] = True
            except ImportError:
                details['pytest_available'] = False
                details['suggestion'] = "pytest模塊不可用，請安裝: pip install pytest"
                return False, details
        
        return True, details
    
    async def _is_coordinator_required(self, request: Dict[str, Any]) -> bool:
        """檢查是否需要分布式協調器"""
        context = request.get('context', {})
        test_scale = context.get('test_scale', 'small')
        distributed = context.get('distributed', False)
        
        # 大規模測試或明確要求分布式
        return test_scale in ['large', 'very_large'] or distributed
    
    async def _needs_intervention(self, request: Dict[str, Any]) -> bool:
        """檢查是否需要智能介入"""
        context = request.get('context', {})
        content = request.get('content', '')
        
        # 檢查是否明確要求介入
        if context.get('intervention', False):
            return True
        
        # 檢查內容是否需要介入
        intervention_triggers = [
            'complex',
            'difficult',
            'help',
            'optimize',
            'improve'
        ]
        
        for trigger in intervention_triggers:
            if trigger in content.lower():
                return True
        
        return False
    
    async def _is_gaia_environment(self) -> bool:
        """檢查是否為Gaia環境"""
        return 'GAIA_VERSION' in os.environ
    
    async def _is_amazon_environment(self) -> bool:
        """檢查是否為Amazon環境"""
        # 檢查是否在EC2上運行
        try:
            # 嘗試訪問EC2元數據服務
            import urllib.request
            req = urllib.request.Request(
                "http://169.254.169.254/latest/meta-data/instance-id",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
            )
            urllib.request.urlopen(req, timeout=0.1)
            return True
        except Exception:
            return False
    
    async def _get_learning_record(self) -> Dict[str, Any]:
        """獲取學習記錄"""
        if not self.learning_db_path.exists():
            return {}
        
        try:
            with open(self.learning_db_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    async def _record_check_results(self, request: Dict[str, Any], 
                                  results: Dict[str, CheckResult],
                                  overall_status: CheckStatus) -> None:
        """記錄檢查結果用於學習"""
        try:
            # 獲取現有記錄
            learning_record = await self._get_learning_record()
            
            # 更新學習記錄
            if not learning_record:
                learning_record = {
                    'learning_sessions': 1,
                    'improvement_rate': 0.0,
                    'learned_patterns': [],
                    'history': []
                }
            else:
                learning_record['learning_sessions'] += 1
            
            # 記錄本次檢查
            check_record = {
                'timestamp': datetime.now().isoformat(),
                'request_type': request.get('intention', ''),
                'overall_status': overall_status.value,
                'passed_checks': [k for k, v in results.items() if v.status == CheckStatus.PASSED],
                'warning_checks': [k for k, v in results.items() if v.status == CheckStatus.WARNING],
                'failed_checks': [k for k, v in results.items() if v.status == CheckStatus.FAILED]
            }
            
            # 添加到歷史記錄
            learning_record['history'].append(check_record)
            
            # 保持最近100條記錄
            if len(learning_record['history']) > 100:
                learning_record['history'] = learning_record['history'][-100:]
            
            # 計算改進率
            if len(learning_record['history']) >= 2:
                recent_history = learning_record['history'][-10:]
                
                # 計算失敗率變化
                old_failure_rate = sum(1 for r in learning_record['history'][:-10] 
                                    if r['overall_status'] == 'failed') / max(1, len(learning_record['history'][:-10]))
                
                new_failure_rate = sum(1 for r in recent_history 
                                    if r['overall_status'] == 'failed') / len(recent_history)
                
                # 改進率 = 失敗率降低的百分比
                if old_failure_rate > 0:
                    improvement = (old_failure_rate - new_failure_rate) / old_failure_rate
                    learning_record['improvement_rate'] = max(0, min(1, improvement))
            
            # 保存學習記錄
            with open(self.learning_db_path, 'w') as f:
                json.dump(learning_record, f, indent=2)
                
        except Exception as e:
            logger.error(f"記錄學習數據失敗: {e}")

# 測試函數
async def test_precondition_checker():
    """測試前置條件檢查器"""
    print("🧪 測試前置條件檢查器")
    print("=" * 60)
    
    checker = PreconditionChecker()
    
    # 測試請求
    test_request = {
        'intention': 'testing_verification',
        'content': '測試用例生成',
        'context': {
            'test_type': 'unit_test',
            'test_scale': 'small',
            'distributed': False
        }
    }
    
    # 執行檢查
    result = await checker.check_all_preconditions(test_request)
    
    print(f"整體狀態: {result['overall_status'].value}")
    print(f"通過檢查: {len(result['passed_checks'])}")
    print(f"警告檢查: {len(result['warning_checks'])}")
    print(f"失敗檢查: {len(result['failed_checks'])}")
    
    # 打印詳細結果
    print("\n📝 詳細檢查結果")
    print("-" * 40)
    
    for check_name, check_result in result['results'].items():
        status_symbol = "✅" if check_result.status == CheckStatus.PASSED else "⚠️" if check_result.status == CheckStatus.WARNING else "❌"
        print(f"{status_symbol} {check_name}: {check_result.message}")
    
    print("\n✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(test_precondition_checker())
