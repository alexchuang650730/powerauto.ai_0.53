#!/usr/bin/env python3
"""
PowerAutomation Level 1 單元測試運行器

批量運行所有Level 1單元測試，生成詳細報告
"""

import unittest
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

class Level1TestRunner:
    """Level 1 測試運行器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        
    def discover_tests(self) -> List[str]:
        """發現所有測試文件"""
        test_files = []
        for category_dir in self.test_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                for test_file in category_dir.glob('test_*.py'):
                    test_files.append(str(test_file.relative_to(self.test_dir)))
        return test_files
    
    def run_category_tests(self, category: str) -> Tuple[int, int, int]:
        """運行指定類別的測試"""
        category_dir = self.test_dir / category
        if not category_dir.exists():
            return 0, 0, 0
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        
        # 加載該類別下的所有測試
        for test_file in category_dir.glob('test_*.py'):
            module_name = f"test.level1.{category}.{test_file.stem}"
            try:
                module = __import__(module_name, fromlist=[''])
                suite.addTests(loader.loadTestsFromModule(module))
            except ImportError as e:
                print(f"⚠️ 無法加載測試模塊 {module_name}: {e}")
        
        # 運行測試
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        return result.testsRun, len(result.failures), len(result.errors)
    
    def run_all_tests(self) -> Dict[str, Tuple[int, int, int]]:
        """運行所有測試"""
        print("🚀 開始運行Level 1單元測試...")
        
        categories = [
            'mcp_adapters',
            'core_tools', 
            'data_processing',
            'routing_intelligence',
            'performance_monitoring',
            'error_handling',
            'configuration',
            'logging'
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for category in categories:
            print(f"📋 運行 {category} 測試...")
            tests, failures, errors = self.run_category_tests(category)
            self.results[category] = (tests, failures, errors)
            
            total_tests += tests
            total_failures += failures
            total_errors += errors
            
            if tests > 0:
                success_rate = ((tests - failures - errors) / tests) * 100
                print(f"  ✅ {category}: {tests}個測試, 成功率 {success_rate:.1f}%")
            else:
                print(f"  ⚠️ {category}: 無測試文件")
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures, 
            'total_errors': total_errors,
            'categories': self.results
        }
    
    def generate_report(self, results: Dict) -> str:
        """生成測試報告"""
        report = []
        report.append("# PowerAutomation Level 1 單元測試報告")
        report.append("=" * 50)
        report.append("")
        
        # 總體統計
        total_tests = results['total_tests']
        total_failures = results['total_failures']
        total_errors = results['total_errors']
        success_count = total_tests - total_failures - total_errors
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        
        report.append(f"## 總體統計")
        report.append(f"- 總測試數: {total_tests}")
        report.append(f"- 成功測試: {success_count}")
        report.append(f"- 失敗測試: {total_failures}")
        report.append(f"- 錯誤測試: {total_errors}")
        report.append(f"- 成功率: {success_rate:.2f}%")
        report.append("")
        
        # 分類統計
        report.append("## 分類統計")
        for category, (tests, failures, errors) in results['categories'].items():
            if tests > 0:
                cat_success_rate = ((tests - failures - errors) / tests) * 100
                report.append(f"### {category}")
                report.append(f"- 測試數: {tests}")
                report.append(f"- 成功率: {cat_success_rate:.1f}%")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函數"""
    runner = Level1TestRunner()
    results = runner.run_all_tests()
    
    # 生成報告
    report = runner.generate_report(results)
    
    # 保存報告
    report_path = Path(__file__).parent / "level1_test_report.md"
    report_path.write_text(report, encoding='utf-8')
    
    print("\n" + "="*50)
    print("🎉 Level 1 單元測試完成!")
    print("="*50)
    print(f"📊 總測試數: {results['total_tests']}")
    print(f"✅ 成功率: {((results['total_tests'] - results['total_failures'] - results['total_errors']) / results['total_tests'] * 100):.1f}%" if results['total_tests'] > 0 else "N/A")
    print(f"📄 詳細報告: {report_path}")
    print("="*50)

if __name__ == '__main__':
    main()
