
# 视觉测试集成代码片段
# 添加到现有的测试框架集成器中

def integrate_visual_testing(self):
    """集成视觉测试功能"""
    print("🎨 集成视觉测试功能...")
    
    try:
        from visual_test_integrator import VisualTestIntegrator
        
        visual_integrator = VisualTestIntegrator()
        success = visual_integrator.integrate_visual_tests_to_framework()
        
        if success:
            print("✅ 视觉测试功能集成成功")
            return True
        else:
            print("❌ 视觉测试功能集成失败")
            return False
            
    except ImportError as e:
        print(f"⚠️ 视觉测试模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 视觉测试集成过程中发生错误: {e}")
        return False

def run_visual_tests(self):
    """运行视觉测试"""
    print("🎨 开始执行视觉测试...")
    
    try:
        from visual_tests.visual_test_suite import VisualTestSuite
        
        suite = VisualTestSuite()
        success = suite.run_all_visual_tests()
        
        return success
        
    except Exception as e:
        print(f"❌ 视觉测试执行失败: {e}")
        return False
