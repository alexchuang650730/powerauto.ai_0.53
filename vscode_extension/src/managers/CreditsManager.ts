import * as vscode from 'vscode';
import { WebSocketClient } from '../services/WebSocketClient';

export interface CreditsInfo {
    current: number;
    total: number;
    used: number;
    lastUpdated: Date;
    monthlyUsage: number;
    costSaved: number;
}

export interface CreditsTransaction {
    id: string;
    type: 'purchase' | 'usage' | 'refund';
    amount: number;
    description: string;
    timestamp: Date;
    status: 'completed' | 'pending' | 'failed';
}

export class CreditsManager {
    private _onCreditsChanged = new vscode.EventEmitter<number>();
    public readonly onCreditsChanged = this._onCreditsChanged.event;
    
    private _creditsInfo: CreditsInfo;
    private _outputChannel: vscode.OutputChannel;
    private _statusBarItem: vscode.StatusBarItem;
    
    constructor(private webSocketClient: WebSocketClient) {
        this._outputChannel = vscode.window.createOutputChannel('PowerAutomation Credits');
        this._creditsInfo = this.initializeCreditsInfo();
        
        // 創建狀態欄項目
        this._statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this._statusBarItem.command = 'powerautomation.refreshCredits';
        this._statusBarItem.tooltip = '點擊刷新積分';
        this.updateStatusBar();
        
        // 監聽WebSocket消息
        this.webSocketClient.onMessage('credits_update', (data) => {
            this.handleCreditsUpdate(data);
        });
        
        // 定期刷新積分
        this.startPeriodicRefresh();
    }
    
    private initializeCreditsInfo(): CreditsInfo {
        return {
            current: 1247, // 默認積分
            total: 2000,
            used: 753,
            lastUpdated: new Date(),
            monthlyUsage: 753,
            costSaved: 342.50
        };
    }
    
    public async refreshCredits(): Promise<void> {
        try {
            this._outputChannel.appendLine('🔄 刷新積分信息...');
            
            // 發送積分查詢請求
            this.webSocketClient.send('get_credits_info', {
                user_id: this.getUserId()
            });
            
            // 顯示刷新狀態
            vscode.window.setStatusBarMessage('$(sync~spin) 刷新積分中...', 2000);
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 刷新積分失敗: ${error}`);
            vscode.window.showErrorMessage(`刷新積分失敗: ${error}`);
        }
    }
    
    public async purchaseCredits(): Promise<void> {
        try {
            // 顯示購買選項
            const options = [
                {
                    label: '$(star) 基礎包',
                    description: '500 積分',
                    detail: '$9.99 - 適合個人開發者',
                    credits: 500,
                    price: 9.99
                },
                {
                    label: '$(star-full) 專業包',
                    description: '1500 積分',
                    detail: '$24.99 - 最受歡迎，節省17%',
                    credits: 1500,
                    price: 24.99
                },
                {
                    label: '$(crown) 企業包',
                    description: '5000 積分',
                    detail: '$79.99 - 企業級，節省33%',
                    credits: 5000,
                    price: 79.99
                }
            ];
            
            const selected = await vscode.window.showQuickPick(options, {
                placeHolder: '選擇積分包'
            });
            
            if (selected) {
                // 確認購買
                const confirm = await vscode.window.showInformationMessage(
                    `確認購買 ${selected.credits} 積分，價格 $${selected.price}？`,
                    '確認購買',
                    '取消'
                );
                
                if (confirm === '確認購買') {
                    await this.processPurchase(selected.credits, selected.price);
                }
            }
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 購買積分失敗: ${error}`);
            vscode.window.showErrorMessage(`購買積分失敗: ${error}`);
        }
    }
    
    public async openPurchasePage(): Promise<void> {
        try {
            // 獲取購買頁面URL
            const config = vscode.workspace.getConfiguration('powerautomation');
            const purchaseUrl = config.get<string>('purchaseUrl', 'https://powerauto.ai/purchase');
            
            // 添加用戶ID參數
            const urlWithParams = `${purchaseUrl}?user_id=${this.getUserId()}&source=vscode`;
            
            // 在外部瀏覽器中打開
            await vscode.env.openExternal(vscode.Uri.parse(urlWithParams));
            
            vscode.window.showInformationMessage('已在瀏覽器中打開購買頁面');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 打開購買頁面失敗: ${error}`);
            vscode.window.showErrorMessage(`打開購買頁面失敗: ${error}`);
        }
    }
    
    private async processPurchase(credits: number, price: number): Promise<void> {
        try {
            this._outputChannel.appendLine(`💰 處理購買: ${credits} 積分, $${price}`);
            
            // 發送購買請求
            this.webSocketClient.send('purchase_credits', {
                user_id: this.getUserId(),
                credits: credits,
                price: price,
                currency: 'USD'
            });
            
            vscode.window.showInformationMessage('正在處理購買請求...');
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 處理購買失敗: ${error}`);
            vscode.window.showErrorMessage(`處理購買失敗: ${error}`);
        }
    }
    
    public async useCredits(amount: number, description: string): Promise<boolean> {
        try {
            if (this._creditsInfo.current < amount) {
                const purchase = await vscode.window.showWarningMessage(
                    `積分不足！當前積分: ${this._creditsInfo.current}，需要: ${amount}`,
                    '購買積分',
                    '取消'
                );
                
                if (purchase === '購買積分') {
                    await this.purchaseCredits();
                }
                return false;
            }
            
            // 發送使用積分請求
            this.webSocketClient.send('use_credits', {
                user_id: this.getUserId(),
                amount: amount,
                description: description
            });
            
            // 本地更新（服務器確認後會同步）
            this._creditsInfo.current -= amount;
            this._creditsInfo.used += amount;
            this._creditsInfo.monthlyUsage += amount;
            this._creditsInfo.lastUpdated = new Date();
            
            this.updateStatusBar();
            this._onCreditsChanged.fire(this._creditsInfo.current);
            
            this._outputChannel.appendLine(`💸 使用積分: ${amount} - ${description}`);
            
            return true;
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 使用積分失敗: ${error}`);
            vscode.window.showErrorMessage(`使用積分失敗: ${error}`);
            return false;
        }
    }
    
    public async getTransactionHistory(): Promise<CreditsTransaction[]> {
        try {
            // 發送交易歷史請求
            this.webSocketClient.send('get_transaction_history', {
                user_id: this.getUserId(),
                limit: 50
            });
            
            // 返回模擬數據（實際應該等待服務器響應）
            return [
                {
                    id: '1',
                    type: 'purchase',
                    amount: 1500,
                    description: '購買專業包',
                    timestamp: new Date(Date.now() - 86400000),
                    status: 'completed'
                },
                {
                    id: '2',
                    type: 'usage',
                    amount: -50,
                    description: 'AI代碼生成',
                    timestamp: new Date(Date.now() - 3600000),
                    status: 'completed'
                },
                {
                    id: '3',
                    type: 'usage',
                    amount: -30,
                    description: '自動化測試生成',
                    timestamp: new Date(Date.now() - 1800000),
                    status: 'completed'
                }
            ];
            
        } catch (error) {
            this._outputChannel.appendLine(`❌ 獲取交易歷史失敗: ${error}`);
            return [];
        }
    }
    
    public async showCreditsPanel(): Promise<void> {
        // 創建並顯示積分管理面板
        const panel = vscode.window.createWebviewPanel(
            'powerautomation.credits',
            'PowerAutomation 積分管理',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = await this.getCreditsWebviewContent();
        
        // 處理來自webview的消息
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'refresh':
                        await this.refreshCredits();
                        break;
                    case 'purchase':
                        await this.purchaseCredits();
                        break;
                    case 'getTransactions':
                        const transactions = await this.getTransactionHistory();
                        panel.webview.postMessage({
                            command: 'transactionsData',
                            data: transactions
                        });
                        break;
                }
            },
            undefined,
            []
        );
        
        // 監聽積分變化並更新webview
        const disposable = this.onCreditsChanged((credits) => {
            panel.webview.postMessage({
                command: 'creditsUpdate',
                data: this._creditsInfo
            });
        });
        
        panel.onDidDispose(() => {
            disposable.dispose();
        });
    }
    
    private async getCreditsWebviewContent(): Promise<string> {
        const transactions = await this.getTransactionHistory();
        
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>積分管理</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .title {
            font-size: 24px;
            font-weight: 600;
        }
        
        .refresh-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
        }
        
        .credits-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .credit-card {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .credit-value {
            font-size: 28px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 4px;
        }
        
        .credit-label {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .purchase-section {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
        }
        
        .purchase-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        
        .purchase-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }
        
        .purchase-option {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .purchase-option:hover {
            border-color: var(--vscode-focusBorder);
        }
        
        .option-credits {
            font-size: 20px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        
        .option-price {
            font-size: 16px;
            margin: 4px 0;
        }
        
        .option-description {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .transactions-section {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 20px;
        }
        
        .transactions-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .transaction-item:last-child {
            border-bottom: none;
        }
        
        .transaction-info {
            flex: 1;
        }
        
        .transaction-description {
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .transaction-time {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .transaction-amount {
            font-weight: bold;
        }
        
        .transaction-amount.positive {
            color: #10B981;
        }
        
        .transaction-amount.negative {
            color: #EF4444;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">💰 積分管理</div>
        <button class="refresh-btn" onclick="refreshCredits()">🔄 刷新</button>
    </div>
    
    <div class="credits-overview">
        <div class="credit-card">
            <div class="credit-value">${this._creditsInfo.current.toLocaleString()}</div>
            <div class="credit-label">當前積分</div>
        </div>
        <div class="credit-card">
            <div class="credit-value">${this._creditsInfo.monthlyUsage.toLocaleString()}</div>
            <div class="credit-label">本月使用</div>
        </div>
        <div class="credit-card">
            <div class="credit-value">$${this._creditsInfo.costSaved.toFixed(2)}</div>
            <div class="credit-label">節省成本</div>
        </div>
        <div class="credit-card">
            <div class="credit-value">${Math.round((this._creditsInfo.current / this._creditsInfo.total) * 100)}%</div>
            <div class="credit-label">剩餘比例</div>
        </div>
    </div>
    
    <div class="purchase-section">
        <div class="purchase-title">購買積分</div>
        <div class="purchase-options">
            <div class="purchase-option" onclick="purchaseCredits(500, 9.99)">
                <div class="option-credits">500 積分</div>
                <div class="option-price">$9.99</div>
                <div class="option-description">基礎包 - 適合個人開發者</div>
            </div>
            <div class="purchase-option" onclick="purchaseCredits(1500, 24.99)">
                <div class="option-credits">1500 積分</div>
                <div class="option-price">$24.99</div>
                <div class="option-description">專業包 - 最受歡迎，節省17%</div>
            </div>
            <div class="purchase-option" onclick="purchaseCredits(5000, 79.99)">
                <div class="option-credits">5000 積分</div>
                <div class="option-price">$79.99</div>
                <div class="option-description">企業包 - 企業級，節省33%</div>
            </div>
        </div>
    </div>
    
    <div class="transactions-section">
        <div class="transactions-title">交易記錄</div>
        <div id="transactions-list">
            ${transactions.map(t => `
                <div class="transaction-item">
                    <div class="transaction-info">
                        <div class="transaction-description">${t.description}</div>
                        <div class="transaction-time">${t.timestamp.toLocaleString()}</div>
                    </div>
                    <div class="transaction-amount ${t.amount > 0 ? 'positive' : 'negative'}">
                        ${t.amount > 0 ? '+' : ''}${t.amount.toLocaleString()}
                    </div>
                </div>
            `).join('')}
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function refreshCredits() {
            vscode.postMessage({ command: 'refresh' });
        }
        
        function purchaseCredits(credits, price) {
            vscode.postMessage({ 
                command: 'purchase',
                credits: credits,
                price: price
            });
        }
        
        // 監聽來自擴展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'creditsUpdate':
                    updateCreditsDisplay(message.data);
                    break;
                case 'transactionsData':
                    updateTransactionsList(message.data);
                    break;
            }
        });
        
        function updateCreditsDisplay(creditsInfo) {
            // 更新積分顯示
            console.log('Credits updated:', creditsInfo);
        }
        
        function updateTransactionsList(transactions) {
            // 更新交易列表
            console.log('Transactions updated:', transactions);
        }
    </script>
</body>
</html>`;
    }
    
    private handleCreditsUpdate(data: any): void {
        this._outputChannel.appendLine(`💰 積分更新: ${JSON.stringify(data)}`);
        
        if (data.current !== undefined) {
            this._creditsInfo.current = data.current;
        }
        if (data.used !== undefined) {
            this._creditsInfo.used = data.used;
        }
        if (data.monthlyUsage !== undefined) {
            this._creditsInfo.monthlyUsage = data.monthlyUsage;
        }
        if (data.costSaved !== undefined) {
            this._creditsInfo.costSaved = data.costSaved;
        }
        
        this._creditsInfo.lastUpdated = new Date();
        
        this.updateStatusBar();
        this._onCreditsChanged.fire(this._creditsInfo.current);
        
        // 處理購買結果
        if (data.type === 'purchase_result') {
            if (data.success) {
                vscode.window.showInformationMessage(
                    `🎉 購買成功！獲得 ${data.credits} 積分`
                );
            } else {
                vscode.window.showErrorMessage(`購買失敗: ${data.error}`);
            }
        }
    }
    
    private updateStatusBar(): void {
        this._statusBarItem.text = `$(star) ${this._creditsInfo.current.toLocaleString()}`;
        this._statusBarItem.show();
    }
    
    private startPeriodicRefresh(): void {
        // 每5分鐘自動刷新一次積分
        setInterval(() => {
            this.refreshCredits();
        }, 5 * 60 * 1000);
    }
    
    private getUserId(): string {
        // 從配置或認證信息獲取用戶ID
        const config = vscode.workspace.getConfiguration('powerautomation');
        return config.get<string>('userId', 'default_user');
    }
    
    public getCreditsInfo(): CreditsInfo {
        return this._creditsInfo;
    }
    
    public dispose(): void {
        this._onCreditsChanged.dispose();
        this._outputChannel.dispose();
        this._statusBarItem.dispose();
    }
}

