import * as vscode from 'vscode';
import { WebSocketClient } from '../services/WebSocketClient';

export interface WorkflowNode {
    id: string;
    name: string;
    status: 'pending' | 'active' | 'processing' | 'completed' | 'error';
    progress: number;
    description: string;
    icon: string;
}

export interface WorkflowStatus {
    isRunning: boolean;
    currentNode: string | null;
    nodes: WorkflowNode[];
    startTime?: Date;
    endTime?: Date;
}

export class WorkflowManager {
    private _onStatusChanged = new vscode.EventEmitter<WorkflowStatus>();
    public readonly onStatusChanged = this._onStatusChanged.event;
    
    private _status: WorkflowStatus;
    private _outputChannel: vscode.OutputChannel;
    
    constructor(private webSocketClient: WebSocketClient) {
        this._outputChannel = vscode.window.createOutputChannel('PowerAutomation Workflow');
        this._status = this.initializeWorkflowStatus();
        
        // 監聽WebSocket消息
        this.webSocketClient.onMessage('workflow_status_update', (data) => {
            this.handleWorkflowUpdate(data);
        });
    }
    
    private initializeWorkflowStatus(): WorkflowStatus {
        // 根據用戶版本初始化不同的工作流節點
        const config = vscode.workspace.getConfiguration('powerautomation');
        const edition = config.get<string>('edition', 'personal_pro');
        
        let nodes: WorkflowNode[];
        
        if (edition === 'enterprise') {
            nodes = [
                {
                    id: 'analysis',
                    name: '需求分析',
                    status: 'pending',
                    progress: 0,
                    description: 'AI理解業務需求，生成技術方案',
                    icon: '📋'
                },
                {
                    id: 'design',
                    name: '架構設計',
                    status: 'pending',
                    progress: 0,
                    description: '智能架構建議，最佳實踐推薦',
                    icon: '🎨'
                },
                {
                    id: 'code',
                    name: '編碼實現',
                    status: 'pending',
                    progress: 0,
                    description: 'AI編程助手，代碼自動生成',
                    icon: '💻'
                },
                {
                    id: 'test',
                    name: '測試驗證',
                    status: 'pending',
                    progress: 0,
                    description: '自動化測試，質量保障',
                    icon: '🧪'
                },
                {
                    id: 'deploy',
                    name: '部署發布',
                    status: 'pending',
                    progress: 0,
                    description: '一鍵部署，環境管理',
                    icon: '🚀'
                },
                {
                    id: 'monitor',
                    name: '監控運維',
                    status: 'pending',
                    progress: 0,
                    description: '性能監控，問題預警',
                    icon: '📊'
                }
            ];
        } else {
            // Personal Pro版本 - 三節點
            nodes = [
                {
                    id: 'code',
                    name: '編碼實現',
                    status: 'pending',
                    progress: 0,
                    description: 'AI編程助手，代碼自動生成',
                    icon: '💻'
                },
                {
                    id: 'test',
                    name: '測試驗證',
                    status: 'pending',
                    progress: 0,
                    description: '自動化測試，質量保障',
                    icon: '🧪'
                },
                {
                    id: 'deploy',
                    name: '部署發布',
                    status: 'pending',
                    progress: 0,
                    description: '一鍵部署，環境管理',
                    icon: '🚀'
                }
            ];
        }
        
        return {
            isRunning: false,
            currentNode: null,
            nodes: nodes
        };
    }
    
    public async startWorkflow(): Promise<void> {
        try {
            this._outputChannel.appendLine('🚀 啟動PowerAutomation工作流...');
            
            this._status.isRunning = true;
            this._status.startTime = new Date();
            this._status.currentNode = this._status.nodes[0].id;
            
            // 重置所有節點狀態
            this._status.nodes.forEach(node => {
                node.status = 'pending';
                node.progress = 0;
            });
            
            // 設置第一個節點為活躍狀態
            this._status.nodes[0].status = 'active';
            
            this._onStatusChanged.fire(this._status);
            
            // 發送啟動請求到服務器
            this.webSocketClient.send('start_workflow', {
                edition: vscode.workspace.getConfiguration('powerautomation').get('edition'),
                nodes: this._status.nodes.map(n => n.id)
            });
            
            vscode.window.showInformationMessage('工作流已啟動');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 啟動工作流失敗: ${error}`);
            vscode.window.showErrorMessage(`啟動工作流失敗: ${error}`);
        }
    }
    
    public async stopWorkflow(): Promise<void> {
        try {
            this._outputChannel.appendLine('⏹️ 停止工作流...');
            
            this._status.isRunning = false;
            this._status.endTime = new Date();
            this._status.currentNode = null;
            
            // 停止所有處理中的節點
            this._status.nodes.forEach(node => {
                if (node.status === 'processing' || node.status === 'active') {
                    node.status = 'pending';
                }
            });
            
            this._onStatusChanged.fire(this._status);
            
            // 發送停止請求到服務器
            this.webSocketClient.send('stop_workflow', {});
            
            vscode.window.showInformationMessage('工作流已停止');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 停止工作流失敗: ${error}`);
            vscode.window.showErrorMessage(`停止工作流失敗: ${error}`);
        }
    }
    
    public async startCodingAssistant(): Promise<void> {
        try {
            this._outputChannel.appendLine('💻 啟動編碼助手...');
            
            // 獲取當前活躍的編輯器
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showWarningMessage('請先打開一個代碼文件');
                return;
            }
            
            // 獲取當前選中的文本或整個文檔
            const document = activeEditor.document;
            const selection = activeEditor.selection;
            const text = selection.isEmpty ? document.getText() : document.getText(selection);
            
            // 發送編碼助手請求
            this.webSocketClient.send('start_coding_assistant', {
                language: document.languageId,
                code: text,
                file_path: document.fileName,
                cursor_position: document.offsetAt(activeEditor.selection.active)
            });
            
            // 更新編碼節點狀態
            const codeNode = this._status.nodes.find(n => n.id === 'code');
            if (codeNode) {
                codeNode.status = 'processing';
                this._onStatusChanged.fire(this._status);
            }
            
            vscode.window.showInformationMessage('編碼助手已啟動');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 啟動編碼助手失敗: ${error}`);
            vscode.window.showErrorMessage(`啟動編碼助手失敗: ${error}`);
        }
    }
    
    public async generateTests(): Promise<void> {
        try {
            this._outputChannel.appendLine('🧪 生成測試用例...');
            
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showWarningMessage('請先打開一個代碼文件');
                return;
            }
            
            const document = activeEditor.document;
            const code = document.getText();
            
            // 發送測試生成請求
            this.webSocketClient.send('generate_tests', {
                language: document.languageId,
                code: code,
                file_path: document.fileName
            });
            
            // 更新測試節點狀態
            const testNode = this._status.nodes.find(n => n.id === 'test');
            if (testNode) {
                testNode.status = 'processing';
                this._onStatusChanged.fire(this._status);
            }
            
            vscode.window.showInformationMessage('正在生成測試用例...');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 生成測試失敗: ${error}`);
            vscode.window.showErrorMessage(`生成測試失敗: ${error}`);
        }
    }
    
    public async deploy(): Promise<void> {
        try {
            this._outputChannel.appendLine('🚀 開始部署...');
            
            // 獲取工作區根目錄
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showWarningMessage('請先打開一個工作區');
                return;
            }
            
            // 檢查是否有package.json或其他配置文件
            const packageJsonUri = vscode.Uri.joinPath(workspaceFolder.uri, 'package.json');
            
            try {
                await vscode.workspace.fs.stat(packageJsonUri);
            } catch {
                vscode.window.showWarningMessage('未找到package.json文件，請確保項目配置正確');
                return;
            }
            
            // 發送部署請求
            this.webSocketClient.send('deploy_project', {
                project_path: workspaceFolder.uri.fsPath,
                project_name: workspaceFolder.name
            });
            
            // 更新部署節點狀態
            const deployNode = this._status.nodes.find(n => n.id === 'deploy');
            if (deployNode) {
                deployNode.status = 'processing';
                this._onStatusChanged.fire(this._status);
            }
            
            vscode.window.showInformationMessage('正在部署項目...');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 部署失敗: ${error}`);
            vscode.window.showErrorMessage(`部署失敗: ${error}`);
        }
    }
    
    private handleWorkflowUpdate(data: any): void {
        this._outputChannel.appendLine(`📊 工作流更新: ${JSON.stringify(data)}`);
        
        if (data.node_id) {
            const node = this._status.nodes.find(n => n.id === data.node_id);
            if (node) {
                if (data.status) node.status = data.status;
                if (data.progress !== undefined) node.progress = data.progress;
                
                // 如果節點完成，自動啟動下一個節點
                if (data.status === 'completed') {
                    const currentIndex = this._status.nodes.findIndex(n => n.id === data.node_id);
                    if (currentIndex < this._status.nodes.length - 1) {
                        this._status.nodes[currentIndex + 1].status = 'active';
                        this._status.currentNode = this._status.nodes[currentIndex + 1].id;
                    } else {
                        // 所有節點完成
                        this._status.isRunning = false;
                        this._status.endTime = new Date();
                        this._status.currentNode = null;
                        vscode.window.showInformationMessage('🎉 工作流已完成！');
                    }
                }
                
                this._onStatusChanged.fire(this._status);
            }
        }
        
        // 處理代碼建議
        if (data.type === 'code_suggestion') {
            this.handleCodeSuggestion(data);
        }
        
        // 處理測試結果
        if (data.type === 'test_generated') {
            this.handleTestGenerated(data);
        }
        
        // 處理部署結果
        if (data.type === 'deployment_result') {
            this.handleDeploymentResult(data);
        }
    }
    
    private async handleCodeSuggestion(data: any): Promise<void> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor || !data.suggestions) return;
        
        // 顯示代碼建議
        const suggestions = data.suggestions;
        if (suggestions.length > 0) {
            const selected = await vscode.window.showQuickPick(
                suggestions.map((s: any, i: number) => ({
                    label: `建議 ${i + 1}`,
                    description: s.description,
                    detail: s.code.substring(0, 100) + '...',
                    suggestion: s
                })),
                { placeHolder: '選擇要應用的代碼建議' }
            );
            
            if (selected) {
                // 應用選中的建議
                const edit = new vscode.WorkspaceEdit();
                const range = data.range ? 
                    new vscode.Range(data.range.start.line, data.range.start.character, 
                                   data.range.end.line, data.range.end.character) :
                    activeEditor.selection;
                
                edit.replace(activeEditor.document.uri, range, selected.suggestion.code);
                await vscode.workspace.applyEdit(edit);
                
                vscode.window.showInformationMessage('代碼建議已應用');
            }
        }
    }
    
    private async handleTestGenerated(data: any): Promise<void> {
        if (!data.test_code) return;
        
        // 創建測試文件
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return;
        
        const testFileName = data.test_file_name || 'generated_test.js';
        const testFileUri = vscode.Uri.joinPath(workspaceFolder.uri, 'tests', testFileName);
        
        try {
            // 確保tests目錄存在
            const testsDir = vscode.Uri.joinPath(workspaceFolder.uri, 'tests');
            await vscode.workspace.fs.createDirectory(testsDir);
            
            // 寫入測試文件
            await vscode.workspace.fs.writeFile(testFileUri, Buffer.from(data.test_code, 'utf8'));
            
            // 打開測試文件
            const document = await vscode.workspace.openTextDocument(testFileUri);
            await vscode.window.showTextDocument(document);
            
            vscode.window.showInformationMessage(`測試文件已生成: ${testFileName}`);
            
        } catch (error) {
            vscode.window.showErrorMessage(`創建測試文件失敗: ${error}`);
        }
    }
    
    private handleDeploymentResult(data: any): void {
        if (data.success) {
            vscode.window.showInformationMessage(
                `🎉 部署成功！${data.url ? ` 訪問地址: ${data.url}` : ''}`
            );
            
            if (data.url) {
                vscode.env.openExternal(vscode.Uri.parse(data.url));
            }
        } else {
            vscode.window.showErrorMessage(`部署失敗: ${data.error}`);
        }
    }
    
    public getStatus(): WorkflowStatus {
        return this._status;
    }
    
    public dispose(): void {
        this._onStatusChanged.dispose();
        this._outputChannel.dispose();
    }
}

