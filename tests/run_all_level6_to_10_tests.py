#!/usr/bin/env python3
"""
PowerAutomation 测试运行器 - 自动修复版本
"""

import os
import sys
import unittest
import importlib
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def discover_and_run_tests(level_dirs):
    """发现并运行指定层级的测试"""
    start_time = time.time()
    total_tests = 0
    success_count = 0
    failure_count = 0
    error_count = 0
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    for level_dir in level_dirs:
        level_name = os.path.basename(level_dir)
        print(f"📋 运行 {level_name.upper()} 测试...")
        
        # 检查目录是否存在
        if not os.path.exists(level_dir):
            print(f"  ⚠️ {level_name.upper()}: 目录不存在")
            continue
        
        # 递归遍历目录查找测试文件
        test_files = []
        for root, _, files in os.walk(level_dir):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        if not test_files:
            print(f"  ⚠️ {level_name.upper()}: 无测试文件")
            continue
        
        # 加载并运行测试
        level_tests = 0
        for test_file in test_files:
            # 将文件路径转换为模块路径
            rel_path = os.path.relpath(test_file, project_root)
            module_path = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            try:
                # 动态导入测试模块
                module = importlib.import_module(module_path)
                
                # 查找所有测试类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, unittest.TestCase) and attr != unittest.TestCase:
                        # 加载测试类中的所有测试方法
                        tests = unittest.defaultTestLoader.loadTestsFromTestCase(attr)
                        suite.addTest(tests)
                        level_tests += tests.countTestCases()
            except Exception as e:
                print(f"  ⚠️ 无法加载测试模块 {module_path}: {str(e)}")
        
        print(f"  📊 {level_name.upper()}: 加载了 {level_tests} 个测试")
        total_tests += level_tests
    
    if total_tests == 0:
        print("⚠️ 未找到任何测试!")
        return {
            'total': 0,
            'success': 0,
            'failure': 0,
            'error': 0,
            'duration': 0
        }
    
    # 运行测试
    print("\n🚀 开始运行测试...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # 计算结果
    success_count = total_tests - len(result.failures) - len(result.errors)
    failure_count = len(result.failures)
    error_count = len(result.errors)
    duration = time.time() - start_time
    
    return {
        'total': total_tests,
        'success': success_count,
        'failure': failure_count,
        'error': error_count,
        'duration': duration
    }

def generate_report(results, level_range, output_file):
    """生成测试报告"""
    success_rate = results['success'] / results['total'] * 100 if results['total'] > 0 else 0
    
    report = f"""# PowerAutomation Level {level_range} 测试报告

## 测试摘要

- **总测试数**: {results['total']}
- **成功**: {results['success']} ({success_rate:.1f}%)
- **失败**: {results['failure']}
- **错误**: {results['error']}
- **耗时**: {results['duration']:.2f} 秒

## 测试覆盖范围

"""
    
    # 写入报告文件
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"📄 详细报告: {output_file}")

def main():
    """主函数"""
    # 根据文件名确定要运行的测试层级
    script_name = os.path.basename(__file__)
    
    if "2_to_4" in script_name:
        level_dirs = [
            os.path.join(project_root, "level2"),
            os.path.join(project_root, "level3"),
            os.path.join(project_root, "level4")
        ]
        level_range = "2-4"
        report_file = os.path.join(project_root, "level2_to_4_test_report.md")
    elif "6_to_10" in script_name:
        level_dirs = [
            os.path.join(project_root, "level6"),
            os.path.join(project_root, "level7"),
            os.path.join(project_root, "level8"),
            os.path.join(project_root, "level9"),
            os.path.join(project_root, "level10")
        ]
        level_range = "6-10"
        report_file = os.path.join(project_root, "level6_to_10_test_report.md")
    else:
        print("❌ 无法确定要运行的测试层级!")
        return 1
    
    # 运行测试
    results = discover_and_run_tests(level_dirs)
    
    # 打印结果摘要
    print("\n" + "=" * 50)
    print(f"🎉 Level {level_range} 测试完成!")
    print("=" * 50)
    print(f"📊 总测试数: {results['total']}")
    
    if results['total'] > 0:
        success_rate = results['success'] / results['total'] * 100
        print(f"✅ 成功: {results['success']} ({success_rate:.1f}%)")
        print(f"❌ 失败: {results['failure']}")
        print(f"⚠️ 错误: {results['error']}")
        print(f"⏱️ 耗时: {results['duration']:.2f} 秒")
    else:
        print("N/A")
    
    # 生成报告
    generate_report(results, level_range, report_file)
    print("=" * 50)
    
    # 如果有失败或错误，返回非零退出码
    if results['failure'] > 0 or results['error'] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
