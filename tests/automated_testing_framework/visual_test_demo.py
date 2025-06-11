#!/usr/bin/env python3
"""
PowerAutomation 视觉测试演示

在当前环境限制下演示视觉测试功能
"""

import os
import sys
from pathlib import Path

# 添加测试框架路径
sys.path.append(str(Path(__file__).parent))
from powerautomation_visual_tester import PowerAutomationVisualTester, VisualTestConfig

def demo_visual_testing():
    """演示视觉测试功能"""
    print("🎨 PowerAutomation 视觉测试演示")
    print("=" * 50)
    
    # 创建适合当前环境的配置
    config = VisualTestConfig(
        browser_type="chromium",
        headless=True,
        viewport_width=1280,  # 降低分辨率以减少内存使用
        viewport_height=720,
        visual_threshold=0.1,
        auto_update_baseline=True,  # 首次运行自动创建基线
        enable_animations=False
    )
    
    # 创建视觉测试器
    tester = PowerAutomationVisualTester(
        test_dir="visual_tests_demo",
        config=config
    )
    
    try:
        # 尝试启动浏览器（即使前置条件不完全满足）
        print("🚀 尝试启动浏览器...")
        
        # 手动启动浏览器（跳过前置条件检查）
        from playwright.sync_api import sync_playwright
        
        tester.playwright = sync_playwright().start()
        tester.browser = tester.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        tester.page = tester.browser.new_page()
        tester.page.set_viewport_size({
            "width": config.viewport_width,
            "height": config.viewport_height
        })
        
        print("✅ 浏览器启动成功")
        
        # 演示测试场景
        test_scenarios = [
            {
                "name": "simple_page_test",
                "url": "data:text/html,<html><body><h1>PowerAutomation Test</h1><p>Visual Testing Demo</p></body></html>",
                "description": "简单页面测试"
            },
            {
                "name": "google_homepage",
                "url": "https://www.google.com",
                "description": "Google首页测试"
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"\n🧪 执行测试: {scenario['description']}")
            
            try:
                # 导航到页面
                if tester.navigate_to(scenario["url"]):
                    # 截图
                    screenshot_path = tester.take_screenshot(scenario["name"])
                    
                    if screenshot_path:
                        # 视觉比较
                        result = tester.compare_visual(
                            test_name=scenario["name"],
                            test_id=f"DEMO_{scenario['name'].upper()}",
                            current_screenshot_path=screenshot_path,
                            update_baseline=True
                        )
                        
                        results.append(result)
                        
                        if result.passed:
                            print(f"✅ {scenario['description']} 通过")
                        else:
                            print(f"❌ {scenario['description']} 失败: {result.error}")
                    else:
                        print(f"❌ {scenario['description']} 截图失败")
                else:
                    print(f"❌ {scenario['description']} 导航失败")
                    
            except Exception as e:
                print(f"❌ {scenario['description']} 执行出错: {e}")
        
        # 生成报告
        if results:
            print("\n📊 生成测试报告...")
            try:
                json_report = tester.generate_visual_report("json")
                html_report = tester.generate_visual_report("html")
                
                print(f"✅ JSON报告: {json_report}")
                print(f"✅ HTML报告: {html_report}")
                
            except Exception as e:
                print(f"⚠️ 报告生成失败: {e}")
        
        # 显示测试结果统计
        if tester.test_results:
            total_tests = len(tester.test_results)
            passed_tests = sum(1 for r in tester.test_results if r.passed)
            
            print(f"\n📈 测试统计:")
            print(f"   总测试数: {total_tests}")
            print(f"   通过测试: {passed_tests}")
            print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        
    finally:
        # 清理资源
        try:
            tester.stop_browser()
        except:
            pass
    
    print("\n🎉 视觉测试演示完成！")

def show_visual_test_capabilities():
    """展示视觉测试能力"""
    print("\n🎯 PowerAutomation 视觉测试能力:")
    print("=" * 50)
    
    capabilities = [
        "✅ 自动截图功能 - 支持全页面和元素截图",
        "✅ 视觉回归测试 - 像素级别的差异检测",
        "✅ 多浏览器支持 - Chromium、Firefox、WebKit",
        "✅ 前置条件验证 - 智能环境检查",
        "✅ 基线管理 - 自动基线创建和更新",
        "✅ 差异可视化 - 生成差异图片",
        "✅ 多格式报告 - JSON和HTML报告",
        "✅ 集成测试框架 - 与端到端测试无缝集成",
        "✅ 兜底自动化验证 - Trae、Manus、数据获取视觉验证",
        "✅ 配置灵活性 - 可调节阈值和参数"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")
    
    print("\n🔧 集成组件:")
    integration_components = [
        "📦 PowerAutomationVisualTester - 核心视觉测试引擎",
        "🔗 VisualTestIntegrator - 框架集成器",
        "🧪 VisualTestSuite - 测试套件管理器",
        "⚙️ VisualTestConfig - 配置管理",
        "📊 增强报告系统 - 详细的视觉测试报告",
        "🔍 前置条件验证 - 环境兼容性检查"
    ]
    
    for component in integration_components:
        print(f"  {component}")

if __name__ == "__main__":
    show_visual_test_capabilities()
    demo_visual_testing()

