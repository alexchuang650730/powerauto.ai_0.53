/**
 * 版本類型定義
 */
export enum EditionType {
    ENTERPRISE = 'enterprise',      // 🏢 企業版 - 完整六節點 + 雲側Admin UI
    PERSONAL_PRO = 'personal_pro',  // 👤 個人專業版 - 核心三節點 + 端側Admin UI
    OPENSOURCE = 'opensource'       // 🔓 開源版 - 基礎功能 + CLI only
}

/**
 * 工作流節點類型
 */
export enum WorkflowNodeType {
    REQUIREMENT_ANALYSIS = 'requirement_analysis',    // 需求分析 (企業版專用)
    ARCHITECTURE_DESIGN = 'architecture_design',     // 架構設計 (企業版專用)
    CODE_IMPLEMENTATION = 'code_implementation',      // 編碼實現 (所有版本)
    TEST_VERIFICATION = 'test_verification',          // 測試驗證 (企業版+個人專業版)
    DEPLOYMENT_RELEASE = 'deployment_release',        // 部署發布 (企業版+個人專業版)
    MONITORING_OPERATIONS = 'monitoring_operations'   // 監控運維 (企業版專用)
}

/**
 * 功能模塊類型
 */
export enum ModuleType {
    // 🏢 企業版專用模塊
    ENTERPRISE_ADMIN = 'enterpriseAdmin',
    MULTI_TENANT_MANAGER = 'multiTenantManager',
    COMPLIANCE_AUDIT = 'complianceAudit',
    CLOUD_ADMIN_UI = 'cloudAdminUI',
    ON_PREMISE_ADMIN = 'onPremiseAdmin',
    
    // 👤 個人專業版核心模塊
    AUTOMATION_FRAMEWORK = 'automationFramework',     // 自動化框架
    INTELLIGENT_INTERVENTION = 'intelligentIntervention', // 智能介入
    RELEASE_MANAGER = 'releaseManager',               // Release Manager
    PLUGIN_SYSTEM = 'pluginSystem',                   // 插件系統
    
    // 👤 個人專業版端側功能
    TERMINAL_CONTROLLER = 'terminalController',       // 終端控制
    INTERACTION_MANAGER = 'interactionManager',       // 交互管理
    SMART_ROUTING = 'smartRouting',                   // 智慧路由
    CREDITS_SYSTEM = 'creditsSystem',                 // 積分系統
    
    // 👤 個人專業版雲側服務 (無UI)
    CLOUD_SYNC_SERVICE = 'cloudSyncService',          // 雲端同步服務
    SMART_ROUTING_SERVICE = 'smartRoutingService',    // 智慧路由服務
    
    // 🔓 開源版模塊
    BASIC_AUTOMATION = 'basicAutomation',
    CLI_INTERFACE = 'cliInterface',
    
    // 通用工作流模塊
    REQUIREMENT_ANALYSIS = 'requirementAnalysis',
    ARCHITECTURE_DESIGN = 'architectureDesign',
    CODE_IMPLEMENTATION = 'codeImplementation',
    TEST_VERIFICATION = 'testVerification',
    DEPLOYMENT_RELEASE = 'deploymentRelease',
    MONITORING_OPERATIONS = 'monitoringOperations'
}

/**
 * UI配置接口
 */
export interface UIConfig {
    showCloudAdmin: boolean;           // 是否顯示雲側Admin UI
    showOnPremiseAdmin: boolean;       // 是否顯示端側Admin UI
    showAllWorkflowNodes: boolean;     // 是否顯示所有工作流節點
    showCoreWorkflowNodes?: boolean;   // 是否顯示核心工作流節點
    showEnterpriseFeatures: boolean;   // 是否顯示企業功能
    showMultiTenantManager: boolean;   // 是否顯示多租戶管理
    showCreditsSystem?: boolean;       // 是否顯示積分系統
    showSmartRouting?: boolean;        // 是否顯示智慧路由
    showBasicFeatures?: boolean;       // 是否顯示基礎功能
    maxWorkflows: number;              // 最大工作流數量 (-1 = 無限制)
    supportedEnvironments: string[];   // 支持的環境
}

/**
 * 雲側服務配置接口
 */
export interface CloudServiceConfig {
    enableCloudAdmin: boolean;         // 啟用雲側Admin UI
    enableMultiTenant?: boolean;       // 啟用多租戶
    enableAdvancedAnalytics?: boolean; // 啟用高級分析
    enableComplianceAudit?: boolean;   // 啟用合規審計
    enableCreditsSync?: boolean;       // 啟用積分同步
    enableSmartRouting?: boolean;      // 啟用智慧路由
    enableBasicAnalytics?: boolean;    // 啟用基礎分析
    enablePersonalBackup?: boolean;    // 啟用個人備份
}

/**
 * 版本功能映射
 */
export const EDITION_FEATURES = {
    [EditionType.ENTERPRISE]: {
        workflowNodes: [
            WorkflowNodeType.REQUIREMENT_ANALYSIS,
            WorkflowNodeType.ARCHITECTURE_DESIGN,
            WorkflowNodeType.CODE_IMPLEMENTATION,
            WorkflowNodeType.TEST_VERIFICATION,
            WorkflowNodeType.DEPLOYMENT_RELEASE,
            WorkflowNodeType.MONITORING_OPERATIONS
        ],
        modules: [
            ModuleType.ENTERPRISE_ADMIN,
            ModuleType.MULTI_TENANT_MANAGER,
            ModuleType.COMPLIANCE_AUDIT,
            ModuleType.CLOUD_ADMIN_UI,
            ModuleType.ON_PREMISE_ADMIN,
            ModuleType.REQUIREMENT_ANALYSIS,
            ModuleType.ARCHITECTURE_DESIGN,
            ModuleType.CODE_IMPLEMENTATION,
            ModuleType.TEST_VERIFICATION,
            ModuleType.DEPLOYMENT_RELEASE,
            ModuleType.MONITORING_OPERATIONS
        ],
        displayName: '企業版',
        description: '完整的端到端閉環企業自動化平台'
    },
    
    [EditionType.PERSONAL_PRO]: {
        workflowNodes: [
            WorkflowNodeType.CODE_IMPLEMENTATION,
            WorkflowNodeType.TEST_VERIFICATION,
            WorkflowNodeType.DEPLOYMENT_RELEASE
        ],
        modules: [
            ModuleType.AUTOMATION_FRAMEWORK,
            ModuleType.INTELLIGENT_INTERVENTION,
            ModuleType.RELEASE_MANAGER,
            ModuleType.PLUGIN_SYSTEM,
            ModuleType.TERMINAL_CONTROLLER,
            ModuleType.INTERACTION_MANAGER,
            ModuleType.SMART_ROUTING,
            ModuleType.CREDITS_SYSTEM,
            ModuleType.CODE_IMPLEMENTATION,
            ModuleType.TEST_VERIFICATION,
            ModuleType.DEPLOYMENT_RELEASE,
            // 雲側服務 (後台運行，無UI)
            ModuleType.CLOUD_SYNC_SERVICE,
            ModuleType.SMART_ROUTING_SERVICE
        ],
        displayName: '個人專業版',
        description: '專注核心開發流程的智能化開發助手'
    },
    
    [EditionType.OPENSOURCE]: {
        workflowNodes: [
            WorkflowNodeType.CODE_IMPLEMENTATION
        ],
        modules: [
            ModuleType.BASIC_AUTOMATION,
            ModuleType.CLI_INTERFACE,
            ModuleType.CODE_IMPLEMENTATION
        ],
        displayName: '開源版',
        description: '基礎的代碼自動化功能'
    }
};

/**
 * 技術架構映射
 */
export const TECHNICAL_ARCHITECTURE = {
    [EditionType.PERSONAL_PRO]: {
        coreNodes: {
            [WorkflowNodeType.CODE_IMPLEMENTATION]: {
                name: '編碼實現',
                description: 'AI編程助手，代碼自動生成',
                technology: ModuleType.AUTOMATION_FRAMEWORK,
                techName: '自動化框架'
            },
            [WorkflowNodeType.TEST_VERIFICATION]: {
                name: '測試驗證',
                description: '自動化測試，質量保障',
                technology: ModuleType.INTELLIGENT_INTERVENTION,
                techName: '智能介入'
            },
            [WorkflowNodeType.DEPLOYMENT_RELEASE]: {
                name: '部署發布',
                description: '一鍵部署，環境管理',
                technology: ModuleType.RELEASE_MANAGER,
                techName: 'Release Manager'
            }
        },
        supportingTech: {
            [ModuleType.PLUGIN_SYSTEM]: 'VS Code插件生態整合',
            [ModuleType.TERMINAL_CONTROLLER]: 'WSL/Mac終端控制',
            [ModuleType.INTERACTION_MANAGER]: '用戶數據收集管理',
            [ModuleType.SMART_ROUTING]: '端雲協同智慧路由',
            [ModuleType.CREDITS_SYSTEM]: '積分系統與參數控制'
        },
        cloudServices: {
            [ModuleType.CLOUD_SYNC_SERVICE]: '積分同步服務 (後台)',
            [ModuleType.SMART_ROUTING_SERVICE]: '端雲協同路由服務 (後台)'
        }
    }
};

