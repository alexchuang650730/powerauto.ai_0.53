#!/usr/bin/env python3
"""
PowerAutomation 增强视觉测试框架

集成Playwright视觉验证到PowerAutomation测试框架
支持自动截图、视觉回归测试、前置条件验证等功能
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

# 导入Playwright相关模块
try:
    from playwright.sync_api import sync_playwright, Page, Browser, Playwright
    from pixelmatch import pixelmatch
    from PIL import Image
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    print(f"警告: Playwright相关模块导入失败: {e}")
    PLAYWRIGHT_AVAILABLE = False

# 导入测试框架组件
sys.path.append(str(Path(__file__).parent))
from enhanced_test_preconditions import EnhancedPreconditionValidator

@dataclass
class VisualTestConfig:
    """视觉测试配置"""
    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    full_page_screenshot: bool = True
    visual_threshold: float = 0.1
    auto_update_baseline: bool = False
    screenshot_format: str = "png"
    enable_animations: bool = False

@dataclass
class VisualTestResult:
    """视觉测试结果"""
    test_name: str
    test_id: str
    passed: bool
    current_image: str
    baseline_image: str
    diff_image: Optional[str]
    mismatched_pixels: int
    total_pixels: int
    mismatch_percentage: float
    threshold: float
    error: Optional[str]
    timestamp: str
    execution_time: float

class PowerAutomationVisualTester:
    """PowerAutomation视觉测试框架"""
    
    def __init__(self, test_dir: str = None, config: VisualTestConfig = None):
        # 设置测试目录
        if test_dir:
            self.test_dir = Path(test_dir)
        else:
            self.test_dir = Path(__file__).parent / "visual_tests"
        
        # 创建子目录
        self.screenshots_dir = self.test_dir / "screenshots"
        self.baseline_dir = self.test_dir / "baseline"
        self.diff_dir = self.test_dir / "diff"
        self.reports_dir = self.test_dir / "reports"
        
        for directory in [self.screenshots_dir, self.baseline_dir, self.diff_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.config = config or VisualTestConfig()
        
        # Playwright组件
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # 测试结果
        self.test_results: List[VisualTestResult] = []
        
        # 前置条件验证器
        self.precondition_validator = EnhancedPreconditionValidator()
        
        # 检查Playwright可用性
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装或导入失败，请运行: pip install playwright && playwright install")
    
    def validate_visual_test_preconditions(self) -> Dict[str, Any]:
        """验证视觉测试前置条件"""
        preconditions = {
            "platform": {
                "required_platforms": ["windows", "macos", "linux"],
                "preferred_platforms": ["linux"],
                "excluded_platforms": []
            },
            "resources": {
                "min_memory_gb": 4,
                "min_cpu_cores": 2,
                "gpu_required": False,
                "min_disk_space_gb": 2
            },
            "capabilities": ["ui_test", "automation_test"],
            "environment": {
                "display_required": "true",
                "browser_support": "chromium"
            },
            "dependencies": ["playwright", "chromium_browser"]
        }
        
        return self.precondition_validator.validate_preconditions(preconditions)
    
    def start_browser(self) -> bool:
        """启动浏览器"""
        try:
            # 验证前置条件
            validation_result = self.validate_visual_test_preconditions()
            if not validation_result["valid"]:
                print(f"❌ 视觉测试前置条件不满足: {validation_result['reason']}")
                if validation_result.get("recommendations"):
                    print(f"建议: {validation_result['recommendations']}")
                return False
            
            self.playwright = sync_playwright().start()
            
            # 启动指定类型的浏览器
            browser_options = {
                "headless": self.config.headless,
                "args": ["--no-sandbox", "--disable-dev-shm-usage"] if self.config.headless else []
            }
            
            if self.config.browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(**browser_options)
            elif self.config.browser_type == "firefox":
                self.browser = self.playwright.firefox.launch(**browser_options)
            elif self.config.browser_type == "webkit":
                self.browser = self.playwright.webkit.launch(**browser_options)
            else:
                raise ValueError(f"不支持的浏览器类型: {self.config.browser_type}")
            
            # 创建页面并设置视口
            self.page = self.browser.new_page()
            self.page.set_viewport_size({
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            })
            
            # 禁用动画（如果配置要求）
            if not self.config.enable_animations:
                self.page.add_init_script("""
                    // 禁用CSS动画和过渡
                    const style = document.createElement('style');
                    style.textContent = `
                        *, *::before, *::after {
                            animation-duration: 0s !important;
                            animation-delay: 0s !important;
                            transition-duration: 0s !important;
                            transition-delay: 0s !important;
                        }
                    `;
                    document.head.appendChild(style);
                """)
            
            print(f"✅ {self.config.browser_type}浏览器已启动 (headless={self.config.headless})")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return False
    
    def stop_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"⚠️ 关闭浏览器时出现警告: {e}")
    
    def navigate_to(self, url: str, wait_until: str = "networkidle") -> bool:
        """导航到指定URL"""
        if not self.page:
            print("❌ 浏览器页面未初始化")
            return False
        
        try:
            print(f"🌐 导航到: {url}")
            self.page.goto(url, wait_until=wait_until, timeout=30000)
            print(f"✅ 成功导航到: {url}")
            return True
            
        except Exception as e:
            print(f"❌ 导航失败: {url} - {e}")
            return False
    
    def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """等待元素出现"""
        if not self.page:
            return False
        
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"⚠️ 等待元素超时: {selector} - {e}")
            return False
    
    def take_screenshot(self, test_name: str, test_id: str = None, 
                       element_selector: str = None) -> Optional[Path]:
        """截取当前页面或指定元素"""
        if not self.page:
            print("❌ 浏览器页面未初始化")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{test_name}_{timestamp}.{self.config.screenshot_format}"
            screenshot_path = self.screenshots_dir / screenshot_filename
            
            screenshot_options = {
                "path": screenshot_path,
                "type": self.config.screenshot_format
            }
            
            if element_selector:
                # 截取指定元素
                element = self.page.locator(element_selector)
                element.screenshot(**screenshot_options)
                print(f"📸 元素截图已保存: {screenshot_path} (元素: {element_selector})")
            else:
                # 截取整个页面
                screenshot_options["full_page"] = self.config.full_page_screenshot
                self.page.screenshot(**screenshot_options)
                print(f"📸 页面截图已保存: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            print(f"❌ 截图失败: {test_name} - {e}")
            return None
    
    def compare_visual(self, test_name: str, test_id: str, 
                      current_screenshot_path: Path,
                      update_baseline: bool = None) -> VisualTestResult:
        """执行视觉比较"""
        start_time = datetime.now()
        
        if update_baseline is None:
            update_baseline = self.config.auto_update_baseline
        
        baseline_filename = f"{test_name}_baseline.{self.config.screenshot_format}"
        baseline_path = self.baseline_dir / baseline_filename
        diff_filename = f"{test_name}_diff.{self.config.screenshot_format}"
        diff_path = self.diff_dir / diff_filename
        
        # 初始化结果
        result = VisualTestResult(
            test_name=test_name,
            test_id=test_id or test_name,
            passed=False,
            current_image=str(current_screenshot_path),
            baseline_image=str(baseline_path),
            diff_image=None,
            mismatched_pixels=0,
            total_pixels=0,
            mismatch_percentage=0.0,
            threshold=self.config.visual_threshold,
            error=None,
            timestamp=start_time.isoformat(),
            execution_time=0.0
        )
        
        try:
            # 如果基线图片不存在或需要更新
            if not baseline_path.exists() or update_baseline:
                # 复制当前截图作为基线
                import shutil
                shutil.copy2(current_screenshot_path, baseline_path)
                result.passed = True
                result.error = "基线图片已创建/更新"
                print(f"✅ 基线图片已更新: {baseline_path}")
                
            else:
                # 执行视觉比较
                result = self._perform_visual_comparison(result, current_screenshot_path, 
                                                       baseline_path, diff_path)
            
        except Exception as e:
            result.error = str(e)
            print(f"❌ 视觉比较出错: {test_name} - {e}")
        
        # 计算执行时间
        end_time = datetime.now()
        result.execution_time = (end_time - start_time).total_seconds()
        
        # 保存结果
        self.test_results.append(result)
        
        return result
    
    def _perform_visual_comparison(self, result: VisualTestResult, 
                                 current_path: Path, baseline_path: Path, 
                                 diff_path: Path) -> VisualTestResult:
        """执行实际的视觉比较"""
        try:
            # 打开图片
            img_current = Image.open(current_path).convert("RGB")
            img_baseline = Image.open(baseline_path).convert("RGB")
            
            # 检查尺寸
            if img_current.size != img_baseline.size:
                result.error = f"图片尺寸不匹配: {img_current.size} vs {img_baseline.size}"
                print(f"❌ {result.error}")
                return result
            
            # 创建差异图片
            img_diff = Image.new("RGBA", img_current.size)
            
            # 执行像素比较
            mismatched_pixels = pixelmatch(
                img_current,
                img_baseline,
                output=img_diff,
                threshold=self.config.visual_threshold,
                includeAA=True
            )
            
            total_pixels = img_current.width * img_current.height
            mismatch_percentage = (mismatched_pixels / total_pixels) * 100
            
            # 更新结果
            result.mismatched_pixels = mismatched_pixels
            result.total_pixels = total_pixels
            result.mismatch_percentage = round(mismatch_percentage, 4)
            
            # 判断是否通过
            if mismatch_percentage <= (self.config.visual_threshold * 100):
                result.passed = True
                print(f"✅ 视觉验证通过: {result.test_name} (差异: {mismatch_percentage:.2f}%)")
            else:
                # 保存差异图片
                img_diff.save(diff_path)
                result.diff_image = str(diff_path)
                print(f"❌ 视觉验证失败: {result.test_name} (差异: {mismatch_percentage:.2f}%)")
                print(f"   差异图片已保存: {diff_path}")
            
        except Exception as e:
            result.error = str(e)
            print(f"❌ 像素比较失败: {e}")
        
        return result
    
    def run_visual_test(self, test_name: str, url: str, test_id: str = None,
                       element_selector: str = None, 
                       wait_selector: str = None,
                       update_baseline: bool = None) -> VisualTestResult:
        """运行完整的视觉测试"""
        print(f"\n🧪 开始视觉测试: {test_name}")
        
        # 导航到URL
        if not self.navigate_to(url):
            return VisualTestResult(
                test_name=test_name,
                test_id=test_id or test_name,
                passed=False,
                current_image="",
                baseline_image="",
                diff_image=None,
                mismatched_pixels=0,
                total_pixels=0,
                mismatch_percentage=0.0,
                threshold=self.config.visual_threshold,
                error="导航失败",
                timestamp=datetime.now().isoformat(),
                execution_time=0.0
            )
        
        # 等待指定元素（如果有）
        if wait_selector:
            self.wait_for_element(wait_selector)
        
        # 截图
        screenshot_path = self.take_screenshot(test_name, test_id, element_selector)
        if not screenshot_path:
            return VisualTestResult(
                test_name=test_name,
                test_id=test_id or test_name,
                passed=False,
                current_image="",
                baseline_image="",
                diff_image=None,
                mismatched_pixels=0,
                total_pixels=0,
                mismatch_percentage=0.0,
                threshold=self.config.visual_threshold,
                error="截图失败",
                timestamp=datetime.now().isoformat(),
                execution_time=0.0
            )
        
        # 视觉比较
        result = self.compare_visual(test_name, test_id or test_name, 
                                   screenshot_path, update_baseline)
        
        print(f"{'✅' if result.passed else '❌'} 视觉测试完成: {test_name}")
        return result
    
    def generate_visual_report(self, report_format: str = "json") -> Path:
        """生成视觉测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 统计信息
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = sum(1 for r in self.test_results if not r.passed and not r.error)
        error_tests = sum(1 for r in self.test_results if r.error and "基线图片已创建" not in r.error)
        
        summary = {
            "report_info": {
                "generation_time": datetime.now().isoformat(),
                "test_framework": "PowerAutomation Visual Testing",
                "browser_type": self.config.browser_type,
                "visual_threshold": self.config.visual_threshold
            },
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0
            },
            "test_results": [asdict(result) for result in self.test_results]
        }
        
        if report_format.lower() == "json":
            report_filename = f"visual_test_report_{timestamp}.json"
            report_path = self.reports_dir / report_filename
            
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
        elif report_format.lower() == "html":
            report_filename = f"visual_test_report_{timestamp}.html"
            report_path = self.reports_dir / report_filename
            
            html_content = self._generate_html_report(summary)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        else:
            raise ValueError(f"不支持的报告格式: {report_format}")
        
        print(f"📊 视觉测试报告已生成: {report_path}")
        return report_path
    
    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """生成HTML格式报告"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 视觉测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #007bff; }
        .test-result { border: 1px solid #ddd; margin-bottom: 20px; border-radius: 6px; overflow: hidden; }
        .test-header { padding: 15px; background: #f8f9fa; border-bottom: 1px solid #ddd; }
        .test-content { padding: 15px; }
        .passed { border-left: 4px solid #28a745; }
        .failed { border-left: 4px solid #dc3545; }
        .error { border-left: 4px solid #ffc107; }
        .image-comparison { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 15px; }
        .image-box { text-align: center; }
        .image-box img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px; }
        .metric { background: #f8f9fa; padding: 10px; border-radius: 4px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PowerAutomation 视觉测试报告</h1>
            <p>生成时间: {generation_time}</p>
            <p>浏览器: {browser_type} | 阈值: {visual_threshold}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="number">{total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>通过测试</h3>
                <div class="number" style="color: #28a745;">{passed_tests}</div>
            </div>
            <div class="summary-card">
                <h3>失败测试</h3>
                <div class="number" style="color: #dc3545;">{failed_tests}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="number" style="color: #007bff;">{success_rate}%</div>
            </div>
        </div>
        
        <div class="test-results">
            {test_results_html}
        </div>
    </div>
</body>
</html>
        """
        
        # 生成测试结果HTML
        test_results_html = ""
        for result in summary["test_results"]:
            status_class = "passed" if result["passed"] else ("error" if result["error"] else "failed")
            status_text = "✅ 通过" if result["passed"] else ("⚠️ 错误" if result["error"] else "❌ 失败")
            
            test_results_html += f"""
            <div class="test-result {status_class}">
                <div class="test-header">
                    <h3>{result['test_name']} {status_text}</h3>
                    <p>测试ID: {result['test_id']} | 执行时间: {result['execution_time']:.2f}s</p>
                </div>
                <div class="test-content">
                    {f'<p style="color: #dc3545;">错误: {result["error"]}</p>' if result["error"] else ''}
                    <div class="metrics">
                        <div class="metric">
                            <strong>差异像素</strong><br>
                            {result['mismatched_pixels']:,}
                        </div>
                        <div class="metric">
                            <strong>总像素</strong><br>
                            {result['total_pixels']:,}
                        </div>
                        <div class="metric">
                            <strong>差异百分比</strong><br>
                            {result['mismatch_percentage']:.2f}%
                        </div>
                        <div class="metric">
                            <strong>阈值</strong><br>
                            {result['threshold'] * 100:.1f}%
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return html_template.format(
            generation_time=summary["report_info"]["generation_time"],
            browser_type=summary["report_info"]["browser_type"],
            visual_threshold=summary["report_info"]["visual_threshold"],
            total_tests=summary["test_summary"]["total_tests"],
            passed_tests=summary["test_summary"]["passed_tests"],
            failed_tests=summary["test_summary"]["failed_tests"],
            success_rate=summary["test_summary"]["success_rate"],
            test_results_html=test_results_html
        )

if __name__ == "__main__":
    # 示例使用
    config = VisualTestConfig(
        browser_type="chromium",
        headless=True,
        visual_threshold=0.1,
        auto_update_baseline=False
    )
    
    tester = PowerAutomationVisualTester(config=config)
    
    try:
        if tester.start_browser():
            # 运行示例测试
            result1 = tester.run_visual_test(
                test_name="google_homepage",
                url="https://www.google.com",
                test_id="VISUAL_001"
            )
            
            result2 = tester.run_visual_test(
                test_name="github_homepage", 
                url="https://github.com",
                test_id="VISUAL_002"
            )
            
            # 生成报告
            tester.generate_visual_report("json")
            tester.generate_visual_report("html")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        
    finally:
        tester.stop_browser()
        
    print("\n🎉 PowerAutomation视觉测试完成！")

