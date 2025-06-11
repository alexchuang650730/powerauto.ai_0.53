/**
 * 企業版角色權限管理系統
 */

/**
 * 企業角色類型
 */
export enum EnterpriseRole {
    SUPER_ADMIN = 'super_admin',           // 超級管理員 - 全部權限
    IT_ADMIN = 'it_admin',                 // IT管理員 - 技術管理權限
    PROJECT_MANAGER = 'project_manager',   // 項目經理 - 項目管理權限
    SENIOR_DEVELOPER = 'senior_developer', // 高級開發者 - 完整開發權限
    DEVELOPER = 'developer',               // 開發者 - 基礎開發權限
    TESTER = 'tester',                     // 測試者 - 測試相關權限
    DEVOPS_ENGINEER = 'devops_engineer',   // DevOps工程師 - 部署運維權限
    BUSINESS_ANALYST = 'business_analyst', // 業務分析師 - 需求分析權限
    VIEWER = 'viewer'                      // 查看者 - 只讀權限
}

/**
 * 權限類型
 */
export enum Permission {
    // 工作流節點權限
    REQUIREMENT_ANALYSIS_READ = 'requirement_analysis_read',
    REQUIREMENT_ANALYSIS_WRITE = 'requirement_analysis_write',
    ARCHITECTURE_DESIGN_READ = 'architecture_design_read',
    ARCHITECTURE_DESIGN_WRITE = 'architecture_design_write',
    CODE_IMPLEMENTATION_READ = 'code_implementation_read',
    CODE_IMPLEMENTATION_WRITE = 'code_implementation_write',
    TEST_VERIFICATION_READ = 'test_verification_read',
    TEST_VERIFICATION_WRITE = 'test_verification_write',
    DEPLOYMENT_RELEASE_READ = 'deployment_release_read',
    DEPLOYMENT_RELEASE_WRITE = 'deployment_release_write',
    MONITORING_OPERATIONS_READ = 'monitoring_operations_read',
    MONITORING_OPERATIONS_WRITE = 'monitoring_operations_write',

    // 系統管理權限
    USER_MANAGEMENT = 'user_management',
    ROLE_MANAGEMENT = 'role_management',
    SYSTEM_CONFIG = 'system_config',
    AUDIT_LOG_VIEW = 'audit_log_view',
    
    // 端側Admin UI控制權限
    ENDPOINT_UI_CONFIG = 'endpoint_ui_config',        // 配置端側UI
    ENDPOINT_FEATURE_CONTROL = 'endpoint_feature_control', // 控制端側功能
    ENDPOINT_MONITORING = 'endpoint_monitoring',      // 監控端側狀態
    
    // 雲側Admin功能權限
    CLOUD_ADMIN_FULL = 'cloud_admin_full',           // 雲側完整權限
    MULTI_TENANT_MANAGE = 'multi_tenant_manage',     // 多租戶管理
    COMPLIANCE_AUDIT = 'compliance_audit',           // 合規審計
    
    // 數據和分析權限
    ANALYTICS_VIEW = 'analytics_view',
    ANALYTICS_EXPORT = 'analytics_export',
    CREDITS_MANAGEMENT = 'credits_management',
    SMART_ROUTING_CONFIG = 'smart_routing_config'
}

/**
 * 角色權限映射
 */
export const ROLE_PERMISSIONS: Record<EnterpriseRole, Permission[]> = {
    [EnterpriseRole.SUPER_ADMIN]: [
        // 全部權限
        ...Object.values(Permission)
    ],

    [EnterpriseRole.IT_ADMIN]: [
        // 系統管理
        Permission.USER_MANAGEMENT,
        Permission.ROLE_MANAGEMENT,
        Permission.SYSTEM_CONFIG,
        Permission.AUDIT_LOG_VIEW,
        
        // 端側控制
        Permission.ENDPOINT_UI_CONFIG,
        Permission.ENDPOINT_FEATURE_CONTROL,
        Permission.ENDPOINT_MONITORING,
        
        // 雲側管理
        Permission.CLOUD_ADMIN_FULL,
        Permission.MULTI_TENANT_MANAGE,
        Permission.COMPLIANCE_AUDIT,
        
        // 所有工作流讀寫權限
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.REQUIREMENT_ANALYSIS_WRITE,
        Permission.ARCHITECTURE_DESIGN_READ,
        Permission.ARCHITECTURE_DESIGN_WRITE,
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.CODE_IMPLEMENTATION_WRITE,
        Permission.TEST_VERIFICATION_READ,
        Permission.TEST_VERIFICATION_WRITE,
        Permission.DEPLOYMENT_RELEASE_READ,
        Permission.DEPLOYMENT_RELEASE_WRITE,
        Permission.MONITORING_OPERATIONS_READ,
        Permission.MONITORING_OPERATIONS_WRITE,
        
        // 數據分析
        Permission.ANALYTICS_VIEW,
        Permission.ANALYTICS_EXPORT,
        Permission.CREDITS_MANAGEMENT,
        Permission.SMART_ROUTING_CONFIG
    ],

    [EnterpriseRole.PROJECT_MANAGER]: [
        // 項目管理相關
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.REQUIREMENT_ANALYSIS_WRITE,
        Permission.ARCHITECTURE_DESIGN_READ,
        Permission.ARCHITECTURE_DESIGN_WRITE,
        
        // 監控權限
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.TEST_VERIFICATION_READ,
        Permission.DEPLOYMENT_RELEASE_READ,
        Permission.MONITORING_OPERATIONS_READ,
        
        // 端側監控
        Permission.ENDPOINT_MONITORING,
        
        // 分析查看
        Permission.ANALYTICS_VIEW,
        Permission.AUDIT_LOG_VIEW
    ],

    [EnterpriseRole.SENIOR_DEVELOPER]: [
        // 完整開發流程
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.ARCHITECTURE_DESIGN_READ,
        Permission.ARCHITECTURE_DESIGN_WRITE,
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.CODE_IMPLEMENTATION_WRITE,
        Permission.TEST_VERIFICATION_READ,
        Permission.TEST_VERIFICATION_WRITE,
        Permission.DEPLOYMENT_RELEASE_READ,
        Permission.DEPLOYMENT_RELEASE_WRITE,
        
        // 端側功能控制
        Permission.ENDPOINT_FEATURE_CONTROL,
        Permission.ENDPOINT_MONITORING,
        
        // 分析查看
        Permission.ANALYTICS_VIEW
    ],

    [EnterpriseRole.DEVELOPER]: [
        // 基礎開發權限
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.CODE_IMPLEMENTATION_WRITE,
        Permission.TEST_VERIFICATION_READ,
        Permission.TEST_VERIFICATION_WRITE,
        
        // 有限的其他權限
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.ARCHITECTURE_DESIGN_READ,
        Permission.DEPLOYMENT_RELEASE_READ
    ],

    [EnterpriseRole.TESTER]: [
        // 測試相關權限
        Permission.TEST_VERIFICATION_READ,
        Permission.TEST_VERIFICATION_WRITE,
        
        // 相關讀取權限
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.DEPLOYMENT_RELEASE_READ,
        
        // 監控權限
        Permission.ENDPOINT_MONITORING,
        Permission.ANALYTICS_VIEW
    ],

    [EnterpriseRole.DEVOPS_ENGINEER]: [
        // 部署運維權限
        Permission.DEPLOYMENT_RELEASE_READ,
        Permission.DEPLOYMENT_RELEASE_WRITE,
        Permission.MONITORING_OPERATIONS_READ,
        Permission.MONITORING_OPERATIONS_WRITE,
        
        // 系統配置
        Permission.SYSTEM_CONFIG,
        Permission.ENDPOINT_UI_CONFIG,
        Permission.ENDPOINT_FEATURE_CONTROL,
        Permission.ENDPOINT_MONITORING,
        
        // 相關讀取權限
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.TEST_VERIFICATION_READ,
        Permission.ARCHITECTURE_DESIGN_READ,
        
        // 分析權限
        Permission.ANALYTICS_VIEW,
        Permission.SMART_ROUTING_CONFIG
    ],

    [EnterpriseRole.BUSINESS_ANALYST]: [
        // 需求分析權限
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.REQUIREMENT_ANALYSIS_WRITE,
        
        // 架構查看
        Permission.ARCHITECTURE_DESIGN_READ,
        
        // 監控和分析
        Permission.ENDPOINT_MONITORING,
        Permission.ANALYTICS_VIEW,
        Permission.AUDIT_LOG_VIEW
    ],

    [EnterpriseRole.VIEWER]: [
        // 只讀權限
        Permission.REQUIREMENT_ANALYSIS_READ,
        Permission.ARCHITECTURE_DESIGN_READ,
        Permission.CODE_IMPLEMENTATION_READ,
        Permission.TEST_VERIFICATION_READ,
        Permission.DEPLOYMENT_RELEASE_READ,
        Permission.MONITORING_OPERATIONS_READ,
        Permission.ANALYTICS_VIEW
    ]
};

/**
 * 端側UI配置接口
 */
export interface EndpointUIConfig {
    userId: string;
    role: EnterpriseRole;
    permissions: Permission[];
    
    // UI顯示控制
    visibleNodes: string[];           // 可見的工作流節點
    enabledFeatures: string[];        // 啟用的功能
    hiddenFeatures: string[];         // 隱藏的功能
    
    // 操作限制
    maxWorkflows: number;             // 最大工作流數量
    maxConcurrentJobs: number;        // 最大並發任務
    allowedEnvironments: string[];    // 允許的部署環境
    
    // 自定義設置
    customSettings: Record<string, any>;
    
    // 更新時間
    lastUpdated: string;
    updatedBy: string;
}

/**
 * 雲側Admin全量功能配置
 */
export interface CloudAdminFullConfig {
    // 端側功能鏡像
    endpointFunctions: {
        terminalControl: boolean;         // 終端控制
        workflowRecording: boolean;       // 工作流錄製
        intelligentIntervention: boolean; // 智能介入
        creditsSystem: boolean;           // 積分系統
        smartRouting: boolean;            // 智慧路由
        interactionManager: boolean;      // 交互管理
    };
    
    // 雲側專有功能
    cloudExclusiveFunctions: {
        multiTenantManagement: boolean;   // 多租戶管理
        globalAnalytics: boolean;         // 全局分析
        complianceAudit: boolean;         // 合規審計
        centralizedConfig: boolean;       // 中央化配置
        roleManagement: boolean;          // 角色管理
        endpointControl: boolean;         // 端側控制
    };
    
    // 管理功能
    managementFunctions: {
        userManagement: boolean;          // 用戶管理
        licenseManagement: boolean;       // 授權管理
        systemMonitoring: boolean;        // 系統監控
        backupRestore: boolean;           // 備份恢復
        securityAudit: boolean;           // 安全審計
    };
}

/**
 * 角色管理器類
 */
export class EnterpriseRoleManager {
    /**
     * 檢查用戶是否有特定權限
     */
    static hasPermission(role: EnterpriseRole, permission: Permission): boolean {
        const rolePermissions = ROLE_PERMISSIONS[role] || [];
        return rolePermissions.includes(permission);
    }

    /**
     * 獲取角色的所有權限
     */
    static getRolePermissions(role: EnterpriseRole): Permission[] {
        return ROLE_PERMISSIONS[role] || [];
    }

    /**
     * 生成端側UI配置
     */
    static generateEndpointUIConfig(
        userId: string, 
        role: EnterpriseRole, 
        customSettings?: Record<string, any>
    ): EndpointUIConfig {
        const permissions = this.getRolePermissions(role);
        
        // 根據權限確定可見節點
        const visibleNodes: string[] = [];
        if (this.hasPermission(role, Permission.REQUIREMENT_ANALYSIS_READ)) {
            visibleNodes.push('requirement_analysis');
        }
        if (this.hasPermission(role, Permission.ARCHITECTURE_DESIGN_READ)) {
            visibleNodes.push('architecture_design');
        }
        if (this.hasPermission(role, Permission.CODE_IMPLEMENTATION_READ)) {
            visibleNodes.push('code_implementation');
        }
        if (this.hasPermission(role, Permission.TEST_VERIFICATION_READ)) {
            visibleNodes.push('test_verification');
        }
        if (this.hasPermission(role, Permission.DEPLOYMENT_RELEASE_READ)) {
            visibleNodes.push('deployment_release');
        }
        if (this.hasPermission(role, Permission.MONITORING_OPERATIONS_READ)) {
            visibleNodes.push('monitoring_operations');
        }

        // 根據權限確定啟用功能
        const enabledFeatures: string[] = [];
        if (this.hasPermission(role, Permission.ENDPOINT_UI_CONFIG)) {
            enabledFeatures.push('ui_config');
        }
        if (this.hasPermission(role, Permission.ENDPOINT_FEATURE_CONTROL)) {
            enabledFeatures.push('feature_control');
        }
        if (this.hasPermission(role, Permission.ANALYTICS_VIEW)) {
            enabledFeatures.push('analytics');
        }
        if (this.hasPermission(role, Permission.CREDITS_MANAGEMENT)) {
            enabledFeatures.push('credits_management');
        }

        // 設置操作限制
        const limits = this.getRoleLimits(role);

        return {
            userId,
            role,
            permissions,
            visibleNodes,
            enabledFeatures,
            hiddenFeatures: [],
            maxWorkflows: limits.maxWorkflows,
            maxConcurrentJobs: limits.maxConcurrentJobs,
            allowedEnvironments: limits.allowedEnvironments,
            customSettings: customSettings || {},
            lastUpdated: new Date().toISOString(),
            updatedBy: 'system'
        };
    }

    /**
     * 獲取角色限制
     */
    private static getRoleLimits(role: EnterpriseRole): {
        maxWorkflows: number;
        maxConcurrentJobs: number;
        allowedEnvironments: string[];
    } {
        const limits = {
            [EnterpriseRole.SUPER_ADMIN]: {
                maxWorkflows: -1,
                maxConcurrentJobs: -1,
                allowedEnvironments: ['development', 'staging', 'production', 'enterprise']
            },
            [EnterpriseRole.IT_ADMIN]: {
                maxWorkflows: -1,
                maxConcurrentJobs: 20,
                allowedEnvironments: ['development', 'staging', 'production', 'enterprise']
            },
            [EnterpriseRole.PROJECT_MANAGER]: {
                maxWorkflows: 50,
                maxConcurrentJobs: 10,
                allowedEnvironments: ['development', 'staging', 'production']
            },
            [EnterpriseRole.SENIOR_DEVELOPER]: {
                maxWorkflows: 30,
                maxConcurrentJobs: 8,
                allowedEnvironments: ['development', 'staging', 'production']
            },
            [EnterpriseRole.DEVELOPER]: {
                maxWorkflows: 15,
                maxConcurrentJobs: 5,
                allowedEnvironments: ['development', 'staging']
            },
            [EnterpriseRole.TESTER]: {
                maxWorkflows: 20,
                maxConcurrentJobs: 6,
                allowedEnvironments: ['development', 'staging']
            },
            [EnterpriseRole.DEVOPS_ENGINEER]: {
                maxWorkflows: 25,
                maxConcurrentJobs: 10,
                allowedEnvironments: ['development', 'staging', 'production']
            },
            [EnterpriseRole.BUSINESS_ANALYST]: {
                maxWorkflows: 10,
                maxConcurrentJobs: 3,
                allowedEnvironments: ['development']
            },
            [EnterpriseRole.VIEWER]: {
                maxWorkflows: 0,
                maxConcurrentJobs: 0,
                allowedEnvironments: []
            }
        };

        return limits[role] || limits[EnterpriseRole.VIEWER];
    }

    /**
     * 驗證端側UI配置
     */
    static validateEndpointConfig(config: EndpointUIConfig): boolean {
        // 驗證權限一致性
        const expectedPermissions = this.getRolePermissions(config.role);
        const hasValidPermissions = config.permissions.every(p => expectedPermissions.includes(p));
        
        // 驗證限制
        const limits = this.getRoleLimits(config.role);
        const hasValidLimits = (
            (limits.maxWorkflows === -1 || config.maxWorkflows <= limits.maxWorkflows) &&
            (limits.maxConcurrentJobs === -1 || config.maxConcurrentJobs <= limits.maxConcurrentJobs) &&
            config.allowedEnvironments.every(env => limits.allowedEnvironments.includes(env))
        );

        return hasValidPermissions && hasValidLimits;
    }
}

