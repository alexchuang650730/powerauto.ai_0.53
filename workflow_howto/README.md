# Workflow HowTo 目录说明

## 📋 目录概述

这个目录包含PowerAutomation MCP架构的完整设计文档和开发指南。**所有开发者在进行MCP相关开发前必须阅读这些文档。**

## ⚠️ 重要提醒

**在开始任何开发工作之前，请务必先阅读 `MANDATORY_DEVELOPMENT_PRINCIPLES.md`**

## 📁 文档结构

### **🚨 强制性文档 (必读)**

#### **`MANDATORY_DEVELOPMENT_PRINCIPLES.md`**
- **系统稳定性保护原则**
- **禁止直接修改现有MCPCoordinator**
- **强制性开发检查清单**
- **紧急回滚程序**
- ⚠️ **违反这些原则将导致生产系统故障**

### **🏗️ 架构设计文档**

#### **`mcp_coordinator_incremental_extension.md`**
- MCPCoordinator增量式扩展设计
- 零影响扩展原则
- 向后兼容性保证
- 渐进式迁移策略

#### **`mcp_coordinator_interaction_management.md`**
- 交互数据管理架构
- MCP注册和通信协议
- InteractionLogManager设计
- 隐私和安全保护

#### **`mcp_reuse_strategy.md`**
- MCP最大化复用策略
- Adapter层复用设计
- 投资回报最大化
- 复用场景矩阵

### **🔧 开发指南文档**

#### **`workflow_design_guide.md`**
- Workflow设计原则
- 标准化目录结构
- 配置文件规范
- BaseWorkflow基础类
- 测试框架和开发检查清单

### **📊 分析文档**

#### **`howto/architecture_design_analysis.md`**
- 深度架构分析
- 设计决策说明
- 技术选型理由

## 🔄 开发流程

### **新开发者入门流程**
1. **必读**: `MANDATORY_DEVELOPMENT_PRINCIPLES.md`
2. **理解架构**: `mcp_coordinator_incremental_extension.md`
3. **学习设计**: `mcp_reuse_strategy.md`
4. **掌握开发**: `workflow_design_guide.md`
5. **开始开发**: 遵循增量式扩展原则

### **新功能开发流程**
1. **设计审查**: 在此目录创建设计文档
2. **架构确认**: 确保符合增量式扩展原则
3. **实现开发**: 创建扩展模块，不修改现有代码
4. **测试验证**: 通过所有兼容性测试
5. **文档更新**: 更新相关设计文档
6. **代码审查**: 获得批准后部署

## 🛡️ 安全检查

### **代码提交前检查清单**
- [ ] 是否阅读了 `MANDATORY_DEVELOPMENT_PRINCIPLES.md`？
- [ ] 是否遵循了增量式扩展原则？
- [ ] 是否保持了向后兼容性？
- [ ] 是否通过了所有回归测试？
- [ ] 是否更新了相关文档？

### **紧急情况处理**
如果发现系统问题，请立即参考 `MANDATORY_DEVELOPMENT_PRINCIPLES.md` 中的紧急回滚程序。

## 📞 联系方式

### **如果有疑问**
- **架构问题**: 参考架构设计文档
- **开发问题**: 参考开发指南文档
- **紧急问题**: 联系系统架构师

## 🔄 文档维护

### **文档更新原则**
- 任何架构变更都必须更新相关文档
- 新功能必须提供完整的设计文档
- 文档变更必须经过审查

### **版本控制**
- 所有文档变更都通过Git进行版本控制
- 重要变更必须在commit message中说明
- 定期备份重要设计文档

---

## ⚠️ 最终提醒

**这些文档不仅仅是参考资料，而是确保PowerAutomation系统稳定运行的关键保障。请认真阅读并严格遵守其中的原则和指南。**

**记住：我们的首要责任是确保现有服务的持续可用性！**

