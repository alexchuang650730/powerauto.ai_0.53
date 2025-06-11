/**
 * 個人專業版角色權限管理系統
 * 特點：雲側Admin UI存在，但實際控制權在PowerAutomation Administrator手中
 */

/**
 * 個人專業版角色類型
 */
export enum PersonalProRole {
    // PowerAutomation官方角色
    POWERAUTOMATION_ADMIN = 'powerautomation_admin',     // PowerAutomation管理員 - 完全控制權
    POWERAUTOMATION_SUPPORT = 'powerautomation_support', // PowerAutomation支持 - 技術支持權限
    
    // 用戶角色 (受限制)
    PREMIUM_USER = 'premium_user',                       // 高級用戶 - 完整功能使用權
    STANDARD_USER = 'standard_user',                     // 標準用戶 - 基礎功能使用權
    TRIAL_USER = 'trial_user',                          // 試用用戶 - 限制功能使用權
    VIEWER_USER = 'viewer_user'                         // 查看用戶 - 只讀權限
}

/**
 * 個人專業版權限類型
 */
export enum PersonalProPermission {
    // 核心工作流權限
    CODE_IMPLEMENTATION_USE = 'code_implementation_use',
    TEST_VERIFICATION_USE = 'test_verification_use',
    DEPLOYMENT_RELEASE_USE = 'deployment_release_use',
    
    // 端側功能權限
    TERMINAL_CONTROL_USE = 'terminal_control_use',
    WORKFLOW_RECORDING_USE = 'workflow_recording_use',
    INTELLIGENT_INTERVENTION_USE = 'intelligent_intervention_use',
    CREDITS_SYSTEM_VIEW = 'credits_system_view',
    SMART_ROUTING_VIEW = 'smart_routing_view',
    
    // 雲側Admin UI權限 (查看為主)
    CLOUD_ADMIN_VIEW = 'cloud_admin_view',               // 查看雲側Admin
    CLOUD_ADMIN_LIMITED_CONFIG = 'cloud_admin_limited_config', // 有限配置權限
    
    // PowerAutomation Administrator專用權限
    POWERAUTOMATION_FULL_CONTROL = 'powerautomation_full_control', // 完全控制
    USER_ROLE_MANAGEMENT = 'user_role_management',       // 用戶角色管理
    SYSTEM_CONFIGURATION = 'system_configuration',       // 系統配置
    ENDPOINT_UI_CONTROL = 'endpoint_ui_control',         // 端側UI控制
    CLOUD_SERVICE_CONTROL = 'cloud_service_control',     // 雲側服務控制
    BILLING_MANAGEMENT = 'billing_management',           // 計費管理
    
    // 數據和分析權限
    PERSONAL_ANALYTICS_VIEW = 'personal_analytics_view', // 個人分析查看
    USAGE_STATISTICS_VIEW = 'usage_statistics_view',     // 使用統計查看
    CREDITS_HISTORY_VIEW = 'credits_history_view'        // 積分歷史查看
}

/**
 * 個人專業版角色權限映射
 */
export const PERSONAL_PRO_ROLE_PERMISSIONS: Record<PersonalProRole, PersonalProPermission[]> = {
    // PowerAutomation官方管理員 - 完全控制權
    [PersonalProRole.POWERAUTOMATION_ADMIN]: [
        // 所有權限
        ...Object.values(PersonalProPermission)
    ],

    // PowerAutomation技術支持 - 技術支持權限
    [PersonalProRole.POWERAUTOMATION_SUPPORT]: [
        // 系統配置和用戶支持
        PersonalProPermission.POWERAUTOMATION_FULL_CONTROL,
        PersonalProPermission.USER_ROLE_MANAGEMENT,
        PersonalProPermission.SYSTEM_CONFIGURATION,
        PersonalProPermission.ENDPOINT_UI_CONTROL,
        PersonalProPermission.CLOUD_SERVICE_CONTROL,
        
        // 查看權限
        PersonalProPermission.CLOUD_ADMIN_VIEW,
        PersonalProPermission.PERSONAL_ANALYTICS_VIEW,
        PersonalProPermission.USAGE_STATISTICS_VIEW,
        PersonalProPermission.CREDITS_HISTORY_VIEW,
        
        // 基礎功能權限
        PersonalProPermission.CODE_IMPLEMENTATION_USE,
        PersonalProPermission.TEST_VERIFICATION_USE,
        PersonalProPermission.DEPLOYMENT_RELEASE_USE
    ],

    // 高級用戶 - 完整功能使用權
    [PersonalProRole.PREMIUM_USER]: [
        // 核心工作流
        PersonalProPermission.CODE_IMPLEMENTATION_USE,
        PersonalProPermission.TEST_VERIFICATION_USE,
        PersonalProPermission.DEPLOYMENT_RELEASE_USE,
        
        // 端側功能
        PersonalProPermission.TERMINAL_CONTROL_USE,
        PersonalProPermission.WORKFLOW_RECORDING_USE,
        PersonalProPermission.INTELLIGENT_INTERVENTION_USE,
        PersonalProPermission.CREDITS_SYSTEM_VIEW,
        PersonalProPermission.SMART_ROUTING_VIEW,
        
        // 雲側Admin查看
        PersonalProPermission.CLOUD_ADMIN_VIEW,
        PersonalProPermission.CLOUD_ADMIN_LIMITED_CONFIG, // 有限配置權限
        
        // 個人數據查看
        PersonalProPermission.PERSONAL_ANALYTICS_VIEW,
        PersonalProPermission.USAGE_STATISTICS_VIEW,
        PersonalProPermission.CREDITS_HISTORY_VIEW
    ],

    // 標準用戶 - 基礎功能使用權
    [PersonalProRole.STANDARD_USER]: [
        // 核心工作流
        PersonalProPermission.CODE_IMPLEMENTATION_USE,
        PersonalProPermission.TEST_VERIFICATION_USE,
        PersonalProPermission.DEPLOYMENT_RELEASE_USE,
        
        // 基礎端側功能
        PersonalProPermission.TERMINAL_CONTROL_USE,
        PersonalProPermission.WORKFLOW_RECORDING_USE,
        PersonalProPermission.CREDITS_SYSTEM_VIEW,
        PersonalProPermission.SMART_ROUTING_VIEW,
        
        // 雲側Admin查看 (受限)
        PersonalProPermission.CLOUD_ADMIN_VIEW,
        
        // 個人數據查看
        PersonalProPermission.PERSONAL_ANALYTICS_VIEW,
        PersonalProPermission.USAGE_STATISTICS_VIEW,
        PersonalProPermission.CREDITS_HISTORY_VIEW
    ],

    // 試用用戶 - 限制功能使用權
    [PersonalProRole.TRIAL_USER]: [
        // 基礎工作流 (受限)
        PersonalProPermission.CODE_IMPLEMENTATION_USE,
        PersonalProPermission.TEST_VERIFICATION_USE,
        
        // 基礎查看權限
        PersonalProPermission.CREDITS_SYSTEM_VIEW,
        PersonalProPermission.CLOUD_ADMIN_VIEW,
        PersonalProPermission.PERSONAL_ANALYTICS_VIEW
    ],

    // 查看用戶 - 只讀權限
    [PersonalProRole.VIEWER_USER]: [
        // 只讀權限
        PersonalProPermission.CLOUD_ADMIN_VIEW,
        PersonalProPermission.PERSONAL_ANALYTICS_VIEW,
        PersonalProPermission.CREDITS_SYSTEM_VIEW
    ]
};

/**
 * 個人專業版端側UI配置接口
 */
export interface PersonalProEndpointUIConfig {
    userId: string;
    userRole: PersonalProRole;                    // 用戶角色
    configuredBy: string;                         // 配置者 (通常是PowerAutomation Administrator)
    configuredByRole: PersonalProRole;            // 配置者角色
    permissions: PersonalProPermission[];
    
    // UI顯示控制 (由PowerAutomation Administrator設定)
    visibleNodes: string[];                       // 可見的工作流節點
    enabledFeatures: string[];                    // 啟用的功能
    hiddenFeatures: string[];                     // 隱藏的功能
    
    // 使用限制 (由PowerAutomation Administrator設定)
    maxWorkflows: number;                         // 最大工作流數量
    maxConcurrentJobs: number;                    // 最大並發任務
    allowedEnvironments: string[];                // 允許的部署環境
    creditsLimit: number;                         // 積分限制
    
    // 雲側Admin UI控制
    cloudAdminAccess: {
        canView: boolean;                         // 可以查看雲側Admin
        canConfigure: boolean;                    // 可以配置 (通常為false)
        visibleSections: string[];                // 可見的雲側Admin區域
        configurableSections: string[];           // 可配置的雲側Admin區域
    };
    
    // 配置元數據
    lastUpdated: string;
    lastUpdatedBy: string;
    configurationLocked: boolean;                 // 配置是否鎖定 (用戶無法修改)
}

/**
 * 個人專業版雲側Admin配置
 */
export interface PersonalProCloudAdminConfig {
    // 功能可見性 (用戶可見但不可配置)
    visibleToUser: {
        creditsManagement: boolean;               // 積分管理可見
        smartRoutingStatus: boolean;              // 智慧路由狀態可見
        usageAnalytics: boolean;                  // 使用分析可見
        endpointStatus: boolean;                  // 端側狀態可見
        workflowHistory: boolean;                 // 工作流歷史可見
    };
    
    // 用戶可配置項目 (有限)
    userConfigurable: {
        personalPreferences: boolean;             // 個人偏好設置
        notificationSettings: boolean;            // 通知設置
        basicWorkflowSettings: boolean;           // 基礎工作流設置
    };
    
    // PowerAutomation Administrator專用控制
    administratorControl: {
        userRoleAssignment: boolean;              // 用戶角色分配
        featureToggle: boolean;                   // 功能開關控制
        usageLimits: boolean;                     // 使用限制設定
        billingConfiguration: boolean;            // 計費配置
        systemMaintenance: boolean;               // 系統維護
    };
}

/**
 * 個人專業版角色管理器
 */
export class PersonalProRoleManager {
    /**
     * 檢查用戶是否有特定權限
     */
    static hasPermission(role: PersonalProRole, permission: PersonalProPermission): boolean {
        const rolePermissions = PERSONAL_PRO_ROLE_PERMISSIONS[role] || [];
        return rolePermissions.includes(permission);
    }

    /**
     * 檢查是否為PowerAutomation官方角色
     */
    static isPowerAutomationRole(role: PersonalProRole): boolean {
        return role === PersonalProRole.POWERAUTOMATION_ADMIN || 
               role === PersonalProRole.POWERAUTOMATION_SUPPORT;
    }

    /**
     * 生成個人專業版端側UI配置
     * 注意：只有PowerAutomation Administrator可以調用此方法
     */
    static generatePersonalProEndpointUIConfig(
        userId: string,
        userRole: PersonalProRole,
        configuredBy: string,
        configuredByRole: PersonalProRole,
        customSettings?: Record<string, any>
    ): PersonalProEndpointUIConfig | null {
        
        // 驗證配置者權限
        if (!this.hasPermission(configuredByRole, PersonalProPermission.ENDPOINT_UI_CONTROL)) {
            console.error('配置者沒有端側UI控制權限');
            return null;
        }

        const permissions = PERSONAL_PRO_ROLE_PERMISSIONS[userRole] || [];
        
        // 根據用戶角色確定可見節點
        const visibleNodes: string[] = [];
        if (this.hasPermission(userRole, PersonalProPermission.CODE_IMPLEMENTATION_USE)) {
            visibleNodes.push('code_implementation');
        }
        if (this.hasPermission(userRole, PersonalProPermission.TEST_VERIFICATION_USE)) {
            visibleNodes.push('test_verification');
        }
        if (this.hasPermission(userRole, PersonalProPermission.DEPLOYMENT_RELEASE_USE)) {
            visibleNodes.push('deployment_release');
        }

        // 根據用戶角色確定啟用功能
        const enabledFeatures: string[] = [];
        if (this.hasPermission(userRole, PersonalProPermission.TERMINAL_CONTROL_USE)) {
            enabledFeatures.push('terminal_control');
        }
        if (this.hasPermission(userRole, PersonalProPermission.WORKFLOW_RECORDING_USE)) {
            enabledFeatures.push('workflow_recording');
        }
        if (this.hasPermission(userRole, PersonalProPermission.INTELLIGENT_INTERVENTION_USE)) {
            enabledFeatures.push('intelligent_intervention');
        }
        if (this.hasPermission(userRole, PersonalProPermission.CREDITS_SYSTEM_VIEW)) {
            enabledFeatures.push('credits_system');
        }

        // 設置雲側Admin訪問權限
        const cloudAdminAccess = {
            canView: this.hasPermission(userRole, PersonalProPermission.CLOUD_ADMIN_VIEW),
            canConfigure: this.hasPermission(userRole, PersonalProPermission.CLOUD_ADMIN_LIMITED_CONFIG),
            visibleSections: this.getVisibleCloudAdminSections(userRole),
            configurableSections: this.getConfigurableCloudAdminSections(userRole)
        };

        // 設置使用限制
        const limits = this.getPersonalProRoleLimits(userRole);

        return {
            userId,
            userRole,
            configuredBy,
            configuredByRole,
            permissions,
            visibleNodes,
            enabledFeatures,
            hiddenFeatures: [],
            maxWorkflows: limits.maxWorkflows,
            maxConcurrentJobs: limits.maxConcurrentJobs,
            allowedEnvironments: limits.allowedEnvironments,
            creditsLimit: limits.creditsLimit,
            cloudAdminAccess,
            lastUpdated: new Date().toISOString(),
            lastUpdatedBy: configuredBy,
            configurationLocked: !this.isPowerAutomationRole(userRole) // 非官方角色配置鎖定
        };
    }

    /**
     * 獲取可見的雲側Admin區域
     */
    private static getVisibleCloudAdminSections(role: PersonalProRole): string[] {
        const sections = {
            [PersonalProRole.POWERAUTOMATION_ADMIN]: [
                'user_management', 'system_config', 'billing', 'analytics', 
                'credits_management', 'smart_routing', 'endpoint_control'
            ],
            [PersonalProRole.POWERAUTOMATION_SUPPORT]: [
                'user_management', 'system_config', 'analytics', 
                'credits_management', 'smart_routing', 'endpoint_control'
            ],
            [PersonalProRole.PREMIUM_USER]: [
                'personal_analytics', 'credits_status', 'smart_routing_status', 'usage_history'
            ],
            [PersonalProRole.STANDARD_USER]: [
                'personal_analytics', 'credits_status', 'usage_history'
            ],
            [PersonalProRole.TRIAL_USER]: [
                'credits_status', 'usage_history'
            ],
            [PersonalProRole.VIEWER_USER]: [
                'credits_status'
            ]
        };

        return sections[role] || [];
    }

    /**
     * 獲取可配置的雲側Admin區域
     */
    private static getConfigurableCloudAdminSections(role: PersonalProRole): string[] {
        const sections = {
            [PersonalProRole.POWERAUTOMATION_ADMIN]: [
                'user_management', 'system_config', 'billing', 'endpoint_control'
            ],
            [PersonalProRole.POWERAUTOMATION_SUPPORT]: [
                'user_management', 'system_config', 'endpoint_control'
            ],
            [PersonalProRole.PREMIUM_USER]: [
                'personal_preferences', 'notification_settings'
            ],
            [PersonalProRole.STANDARD_USER]: [
                'personal_preferences'
            ],
            [PersonalProRole.TRIAL_USER]: [],
            [PersonalProRole.VIEWER_USER]: []
        };

        return sections[role] || [];
    }

    /**
     * 獲取個人專業版角色限制
     */
    private static getPersonalProRoleLimits(role: PersonalProRole): {
        maxWorkflows: number;
        maxConcurrentJobs: number;
        allowedEnvironments: string[];
        creditsLimit: number;
    } {
        const limits = {
            [PersonalProRole.POWERAUTOMATION_ADMIN]: {
                maxWorkflows: -1,
                maxConcurrentJobs: -1,
                allowedEnvironments: ['development', 'staging', 'production'],
                creditsLimit: -1
            },
            [PersonalProRole.POWERAUTOMATION_SUPPORT]: {
                maxWorkflows: 100,
                maxConcurrentJobs: 20,
                allowedEnvironments: ['development', 'staging', 'production'],
                creditsLimit: 10000
            },
            [PersonalProRole.PREMIUM_USER]: {
                maxWorkflows: 50,
                maxConcurrentJobs: 10,
                allowedEnvironments: ['development', 'production'],
                creditsLimit: 5000
            },
            [PersonalProRole.STANDARD_USER]: {
                maxWorkflows: 20,
                maxConcurrentJobs: 5,
                allowedEnvironments: ['development', 'production'],
                creditsLimit: 2000
            },
            [PersonalProRole.TRIAL_USER]: {
                maxWorkflows: 5,
                maxConcurrentJobs: 2,
                allowedEnvironments: ['development'],
                creditsLimit: 500
            },
            [PersonalProRole.VIEWER_USER]: {
                maxWorkflows: 0,
                maxConcurrentJobs: 0,
                allowedEnvironments: [],
                creditsLimit: 0
            }
        };

        return limits[role] || limits[PersonalProRole.VIEWER_USER];
    }
}

