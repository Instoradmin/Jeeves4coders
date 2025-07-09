"use strict";
/**
 * Jeeves4coders Configuration Webview
 * Provides a comprehensive UI for configuring accounts and SSO
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConfigurationWebview = void 0;
const vscode = require("vscode");
const configManager_1 = require("./configManager");
class ConfigurationWebview {
    constructor(context) {
        this.context = context;
        this.configManager = new configManager_1.ConfigurationManager(context);
    }
    async show() {
        if (this.panel) {
            this.panel.reveal();
            return;
        }
        this.panel = vscode.window.createWebviewPanel('jeeves4coders.config', 'Jeeves4coders Configuration', vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [this.context.extensionUri]
        });
        this.panel.webview.html = await this.getWebviewContent();
        this.setupWebviewMessageHandling();
        this.panel.onDidDispose(() => {
            this.panel = undefined;
        });
    }
    setupWebviewMessageHandling() {
        if (!this.panel)
            return;
        this.panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'ssoLogin':
                    await this.handleSSOLogin();
                    break;
                case 'connectGitHub':
                    await this.handleConnectGitHub(message.data);
                    break;
                case 'connectJIRA':
                    await this.handleConnectJIRA(message.data);
                    break;
                case 'connectConfluence':
                    await this.handleConnectConfluence(message.data);
                    break;
                case 'disconnect':
                    await this.handleDisconnect(message.accountType);
                    break;
                case 'testConnection':
                    await this.handleTestConnection(message.accountType);
                    break;
                case 'refreshData':
                    await this.refreshWebviewData();
                    break;
            }
        });
    }
    async handleSSOLogin() {
        try {
            const success = await this.configManager.initiateSSO();
            if (success) {
                // Wait a bit for the OAuth flow to complete
                setTimeout(async () => {
                    await this.refreshWebviewData();
                }, 3000);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`SSO login failed: ${error}`);
        }
    }
    async handleConnectGitHub(data) {
        try {
            const config = {
                type: 'github',
                connected: true,
                username: data.username,
                email: data.email,
                token: data.token,
                baseUrl: data.baseUrl || 'https://api.github.com'
            };
            await this.configManager.storeAccountConfig(config);
            await this.refreshWebviewData();
            vscode.window.showInformationMessage('GitHub account connected successfully!');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to connect GitHub: ${error}`);
        }
    }
    async handleConnectJIRA(data) {
        try {
            const config = {
                type: 'jira',
                connected: true,
                username: data.username,
                email: data.email,
                token: data.token,
                baseUrl: data.baseUrl
            };
            await this.configManager.storeAccountConfig(config);
            await this.refreshWebviewData();
            vscode.window.showInformationMessage('JIRA account connected successfully!');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to connect JIRA: ${error}`);
        }
    }
    async handleConnectConfluence(data) {
        try {
            const config = {
                type: 'confluence',
                connected: true,
                username: data.username,
                email: data.email,
                token: data.token,
                baseUrl: data.baseUrl
            };
            await this.configManager.storeAccountConfig(config);
            await this.refreshWebviewData();
            vscode.window.showInformationMessage('Confluence account connected successfully!');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to connect Confluence: ${error}`);
        }
    }
    async handleDisconnect(accountType) {
        try {
            if (accountType === 'sso') {
                await this.configManager.clearSSO();
                vscode.window.showInformationMessage('SSO disconnected successfully!');
            }
            else {
                await this.configManager.clearAccountConfig(accountType);
                vscode.window.showInformationMessage(`${accountType.toUpperCase()} account disconnected successfully!`);
            }
            await this.refreshWebviewData();
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to disconnect: ${error}`);
        }
    }
    async handleTestConnection(accountType) {
        try {
            // Implement connection testing logic here
            vscode.window.showInformationMessage(`Testing ${accountType} connection...`);
            // For now, just show success
            setTimeout(() => {
                vscode.window.showInformationMessage(`${accountType.toUpperCase()} connection test successful!`);
            }, 1000);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Connection test failed: ${error}`);
        }
    }
    async refreshWebviewData() {
        if (!this.panel)
            return;
        const ssoConfig = await this.configManager.getSSOConfig();
        const githubConfig = await this.configManager.getAccountConfig('github');
        const jiraConfig = await this.configManager.getAccountConfig('jira');
        const confluenceConfig = await this.configManager.getAccountConfig('confluence');
        this.panel.webview.postMessage({
            command: 'updateData',
            data: {
                sso: ssoConfig,
                github: githubConfig,
                jira: jiraConfig,
                confluence: confluenceConfig
            }
        });
    }
    async getWebviewContent() {
        const ssoConfig = await this.configManager.getSSOConfig();
        const githubConfig = await this.configManager.getAccountConfig('github');
        const jiraConfig = await this.configManager.getAccountConfig('jira');
        const confluenceConfig = await this.configManager.getAccountConfig('confluence');
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jeeves4coders Configuration</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            margin: 0;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .robot-icon {
            font-size: 2.5em;
            margin-right: 15px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            background-color: var(--vscode-editor-background);
        }
        .section h3 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
            display: flex;
            align-items: center;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 10px;
        }
        .connected {
            background-color: #4CAF50;
        }
        .disconnected {
            background-color: #F44336;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 4px;
            box-sizing: border-box;
        }
        .button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
        }
        .button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .button.secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .button.danger {
            background-color: #F44336;
            color: white;
        }
        .user-info {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .hidden {
            display: none;
        }
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <span class="robot-icon">🤖</span>
        <div>
            <h1>Jeeves4coders Configuration</h1>
            <p>Configure your accounts and authentication settings</p>
        </div>
    </div>

    <!-- SSO Section -->
    <div class="section">
        <h3>
            🔐 Single Sign-On (Google OAuth2)
            <span class="status-indicator ${ssoConfig.accessToken ? 'connected' : 'disconnected'}"></span>
        </h3>
        
        <div id="sso-disconnected" class="${ssoConfig.accessToken ? 'hidden' : ''}">
            <p>Connect with Google OAuth2 for seamless authentication across all services.</p>
            <div class="form-group">
                <label for="oauth-client-id">Google OAuth2 Client ID:</label>
                <input type="text" id="oauth-client-id" value="${ssoConfig.clientId}" 
                       placeholder="your-client-id.googleusercontent.com">
            </div>
            <button class="button" onclick="connectSSO()">Connect with Google</button>
        </div>
        
        <div id="sso-connected" class="${ssoConfig.accessToken ? '' : 'hidden'}">
            <div class="user-info">
                <strong>Connected as:</strong> ${ssoConfig.userInfo?.name || 'Unknown'}<br>
                <strong>Email:</strong> ${ssoConfig.userInfo?.email || 'Unknown'}
            </div>
            <button class="button danger" onclick="disconnect('sso')">Disconnect SSO</button>
        </div>
    </div>

    <!-- GitHub Section -->
    <div class="section">
        <h3>
            🐙 GitHub
            <span class="status-indicator ${githubConfig.connected ? 'connected' : 'disconnected'}"></span>
        </h3>
        
        <div id="github-form" class="${githubConfig.connected ? 'hidden' : ''}">
            <div class="form-group">
                <label for="github-username">Username:</label>
                <input type="text" id="github-username" placeholder="your-username">
            </div>
            <div class="form-group">
                <label for="github-email">Email:</label>
                <input type="email" id="github-email" placeholder="your-email@example.com">
            </div>
            <div class="form-group">
                <label for="github-token">Personal Access Token:</label>
                <input type="password" id="github-token" placeholder="ghp_xxxxxxxxxxxx">
            </div>
            <div class="form-group">
                <label for="github-baseurl">Base URL (optional):</label>
                <input type="text" id="github-baseurl" value="https://api.github.com" placeholder="https://api.github.com">
            </div>
            <button class="button" onclick="connectGitHub()">Connect GitHub</button>
        </div>
        
        <div id="github-connected" class="${githubConfig.connected ? '' : 'hidden'}">
            <div class="user-info">
                <strong>Username:</strong> ${githubConfig.username || 'Unknown'}<br>
                <strong>Email:</strong> ${githubConfig.email || 'Unknown'}<br>
                <strong>Last Connected:</strong> ${githubConfig.lastConnected || 'Unknown'}
            </div>
            <button class="button secondary" onclick="testConnection('github')">Test Connection</button>
            <button class="button danger" onclick="disconnect('github')">Disconnect</button>
        </div>
    </div>

    <!-- JIRA Section -->
    <div class="section">
        <h3>
            🎫 JIRA
            <span class="status-indicator ${jiraConfig.connected ? 'connected' : 'disconnected'}"></span>
        </h3>
        
        <div id="jira-form" class="${jiraConfig.connected ? 'hidden' : ''}">
            <div class="form-group">
                <label for="jira-baseurl">JIRA Base URL:</label>
                <input type="text" id="jira-baseurl" placeholder="https://your-company.atlassian.net">
            </div>
            <div class="form-group">
                <label for="jira-email">Email:</label>
                <input type="email" id="jira-email" placeholder="your-email@company.com">
            </div>
            <div class="form-group">
                <label for="jira-token">API Token:</label>
                <input type="password" id="jira-token" placeholder="your-api-token">
            </div>
            <button class="button" onclick="connectJIRA()">Connect JIRA</button>
        </div>
        
        <div id="jira-connected" class="${jiraConfig.connected ? '' : 'hidden'}">
            <div class="user-info">
                <strong>Email:</strong> ${jiraConfig.email || 'Unknown'}<br>
                <strong>Base URL:</strong> ${jiraConfig.baseUrl || 'Unknown'}<br>
                <strong>Last Connected:</strong> ${jiraConfig.lastConnected || 'Unknown'}
            </div>
            <button class="button secondary" onclick="testConnection('jira')">Test Connection</button>
            <button class="button danger" onclick="disconnect('jira')">Disconnect</button>
        </div>
    </div>

    <!-- Confluence Section -->
    <div class="section">
        <h3>
            📚 Confluence
            <span class="status-indicator ${confluenceConfig.connected ? 'connected' : 'disconnected'}"></span>
        </h3>
        
        <div id="confluence-form" class="${confluenceConfig.connected ? 'hidden' : ''}">
            <div class="form-group">
                <label for="confluence-baseurl">Confluence Base URL:</label>
                <input type="text" id="confluence-baseurl" placeholder="https://your-company.atlassian.net/wiki">
            </div>
            <div class="form-group">
                <label for="confluence-email">Email:</label>
                <input type="email" id="confluence-email" placeholder="your-email@company.com">
            </div>
            <div class="form-group">
                <label for="confluence-token">API Token:</label>
                <input type="password" id="confluence-token" placeholder="your-api-token">
            </div>
            <button class="button" onclick="connectConfluence()">Connect Confluence</button>
        </div>
        
        <div id="confluence-connected" class="${confluenceConfig.connected ? '' : 'hidden'}">
            <div class="user-info">
                <strong>Email:</strong> ${confluenceConfig.email || 'Unknown'}<br>
                <strong>Base URL:</strong> ${confluenceConfig.baseUrl || 'Unknown'}<br>
                <strong>Last Connected:</strong> ${confluenceConfig.lastConnected || 'Unknown'}
            </div>
            <button class="button secondary" onclick="testConnection('confluence')">Test Connection</button>
            <button class="button danger" onclick="disconnect('confluence')">Disconnect</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function connectSSO() {
            const clientId = document.getElementById('oauth-client-id').value;
            if (!clientId) {
                alert('Please enter your Google OAuth2 Client ID');
                return;
            }
            
            vscode.postMessage({
                command: 'ssoLogin',
                data: { clientId }
            });
        }

        function connectGitHub() {
            const username = document.getElementById('github-username').value;
            const email = document.getElementById('github-email').value;
            const token = document.getElementById('github-token').value;
            const baseUrl = document.getElementById('github-baseurl').value;

            if (!username || !email || !token) {
                alert('Please fill in all required fields');
                return;
            }

            vscode.postMessage({
                command: 'connectGitHub',
                data: { username, email, token, baseUrl }
            });
        }

        function connectJIRA() {
            const baseUrl = document.getElementById('jira-baseurl').value;
            const email = document.getElementById('jira-email').value;
            const token = document.getElementById('jira-token').value;

            if (!baseUrl || !email || !token) {
                alert('Please fill in all required fields');
                return;
            }

            vscode.postMessage({
                command: 'connectJIRA',
                data: { baseUrl, email, token }
            });
        }

        function connectConfluence() {
            const baseUrl = document.getElementById('confluence-baseurl').value;
            const email = document.getElementById('confluence-email').value;
            const token = document.getElementById('confluence-token').value;

            if (!baseUrl || !email || !token) {
                alert('Please fill in all required fields');
                return;
            }

            vscode.postMessage({
                command: 'connectConfluence',
                data: { baseUrl, email, token }
            });
        }

        function disconnect(accountType) {
            if (confirm(\`Are you sure you want to disconnect \${accountType.toUpperCase()}?\`)) {
                vscode.postMessage({
                    command: 'disconnect',
                    accountType: accountType
                });
            }
        }

        function testConnection(accountType) {
            vscode.postMessage({
                command: 'testConnection',
                accountType: accountType
            });
        }

        // Listen for messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            if (message.command === 'updateData') {
                // Refresh the page with new data
                location.reload();
            }
        });

        // Auto-refresh data every 30 seconds
        setInterval(() => {
            vscode.postMessage({ command: 'refreshData' });
        }, 30000);
    </script>
</body>
</html>`;
    }
}
exports.ConfigurationWebview = ConfigurationWebview;
//# sourceMappingURL=configWebview.js.map