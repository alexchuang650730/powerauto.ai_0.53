import * as vscode from 'vscode';
import { PowerAutomationProvider } from './providers/PowerAutomationProvider';
import { WorkflowManager } from './managers/WorkflowManager';
import { CreditsManager } from './managers/CreditsManager';
import { WebSocketClient } from './services/WebSocketClient';
import { EditionModuleManager } from './managers/EditionModuleManager';
import { EditionType } from './types/EditionTypes';

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation VS Code Extension is now active!');
    
    // 初始化版本管理器
    const editionManager = new EditionModuleManager();
    
    // 檢測用戶版本類型
    const userEdition = detectUserEdition();
    editionManager.setEdition(userEdition);
    
    // 初始化核心服務
    const webSocketClient = new WebSocketClient();
    const workflowManager = new WorkflowManager(webSocketClient);
    const creditsManager = new CreditsManager(webSocketClient);
    
    // 創建側邊欄提供者
    const powerAutomationProvider = new PowerAutomationProvider(
        context,
        workflowManager,
        creditsManager,
        editionManager
    );
    
    // 註冊側邊欄視圖
    vscode.window.createTreeView('powerautomation', {
        treeDataProvider: powerAutomationProvider,
        showCollapseAll: true
    });
    
    // 註冊Webview面板
    const webviewProvider = new PowerAutomationWebviewProvider(
        context.extensionUri,
        workflowManager,
        creditsManager,
        editionManager
    );
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'powerautomation.webview',
            webviewProvider
        )
    );
    
    // 註冊命令
    registerCommands(context, workflowManager, creditsManager, editionManager);
    
    // 初始化WebSocket連接
    webSocketClient.connect();
    
    // 監聽配置變更
    vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('powerautomation')) {
            powerAutomationProvider.refresh();
        }
    });
    
    // 狀態欄項目
    createStatusBarItems(context, creditsManager);
}

function detectUserEdition(): EditionType {
    // 從配置或API檢測用戶版本
    const config = vscode.workspace.getConfiguration('powerautomation');
    const edition = config.get<string>('edition', 'personal_pro');
    
    switch (edition) {
        case 'enterprise':
            return EditionType.ENTERPRISE;
        case 'personal_pro':
            return EditionType.PERSONAL_PROFESSIONAL;
        case 'opensource':
            return EditionType.OPENSOURCE;
        default:
            return EditionType.PERSONAL_PROFESSIONAL;
    }
}

function registerCommands(
    context: vscode.ExtensionContext,
    workflowManager: WorkflowManager,
    creditsManager: CreditsManager,
    editionManager: EditionModuleManager
) {
    // 工作流命令
    const startWorkflowCommand = vscode.commands.registerCommand(
        'powerautomation.startWorkflow',
        () => workflowManager.startWorkflow()
    );
    
    const stopWorkflowCommand = vscode.commands.registerCommand(
        'powerautomation.stopWorkflow',
        () => workflowManager.stopWorkflow()
    );
    
    // 編碼助手命令
    const startCodingAssistantCommand = vscode.commands.registerCommand(
        'powerautomation.startCodingAssistant',
        () => workflowManager.startCodingAssistant()
    );
    
    // 測試生成命令
    const generateTestsCommand = vscode.commands.registerCommand(
        'powerautomation.generateTests',
        () => workflowManager.generateTests()
    );
    
    // 部署命令
    const deployCommand = vscode.commands.registerCommand(
        'powerautomation.deploy',
        () => workflowManager.deploy()
    );
    
    // 積分管理命令
    const refreshCreditsCommand = vscode.commands.registerCommand(
        'powerautomation.refreshCredits',
        () => creditsManager.refreshCredits()
    );
    
    const purchaseCreditsCommand = vscode.commands.registerCommand(
        'powerautomation.purchaseCredits',
        () => creditsManager.openPurchasePage()
    );
    
    // 設置命令
    const openSettingsCommand = vscode.commands.registerCommand(
        'powerautomation.openSettings',
        () => vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation')
    );
    
    // 版本切換命令（僅企業版）
    const switchEditionCommand = vscode.commands.registerCommand(
        'powerautomation.switchEdition',
        () => {
            if (editionManager.getCurrentEdition() === EditionType.ENTERPRISE) {
                showEditionSwitcher(editionManager);
            } else {
                vscode.window.showInformationMessage('版本切換功能僅在企業版中可用');
            }
        }
    );
    
    // 註冊所有命令
    context.subscriptions.push(
        startWorkflowCommand,
        stopWorkflowCommand,
        startCodingAssistantCommand,
        generateTestsCommand,
        deployCommand,
        refreshCreditsCommand,
        purchaseCreditsCommand,
        openSettingsCommand,
        switchEditionCommand
    );
}

function createStatusBarItems(context: vscode.ExtensionContext, creditsManager: CreditsManager) {
    // 積分顯示
    const creditsStatusBar = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    creditsStatusBar.command = 'powerautomation.refreshCredits';
    creditsStatusBar.tooltip = '點擊刷新積分';
    
    // 工作流狀態
    const workflowStatusBar = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        99
    );
    workflowStatusBar.command = 'powerautomation.startWorkflow';
    workflowStatusBar.text = '$(play) PowerAutomation';
    workflowStatusBar.tooltip = '啟動工作流';
    
    // 更新積分顯示
    creditsManager.onCreditsChanged((credits) => {
        creditsStatusBar.text = `$(star) ${credits} 積分`;
        creditsStatusBar.show();
    });
    
    workflowStatusBar.show();
    
    context.subscriptions.push(creditsStatusBar, workflowStatusBar);
}

async function showEditionSwitcher(editionManager: EditionModuleManager) {
    const options = [
        { label: '$(crown) 超級管理員', description: '完整六節點工作流', value: 'super_admin' },
        { label: '$(person) 開發者', description: '三節點開發工作流', value: 'developer' },
        { label: '$(beaker) 測試者', description: '測試驗證專用', value: 'tester' },
        { label: '$(rocket) DevOps', description: '部署運維專用', value: 'devops' }
    ];
    
    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: '選擇您的角色模式'
    });
    
    if (selected) {
        editionManager.switchRole(selected.value);
        vscode.window.showInformationMessage(`已切換到 ${selected.label} 模式`);
    }
}

class PowerAutomationWebviewProvider implements vscode.WebviewViewProvider {
    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly workflowManager: WorkflowManager,
        private readonly creditsManager: CreditsManager,
        private readonly editionManager: EditionModuleManager
    ) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        token: vscode.CancellationToken
    ) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };
        
        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);
        
        // 處理來自webview的消息
        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'startWorkflow':
                        this.workflowManager.startWorkflow();
                        break;
                    case 'startCoding':
                        this.workflowManager.startCodingAssistant();
                        break;
                    case 'generateTests':
                        this.workflowManager.generateTests();
                        break;
                    case 'deploy':
                        this.workflowManager.deploy();
                        break;
                    case 'refreshCredits':
                        this.creditsManager.refreshCredits();
                        break;
                    case 'purchaseCredits':
                        this.creditsManager.openPurchasePage();
                        break;
                }
            },
            undefined,
            []
        );
        
        // 監聽狀態變更
        this.workflowManager.onStatusChanged((status) => {
            webviewView.webview.postMessage({
                command: 'workflowStatusChanged',
                status: status
            });
        });
        
        this.creditsManager.onCreditsChanged((credits) => {
            webviewView.webview.postMessage({
                command: 'creditsChanged',
                credits: credits
            });
        });
    }
    
    private getHtmlForWebview(webview: vscode.Webview): string {
        const edition = this.editionManager.getCurrentEdition();
        const isEnterprise = edition === EditionType.ENTERPRISE;
        const isPersonalPro = edition === EditionType.PERSONAL_PROFESSIONAL;
        
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 16px;
        }
        
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .logo {
            width: 24px;
            height: 24px;
            margin-right: 8px;
            background: linear-gradient(135deg, #007ACC 0%, #005A9E 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
        
        .title {
            font-weight: 600;
            font-size: 14px;
        }
        
        .edition-badge {
            margin-left: auto;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            ${isEnterprise ? 'background: #FFA500; color: white;' : 'background: #007ACC; color: white;'}
        }
        
        .credits-section {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            text-align: center;
        }
        
        .credits-amount {
            font-size: 18px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 4px;
        }
        
        .credits-label {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .workflow-section {
            margin-bottom: 16px;
        }
        
        .section-title {
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .workflow-node {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .workflow-node:hover {
            background: var(--vscode-list-hoverBackground);
        }
        
        .workflow-node.active {
            border-color: var(--vscode-focusBorder);
            background: var(--vscode-list-activeSelectionBackground);
        }
        
        .workflow-node.processing {
            border-color: #FFA500;
            background: rgba(255, 165, 0, 0.1);
        }
        
        .node-header {
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }
        
        .node-icon {
            width: 16px;
            height: 16px;
            margin-right: 8px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
        }
        
        .code-icon { background: #10B981; }
        .test-icon { background: #F59E0B; }
        .deploy-icon { background: #3B82F6; }
        .analysis-icon { background: #8B5CF6; }
        .design-icon { background: #EC4899; }
        .monitor-icon { background: #6B7280; }
        
        .node-title {
            font-weight: 600;
            font-size: 12px;
        }
        
        .node-status {
            margin-left: auto;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
        }
        
        .status-pending { background: #6B7280; color: white; }
        .status-active { background: #10B981; color: white; }
        .status-processing { background: #F59E0B; color: white; }
        .status-completed { background: #3B82F6; color: white; }
        
        .node-description {
            font-size: 11px;
            opacity: 0.8;
            margin-top: 4px;
        }
        
        .progress-bar {
            height: 4px;
            background: var(--vscode-progressBar-background);
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--vscode-progressBar-foreground);
            transition: width 0.3s ease;
        }
        
        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 16px;
        }
        
        .btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .btn:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .btn-secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 16px;
        }
        
        .stat-item {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            padding: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-weight: bold;
            font-size: 14px;
            color: var(--vscode-textLink-foreground);
        }
        
        .stat-label {
            font-size: 10px;
            opacity: 0.8;
            margin-top: 2px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">PA</div>
        <div class="title">PowerAutomation</div>
        <div class="edition-badge">${isEnterprise ? '企業版' : '專業版'}</div>
    </div>
    
    ${isPersonalPro ? `
    <div class="credits-section">
        <div class="credits-amount" id="credits-amount">1,247</div>
        <div class="credits-label">可用積分</div>
    </div>
    ` : ''}
    
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-value" id="active-projects">12</div>
            <div class="stat-label">活躍項目</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="success-rate">94.2%</div>
            <div class="stat-label">成功率</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="time-saved">3.2h</div>
            <div class="stat-label">今日節省</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="cost-saved">$342</div>
            <div class="stat-label">成本節省</div>
        </div>
    </div>
    
    <div class="workflow-section">
        <div class="section-title">${isEnterprise ? '六節點工作流' : '智能開發流程'}</div>
        
        ${isEnterprise ? `
        <div class="workflow-node" data-node="analysis">
            <div class="node-header">
                <div class="node-icon analysis-icon">📋</div>
                <div class="node-title">需求分析</div>
                <div class="node-status status-completed">已完成</div>
            </div>
            <div class="node-description">AI理解業務需求，生成技術方案</div>
        </div>
        
        <div class="workflow-node" data-node="design">
            <div class="node-header">
                <div class="node-icon design-icon">🎨</div>
                <div class="node-title">架構設計</div>
                <div class="node-status status-completed">已完成</div>
            </div>
            <div class="node-description">智能架構建議，最佳實踐推薦</div>
        </div>
        ` : ''}
        
        <div class="workflow-node active" data-node="code">
            <div class="node-header">
                <div class="node-icon code-icon">💻</div>
                <div class="node-title">編碼實現</div>
                <div class="node-status status-processing">進行中</div>
            </div>
            <div class="node-description">AI編程助手，代碼自動生成</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 67%"></div>
            </div>
        </div>
        
        <div class="workflow-node" data-node="test">
            <div class="node-header">
                <div class="node-icon test-icon">🧪</div>
                <div class="node-title">測試驗證</div>
                <div class="node-status status-pending">等待中</div>
            </div>
            <div class="node-description">自動化測試，質量保障</div>
        </div>
        
        <div class="workflow-node" data-node="deploy">
            <div class="node-header">
                <div class="node-icon deploy-icon">🚀</div>
                <div class="node-title">部署發布</div>
                <div class="node-status status-pending">等待中</div>
            </div>
            <div class="node-description">一鍵部署，環境管理</div>
        </div>
        
        ${isEnterprise ? `
        <div class="workflow-node" data-node="monitor">
            <div class="node-header">
                <div class="node-icon monitor-icon">📊</div>
                <div class="node-title">監控運維</div>
                <div class="node-status status-pending">等待中</div>
            </div>
            <div class="node-description">性能監控，問題預警</div>
        </div>
        ` : ''}
    </div>
    
    <div class="action-buttons">
        <button class="btn" onclick="startWorkflow()">
            ▶️ 啟動工作流
        </button>
        <button class="btn btn-secondary" onclick="startCoding()">
            💻 編碼助手
        </button>
        <button class="btn btn-secondary" onclick="generateTests()">
            🧪 生成測試
        </button>
        <button class="btn btn-secondary" onclick="deploy()">
            🚀 一鍵部署
        </button>
        ${isPersonalPro ? `
        <button class="btn btn-secondary" onclick="purchaseCredits()">
            💰 購買積分
        </button>
        ` : ''}
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function startWorkflow() {
            vscode.postMessage({ command: 'startWorkflow' });
        }
        
        function startCoding() {
            vscode.postMessage({ command: 'startCoding' });
        }
        
        function generateTests() {
            vscode.postMessage({ command: 'generateTests' });
        }
        
        function deploy() {
            vscode.postMessage({ command: 'deploy' });
        }
        
        function purchaseCredits() {
            vscode.postMessage({ command: 'purchaseCredits' });
        }
        
        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'workflowStatusChanged':
                    updateWorkflowStatus(message.status);
                    break;
                case 'creditsChanged':
                    updateCredits(message.credits);
                    break;
            }
        });
        
        function updateWorkflowStatus(status) {
            // 更新工作流狀態顯示
            console.log('Workflow status updated:', status);
        }
        
        function updateCredits(credits) {
            const creditsElement = document.getElementById('credits-amount');
            if (creditsElement) {
                creditsElement.textContent = credits.toLocaleString();
            }
        }
    </script>
</body>
</html>`;
    }
}

export function deactivate() {
    console.log('PowerAutomation VS Code Extension is now deactivated');
}

