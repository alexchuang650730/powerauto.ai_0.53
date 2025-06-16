# ⚠️ 强制性开发原则 - 系统稳定性保护

## 🚨 重要警告：违反这些原则将导致生产系统故障

### ❌ 绝对禁止的操作

#### **1. 禁止直接修改现有MCPCoordinator**
```
❌ 绝对不要修改现有的MCPCoordinator代码
❌ 绝对不要改变现有的API接口
❌ 绝对不要修改现有的路由逻辑
❌ 绝对不要改变现有的数据结构
```

#### **2. 禁止破坏向后兼容性**
```
❌ 不要删除现有的API端点
❌ 不要修改现有的请求/响应格式
❌ 不要改变现有的错误处理逻辑
❌ 不要修改现有的配置文件格式
```

#### **3. 禁止影响现有MCP**
```
❌ 不要修改现有MCP的接口
❌ 不要改变现有MCP的注册流程
❌ 不要影响现有MCP的正常运行
❌ 不要强制现有MCP使用新功能
```

### ✅ 强制要求的开发方式

#### **1. 必须使用增量式扩展**
```python
# ✅ 正确方式：创建扩展模块
class MCPCoordinatorExtensions:
    def __init__(self, coordinator: MCPCoordinator):
        self.coordinator = coordinator  # 引用现有coordinator
        # 添加新功能...

# ❌ 错误方式：直接修改现有类
class MCPCoordinator:  # 不要修改这个类！
    def __init__(self):
        # 不要在这里添加新功能！
```

#### **2. 必须保持API向后兼容**
```python
# ✅ 正确方式：添加新的API版本
@app.route('/api/v2/new_feature', methods=['POST'])
def new_feature():
    # 新功能使用新端点
    pass

# ❌ 错误方式：修改现有API
@app.route('/api/v1/existing_endpoint', methods=['POST'])
def existing_endpoint():
    # 不要修改现有端点的逻辑！
```

#### **3. 必须使用可选配置**
```toml
# ✅ 正确方式：新功能默认关闭
[extensions]
new_feature = false  # 默认关闭，不影响现有功能

# ❌ 错误方式：强制启用新功能
[extensions]
new_feature = true  # 这会影响现有系统！
```

## 🔧 安全开发检查清单

### **代码提交前必须检查**

#### **✅ 兼容性检查**
- [ ] 现有API端点是否保持不变？
- [ ] 现有请求/响应格式是否保持不变？
- [ ] 现有配置文件是否仍然有效？
- [ ] 现有MCP是否能继续正常工作？

#### **✅ 扩展性检查**
- [ ] 新功能是否作为可选扩展实现？
- [ ] 新功能是否默认关闭？
- [ ] 是否提供了回滚机制？
- [ ] 是否有完整的向后兼容测试？

#### **✅ 文档检查**
- [ ] 是否更新了相关设计文档？
- [ ] 是否说明了新功能的启用方式？
- [ ] 是否提供了迁移指南？
- [ ] 是否有回滚操作说明？

## 🧪 强制性测试要求

### **提交代码前必须通过的测试**

#### **1. 现有功能回归测试**
```bash
# 必须通过所有现有功能测试
pytest tests/existing_functionality/
pytest tests/api_compatibility/
pytest tests/mcp_compatibility/
```

#### **2. 向后兼容性测试**
```bash
# 必须通过向后兼容性测试
pytest tests/backward_compatibility/
pytest tests/api_version_compatibility/
pytest tests/config_compatibility/
```

#### **3. 扩展功能测试**
```bash
# 扩展功能必须可选启用/关闭
pytest tests/extensions/test_optional_features.py
pytest tests/extensions/test_rollback_capability.py
```

## 🚨 违规后果

### **代码审查拒绝**
- 任何违反这些原则的代码将被立即拒绝
- 必须重新设计为增量式扩展
- 必须通过所有兼容性测试

### **生产部署阻止**
- 违反原则的代码不允许部署到生产环境
- 必须提供完整的回滚计划
- 必须经过额外的安全审查

### **系统故障责任**
- 因违反原则导致的系统故障，开发者承担全部责任
- 必须立即回滚到稳定版本
- 必须提供详细的故障分析报告

## 📋 开发流程

### **新功能开发流程**

#### **步骤1: 设计审查**
1. 提交设计文档到 `workflow_howto/` 目录
2. 确保设计符合增量式扩展原则
3. 获得架构师审查批准

#### **步骤2: 实现开发**
1. 创建扩展模块，不修改现有代码
2. 实现可选配置，默认关闭新功能
3. 添加完整的向后兼容性支持

#### **步骤3: 测试验证**
1. 运行所有现有功能回归测试
2. 运行向后兼容性测试
3. 验证新功能的可选启用/关闭

#### **步骤4: 文档更新**
1. 更新 `workflow_howto/` 中的相关文档
2. 提供新功能的使用指南
3. 提供回滚操作说明

#### **步骤5: 代码审查**
1. 提交代码进行审查
2. 确保通过所有检查清单
3. 获得至少2名资深开发者的批准

#### **步骤6: 分阶段部署**
1. 先在测试环境部署（新功能关闭）
2. 验证现有功能正常
3. 逐步启用新功能进行测试
4. 最后部署到生产环境

## 🔄 紧急回滚程序

### **如果发现系统问题**

#### **立即回滚步骤**
```bash
# 1. 关闭所有扩展功能
echo "[extensions]" > /tmp/disable_extensions.toml
echo "all_extensions = false" >> /tmp/disable_extensions.toml
cp /tmp/disable_extensions.toml /path/to/config/

# 2. 重启服务
systemctl restart mcp_coordinator

# 3. 验证现有功能
curl -X POST /api/v1/health_check

# 4. 如果仍有问题，回滚代码
git revert <commit_hash>
git push origin main
```

#### **回滚验证**
- [ ] 所有现有API端点正常响应
- [ ] 所有现有MCP正常工作
- [ ] 系统性能恢复正常
- [ ] 错误日志清除

## 📞 紧急联系

### **如果遇到问题**
- **架构师**: 立即联系系统架构师
- **运维团队**: 通知运维团队准备回滚
- **测试团队**: 请求紧急回归测试
- **产品团队**: 通知产品团队可能的影响

## 📚 参考文档

### **必读文档**
- `workflow_howto/mcp_coordinator_incremental_extension.md` - 增量扩展设计
- `workflow_howto/mcp_coordinator_interaction_management.md` - 交互数据管理
- `workflow_howto/workflow_design_guide.md` - Workflow设计指南
- `workflow_howto/mcp_reuse_strategy.md` - MCP复用策略

---

## ⚠️ 最终警告

**这些原则不是建议，而是强制性要求。违反这些原则可能导致整个PowerAutomation系统的故障，影响所有用户和服务。请严格遵守这些原则，确保系统的稳定性和可靠性。**

**记住：现有的服务必须继续工作，这是我们的首要责任！**

