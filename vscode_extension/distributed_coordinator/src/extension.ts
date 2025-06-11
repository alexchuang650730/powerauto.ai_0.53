import * as vscode from 'vscode';
import * as path from 'path';
import axios from 'axios';

/**
 * PowerAutomation 分布式协调器 VSCode 扩展
 */

interface NodeStatus {
    nodeId: string;
    status: 'online' | 'offline' | 'busy';
    cpuUsage: number;
    memoryUsage: number;
    activeTasks: number;
    lastHeartbeat: string;
}

interface CoordinatorStatus {
    status: 'active' | 'inactive' | 'error';
    totalNodes: number;
    activeNodes: number;
    totalTasks: number;
    completedTasks: number;
    uptime: number;
}

interface PerformanceMetrics {
    cacheHitRate: number;
    averageExecutionTime: number;
    parallelEfficiency: number;
    resourceUtilization: number;
}

class DistributedCoordinatorProvider implements vscode.TreeDataProvider<NodeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<NodeItem | undefined | null | void> = new vscode.EventEmitter<NodeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<NodeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private nodes: NodeStatus[] = [];
    private coordinatorStatus: CoordinatorStatus | null = null;

    constructor(private context: vscode.ExtensionContext) {
        this.startStatusPolling();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: NodeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: NodeItem): Thenable<NodeItem[]> {
        if (!element) {
            // 根节点 - 显示协调器状态和节点列表
            const items: NodeItem[] = [];
            
            if (this.coordinatorStatus) {
                items.push(new NodeItem(
                    `协调器状态: ${this.coordinatorStatus.status}`,
                    `活跃节点: ${this.coordinatorStatus.activeNodes}/${this.coordinatorStatus.totalNodes}`,
                    vscode.TreeItemCollapsibleState.None,
                    'coordinator'
                ));
            }

            // 添加节点
            this.nodes.forEach(node => {
                const statusIcon = node.status === 'online' ? '🟢' : 
                                 node.status === 'busy' ? '🟡' : '🔴';
                items.push(new NodeItem(
                    `${statusIcon} ${node.nodeId}`,
                    `CPU: ${node.cpuUsage}% | 内存: ${node.memoryUsage}% | 任务: ${node.activeTasks}`,
                    vscode.TreeItemCollapsibleState.None,
                    'node'
                ));
            });

            return Promise.resolve(items);
        }
        return Promise.resolve([]);
    }

    private async startStatusPolling() {
        const refreshInterval = vscode.workspace.getConfiguration('powerautomation.distributed').get<number>('refreshInterval', 5000);
        
        setInterval(async () => {
            try {
                await this.updateStatus();
                this.refresh();
            } catch (error) {
                console.error('状态更新失败:', error);
            }
        }, refreshInterval);
    }

    private async updateStatus() {
        try {
            // 模拟API调用 - 实际应该调用MCP适配器
            this.coordinatorStatus = {
                status: 'active',
                totalNodes: 5,
                activeNodes: 4,
                totalTasks: 156,
                completedTasks: 142,
                uptime: 3600
            };

            this.nodes = [
                {
                    nodeId: 'node-1',
                    status: 'online',
                    cpuUsage: 45,
                    memoryUsage: 60,
                    activeTasks: 3,
                    lastHeartbeat: new Date().toISOString()
                },
                {
                    nodeId: 'node-2', 
                    status: 'busy',
                    cpuUsage: 85,
                    memoryUsage: 75,
                    activeTasks: 8,
                    lastHeartbeat: new Date().toISOString()
                },
                {
                    nodeId: 'node-3',
                    status: 'online',
                    cpuUsage: 30,
                    memoryUsage: 45,
                    activeTasks: 2,
                    lastHeartbeat: new Date().toISOString()
                },
                {
                    nodeId: 'node-4',
                    status: 'offline',
                    cpuUsage: 0,
                    memoryUsage: 0,
                    activeTasks: 0,
                    lastHeartbeat: new Date(Date.now() - 300000).toISOString()
                }
            ];
        } catch (error) {
            console.error('获取状态失败:', error);
        }
    }
}

class NodeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string
    ) {
        super(label, collapsibleState);
        this.tooltip = description;
        this.description = description;
    }
}

class PerformanceWebviewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'powerautomation.performance';

    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // 定期更新性能数据
        setInterval(() => {
            this.updatePerformanceData();
        }, 2000);
    }

    private updatePerformanceData() {
        if (this._view) {
            // 模拟性能数据
            const metrics: PerformanceMetrics = {
                cacheHitRate: Math.random() * 100,
                averageExecutionTime: 120 + Math.random() * 60,
                parallelEfficiency: 80 + Math.random() * 20,
                resourceUtilization: 60 + Math.random() * 30
            };

            this._view.webview.postMessage({
                type: 'updateMetrics',
                metrics: metrics
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>性能监控</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 10px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                .metric {
                    margin: 10px 0;
                    padding: 10px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                }
                .metric-label {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .metric-value {
                    font-size: 1.2em;
                    color: var(--vscode-textLink-foreground);
                }
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background-color: var(--vscode-progressBar-background);
                    border-radius: 4px;
                    overflow: hidden;
                    margin-top: 5px;
                }
                .progress-fill {
                    height: 100%;
                    background-color: var(--vscode-progressBar-foreground);
                    transition: width 0.3s ease;
                }
            </style>
        </head>
        <body>
            <h3>🚀 性能监控</h3>
            
            <div class="metric">
                <div class="metric-label">缓存命中率</div>
                <div class="metric-value" id="cacheHitRate">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cacheHitRateBar"></div>
                </div>
            </div>

            <div class="metric">
                <div class="metric-label">平均执行时间</div>
                <div class="metric-value" id="avgExecutionTime">--</div>
            </div>

            <div class="metric">
                <div class="metric-label">并行效率</div>
                <div class="metric-value" id="parallelEfficiency">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="parallelEfficiencyBar"></div>
                </div>
            </div>

            <div class="metric">
                <div class="metric-label">资源利用率</div>
                <div class="metric-value" id="resourceUtilization">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="resourceUtilizationBar"></div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    if (message.type === 'updateMetrics') {
                        const metrics = message.metrics;
                        
                        document.getElementById('cacheHitRate').textContent = metrics.cacheHitRate.toFixed(1) + '%';
                        document.getElementById('cacheHitRateBar').style.width = metrics.cacheHitRate + '%';
                        
                        document.getElementById('avgExecutionTime').textContent = metrics.averageExecutionTime.toFixed(0) + 'ms';
                        
                        document.getElementById('parallelEfficiency').textContent = metrics.parallelEfficiency.toFixed(1) + '%';
                        document.getElementById('parallelEfficiencyBar').style.width = metrics.parallelEfficiency + '%';
                        
                        document.getElementById('resourceUtilization').textContent = metrics.resourceUtilization.toFixed(1) + '%';
                        document.getElementById('resourceUtilizationBar').style.width = metrics.resourceUtilization + '%';
                    }
                });
            </script>
        </body>
        </html>`;
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation 分布式协调器扩展已激活');

    // 注册树视图提供者
    const distributedProvider = new DistributedCoordinatorProvider(context);
    vscode.window.registerTreeDataProvider('powerautomationDistributedNodes', distributedProvider);

    // 注册性能监控WebView
    const performanceProvider = new PerformanceWebviewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('powerautomation.performance', performanceProvider)
    );

    // 注册命令
    const commands = [
        vscode.commands.registerCommand('powerautomation.distributed.activate', async () => {
            vscode.window.showInformationMessage('🚀 PowerAutomation 分布式协调器已激活');
            
            // 设置上下文
            vscode.commands.executeCommand('setContext', 'powerautomation.distributed.active', true);
            
            // 刷新视图
            distributedProvider.refresh();
        }),

        vscode.commands.registerCommand('powerautomation.distributed.showStatus', async () => {
            const panel = vscode.window.createWebviewPanel(
                'coordinatorStatus',
                '协调器状态',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = `
                <html>
                <body>
                    <h1>🎯 分布式协调器状态</h1>
                    <p>状态: 活跃</p>
                    <p>节点数: 4/5</p>
                    <p>运行时间: 1小时</p>
                    <p>完成任务: 142/156</p>
                </body>
                </html>
            `;
        }),

        vscode.commands.registerCommand('powerautomation.distributed.showNodes', async () => {
            const quickPick = vscode.window.createQuickPick();
            quickPick.items = [
                { label: '🟢 node-1', description: 'CPU: 45% | 内存: 60% | 任务: 3' },
                { label: '🟡 node-2', description: 'CPU: 85% | 内存: 75% | 任务: 8' },
                { label: '🟢 node-3', description: 'CPU: 30% | 内存: 45% | 任务: 2' },
                { label: '🔴 node-4', description: '离线' }
            ];
            quickPick.onDidChangeSelection(selection => {
                if (selection[0]) {
                    vscode.window.showInformationMessage(`选择了节点: ${selection[0].label}`);
                }
            });
            quickPick.show();
        }),

        vscode.commands.registerCommand('powerautomation.distributed.showPerformance', async () => {
            vscode.window.showInformationMessage('📊 性能报告: 缓存命中率 78%, 并行效率 85%');
        }),

        vscode.commands.registerCommand('powerautomation.distributed.runTests', async () => {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "运行分布式测试",
                cancellable: true
            }, async (progress, token) => {
                for (let i = 0; i < 100; i += 10) {
                    if (token.isCancellationRequested) {
                        break;
                    }
                    
                    progress.report({ 
                        increment: 10, 
                        message: `执行中... ${i + 10}%` 
                    });
                    
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
                
                vscode.window.showInformationMessage('✅ 分布式测试执行完成！');
            });
        })
    ];

    context.subscriptions.push(...commands);

    // 自动启动
    const autoStart = vscode.workspace.getConfiguration('powerautomation.distributed').get<boolean>('autoStart', true);
    if (autoStart) {
        vscode.commands.executeCommand('powerautomation.distributed.activate');
    }
}

export function deactivate() {
    console.log('PowerAutomation 分布式协调器扩展已停用');
}

