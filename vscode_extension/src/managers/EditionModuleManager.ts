import * as vscode from 'vscode';
import { EditionType } from '../types/EditionTypes';

/**
 * 版本模塊管理器 - 根據不同版本動態加載功能模塊
 */
export class EditionModuleManager {
    private edition: EditionType;
    private loadedModules: Map<string, any> = new Map();

    constructor() {
        this.edition = this.getEditionFromConfig();
        console.log(`🎯 當前版本: ${this.edition}`);
    }

    /**
     * 從配置獲取版本類型
     */
    private getEditionFromConfig(): EditionType {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const editionString = config.get<string>('edition', 'personal_pro');
        
        switch (editionString) {
            case 'enterprise':
                return EditionType.ENTERPRISE;
            case 'personal_pro':
                return EditionType.PERSONAL_PRO;
            case 'opensource':
                return EditionType.OPENSOURCE;
            default:
                return EditionType.PERSONAL_PRO;
        }
    }

    /**
     * 獲取當前版本
     */
    getEdition(): EditionType {
        return this.edition;
    }

    /**
     * 動態加載模塊
     */
    async loadModule(moduleName: string): Promise<any> {
        if (this.loadedModules.has(moduleName)) {
            return this.loadedModules.get(moduleName);
        }

        const moduleConfig = this.getModuleConfig(moduleName);
        if (!moduleConfig.enabled) {
            console.log(`⚠️ 模塊 ${moduleName} 在 ${this.edition} 版本中不可用`);
            return null;
        }

        try {
            const module = await import(moduleConfig.path);
            this.loadedModules.set(moduleName, module);
            console.log(`✅ 模塊 ${moduleName} 加載成功`);
            return module;
        } catch (error) {
            console.error(`❌ 模塊 ${moduleName} 加載失敗:`, error);
            return null;
        }
    }

    /**
     * 獲取模塊配置
     */
    private getModuleConfig(moduleName: string): { enabled: boolean; path: string } {
        const moduleConfigs = {
            // 🏢 企業版模塊配置
            [EditionType.ENTERPRISE]: {
                'requirementAnalysis': { enabled: true, path: '../modules/RequirementAnalysisModule' },
                'architectureDesign': { enabled: true, path: '../modules/ArchitectureDesignModule' },
                'codeImplementation': { enabled: true, path: '../modules/CodeImplementationModule' },
                'testVerification': { enabled: true, path: '../modules/TestVerificationModule' },
                'deploymentRelease': { enabled: true, path: '../modules/DeploymentReleaseModule' },
                'monitoringOperations': { enabled: true, path: '../modules/MonitoringOperationsModule' },
                'enterpriseAdmin': { enabled: true, path: '../modules/EnterpriseAdminModule' },
                'multiTenantManager': { enabled: true, path: '../modules/MultiTenantManagerModule' },
                'complianceAudit': { enabled: true, path: '../modules/ComplianceAuditModule' },
                'cloudAdminUI': { enabled: true, path: '../modules/CloudAdminUIModule' },
                'onPremiseAdmin': { enabled: true, path: '../modules/OnPremiseAdminModule' },
                // 🆕 企業版雲側Admin全量功能
                'cloudAdminFull': { enabled: true, path: '../modules/CloudAdminFullModule' },
                'roleManagement': { enabled: true, path: '../modules/RoleManagementModule' },
                'endpointControl': { enabled: true, path: '../modules/EndpointControlModule' },
                'centralizedConfig': { enabled: true, path: '../modules/CentralizedConfigModule' },
                // 🆕 端側功能鏡像 (雲側可控制)
                'cloudTerminalControl': { enabled: true, path: '../modules/CloudTerminalControlModule' },
                'cloudWorkflowRecording': { enabled: true, path: '../modules/CloudWorkflowRecordingModule' },
                'cloudIntelligentIntervention': { enabled: true, path: '../modules/CloudIntelligentInterventionModule' },
                'cloudCreditsSystem': { enabled: true, path: '../modules/CloudCreditsSystemModule' },
                'cloudSmartRouting': { enabled: true, path: '../modules/CloudSmartRoutingModule' },
                'cloudInteractionManager': { enabled: true, path: '../modules/CloudInteractionManagerModule' }
            },

            // 👤 個人專業版模塊配置
            [EditionType.PERSONAL_PRO]: {
                'requirementAnalysis': { enabled: false, path: '' },
                'architectureDesign': { enabled: false, path: '' },
                'codeImplementation': { enabled: true, path: '../modules/CodeImplementationModule' },
                'testVerification': { enabled: true, path: '../modules/TestVerificationModule' },
                'deploymentRelease': { enabled: true, path: '../modules/DeploymentReleaseModule' },
                'monitoringOperations': { enabled: false, path: '' },
                'automationFramework': { enabled: true, path: '../modules/AutomationFrameworkModule' },
                'intelligentIntervention': { enabled: true, path: '../modules/IntelligentInterventionModule' },
                'releaseManager': { enabled: true, path: '../modules/ReleaseManagerModule' },
                'pluginSystem': { enabled: true, path: '../modules/PluginSystemModule' },
                'terminalController': { enabled: true, path: '../modules/TerminalControllerModule' },
                'interactionManager': { enabled: true, path: '../modules/InteractionManagerModule' },
                'smartRouting': { enabled: true, path: '../modules/SmartRoutingModule' },
                'creditsSystem': { enabled: true, path: '../modules/CreditsSystemModule' },
                // 🚫 個人專業版不包含雲側Admin UI
                'cloudAdminUI': { enabled: false, path: '' },
                'enterpriseAdmin': { enabled: false, path: '' },
                // ✅ 雲側服務（後台，無UI）
                'cloudSyncService': { enabled: true, path: '../services/CloudSyncService' },
                'smartRoutingService': { enabled: true, path: '../services/SmartRoutingService' }
            },

            // 🔓 開源版模塊配置
            [EditionType.OPENSOURCE]: {
                'requirementAnalysis': { enabled: false, path: '' },
                'architectureDesign': { enabled: false, path: '' },
                'codeImplementation': { enabled: true, path: '../modules/CodeImplementationModule' },
                'testVerification': { enabled: false, path: '' },
                'deploymentRelease': { enabled: false, path: '' },
                'monitoringOperations': { enabled: false, path: '' },
                'basicAutomation': { enabled: true, path: '../modules/BasicAutomationModule' },
                'cliInterface': { enabled: true, path: '../modules/CLIInterfaceModule' },
                // 🚫 開源版不包含任何UI
                'cloudAdminUI': { enabled: false, path: '' },
                'enterpriseAdmin': { enabled: false, path: '' },
                'vscodeUI': { enabled: false, path: '' }
            }
        };

        const editionConfig = moduleConfigs[this.edition];
        return editionConfig[moduleName] || { enabled: false, path: '' };
    }

    /**
     * 獲取可用的功能列表
     */
    getAvailableFeatures(): string[] {
        const featureMap = {
            [EditionType.ENTERPRISE]: [
                '需求分析', '架構設計', '編碼實現', '測試驗證', 
                '部署發布', '監控運維', '企業管理', '多租戶管理',
                '合規審計', '雲側Admin UI', '端側Admin UI'
            ],
            [EditionType.PERSONAL_PRO]: [
                '編碼實現', '測試驗證', '部署發布', 
                '自動化框架', '智能介入', 'Release Manager',
                '插件系統', '終端控制', '交互管理',
                '智慧路由', '積分系統', '端側Admin UI'
                // 注意：雲側服務存在但不在UI中體現
            ],
            [EditionType.OPENSOURCE]: [
                '編碼實現', '基礎自動化', 'CLI接口'
            ]
        };

        return featureMap[this.edition] || [];
    }

    /**
     * 檢查功能是否可用
     */
    isFeatureAvailable(featureName: string): boolean {
        const moduleConfig = this.getModuleConfig(featureName);
        return moduleConfig.enabled;
    }

    /**
     * 獲取版本特定的UI配置
     */
    getUIConfig(): any {
        const uiConfigs = {
            [EditionType.ENTERPRISE]: {
                showCloudAdmin: true,
                showOnPremiseAdmin: true,
                showAllWorkflowNodes: true,
                showEnterpriseFeatures: true,
                showMultiTenantManager: true,
                // 🆕 企業版雲側Admin全量功能
                showCloudAdminFull: true,           // 雲側包含端側全量功能
                showRoleManagement: true,           // 角色管理
                showEndpointControl: true,          // 端側控制
                showCentralizedConfig: true,        // 中央化配置
                // 🆕 端側功能鏡像控制
                cloudControlEndpoint: true,         // 雲側可控制端側
                roleBasedEndpointUI: true,          // 基於角色的端側UI配置
                maxWorkflows: -1, // 無限制
                supportedEnvironments: ['development', 'staging', 'production', 'enterprise']
            },
            [EditionType.PERSONAL_PRO]: {
                showCloudAdmin: true, // ✅ 個人版也顯示雲側Admin UI
                showOnPremiseAdmin: false,
                showAllWorkflowNodes: false,
                showEnterpriseFeatures: false,
                showMultiTenantManager: false,
                showCoreWorkflowNodes: true, // ✅ 只顯示核心三節點
                showCreditsSystem: true,
                showSmartRouting: true,
                // ✅ 個人版包含雲側Admin UI但權限受限
                showCloudAdminFull: false,              // 不是完整雲側Admin
                showRoleManagement: false,              // 用戶不能管理角色
                showEndpointControl: false,             // 用戶不能控制端側
                showCentralizedConfig: false,           // 用戶不能中央化配置
                cloudControlEndpoint: false,            // 用戶不能雲側控制端側
                roleBasedEndpointUI: true,              // ✅ 但仍有基於角色的端側UI
                // 🆕 個人版特有配置
                showPersonalCloudAdmin: true,           // 顯示個人版雲側Admin
                powerautomationAdminControl: true,      // PowerAutomation Administrator控制
                userConfigurationLimited: true,        // 用戶配置權限有限
                maxWorkflows: 10,
                supportedEnvironments: ['development', 'production']
            },
            [EditionType.OPENSOURCE]: {
                showCloudAdmin: false,
                showOnPremiseAdmin: false,
                showAllWorkflowNodes: false,
                showEnterpriseFeatures: false,
                showMultiTenantManager: false,
                showCoreWorkflowNodes: false,
                showBasicFeatures: true,
                // 🚫 開源版不包含任何高級功能
                showCloudAdminFull: false,
                showRoleManagement: false,
                showEndpointControl: false,
                showCentralizedConfig: false,
                cloudControlEndpoint: false,
                roleBasedEndpointUI: false,
                maxWorkflows: 3,
                supportedEnvironments: ['development']
            }
        };

        return uiConfigs[this.edition];
    }

    /**
     * 獲取雲側服務配置
     */
    getCloudServiceConfig(): any {
        return {
            [EditionType.ENTERPRISE]: {
                enableCloudAdmin: true,
                enableMultiTenant: true,
                enableAdvancedAnalytics: true,
                enableComplianceAudit: true
            },
            [EditionType.PERSONAL_PRO]: {
                enableCloudAdmin: false, // 🚫 不啟用雲側Admin UI
                enableCreditsSync: true, // ✅ 啟用積分同步服務
                enableSmartRouting: true, // ✅ 啟用智慧路由服務
                enableBasicAnalytics: true,
                enablePersonalBackup: true
            },
            [EditionType.OPENSOURCE]: {
                enableCloudAdmin: false,
                enableCreditsSync: false,
                enableSmartRouting: false,
                enableBasicAnalytics: false
            }
        }[this.edition];
    }

    /**
     * 重新加載配置
     */
    reloadConfiguration(): void {
        this.edition = this.getEditionFromConfig();
        this.loadedModules.clear();
        console.log(`🔄 配置已重新加載，當前版本: ${this.edition}`);
    }

    /**
     * 獲取版本信息
     */
    getVersionInfo(): any {
        return {
            edition: this.edition,
            features: this.getAvailableFeatures(),
            uiConfig: this.getUIConfig(),
            cloudConfig: this.getCloudServiceConfig(),
            loadedModules: Array.from(this.loadedModules.keys())
        };
    }
}

