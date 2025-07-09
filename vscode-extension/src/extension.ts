/**
 * Jeeves4coders VS Code Extension
 * Your intelligent coding assistant integrated into VS Code
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {
    console.log('Jeeves4coders extension is now active!');

    // Initialize status bar
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = "$(robot) Jeeves4coders";
    statusBarItem.tooltip = "Click to open Jeeves4coders";
    statusBarItem.command = 'jeeves4coders.showStatus';
    statusBarItem.show();

    // Register commands
    const commands = [
        vscode.commands.registerCommand('jeeves4coders.init', initializeJeeves),
        vscode.commands.registerCommand('jeeves4coders.runWorkflow', runWorkflow),
        vscode.commands.registerCommand('jeeves4coders.runTests', runTests),
        vscode.commands.registerCommand('jeeves4coders.codeReview', runCodeReview),
        vscode.commands.registerCommand('jeeves4coders.showStatus', showStatus),
        vscode.commands.registerCommand('jeeves4coders.openSettings', openSettings)
    ];

    // Register providers
    const statusProvider = new JeevesStatusProvider();
    const workflowProvider = new JeevesWorkflowProvider();
    const resultsProvider = new JeevesResultsProvider();

    vscode.window.registerTreeDataProvider('jeeves4coders.status', statusProvider);
    vscode.window.registerTreeDataProvider('jeeves4coders.workflows', workflowProvider);
    vscode.window.registerTreeDataProvider('jeeves4coders.results', resultsProvider);

    // Auto-run on file save if enabled
    const onSaveDisposable = vscode.workspace.onDidSaveTextDocument(async (document) => {
        const config = vscode.workspace.getConfiguration('jeeves4coders');
        if (config.get('autoRun')) {
            await runWorkflow();
        }
    });

    context.subscriptions.push(statusBarItem, onSaveDisposable, ...commands);

    // Set context for when extension is enabled
    vscode.commands.executeCommand('setContext', 'jeeves4coders.enabled', true);
}

async function initializeJeeves() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('Please open a workspace folder first');
        return;
    }

    try {
        vscode.window.showInformationMessage('Initializing Jeeves4coders...');
        
        const terminal = vscode.window.createTerminal('Jeeves4coders Init');
        terminal.sendText('npx jeeves4coders init');
        terminal.show();

        vscode.window.showInformationMessage('Jeeves4coders initialization started in terminal');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to initialize Jeeves4coders: ${error}`);
    }
}

async function runWorkflow() {
    const config = vscode.workspace.getConfiguration('jeeves4coders');
    const defaultWorkflow = config.get('defaultWorkflow', 'code_quality');

    const workflows = ['code_quality', 'full_analysis', 'testing_only', 'ci_cd', 'deployment'];
    
    const selectedWorkflow = await vscode.window.showQuickPick(workflows, {
        placeHolder: `Select workflow (default: ${defaultWorkflow})`,
        canPickMany: false
    });

    if (!selectedWorkflow) {
        return;
    }

    try {
        vscode.window.showInformationMessage(`Running ${selectedWorkflow} workflow...`);
        
        const terminal = vscode.window.createTerminal('Jeeves4coders Workflow');
        terminal.sendText(`npx jeeves4coders workflow ${selectedWorkflow}`);
        terminal.show();

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to run workflow: ${error}`);
    }
}

async function runTests() {
    const testTypes = ['unit', 'functional', 'integration', 'regression', 'performance', 'security', 'all'];
    
    const selectedTests = await vscode.window.showQuickPick(testTypes, {
        placeHolder: 'Select test types to run',
        canPickMany: true
    });

    if (!selectedTests || selectedTests.length === 0) {
        return;
    }

    try {
        vscode.window.showInformationMessage(`Running ${selectedTests.join(', ')} tests...`);
        
        const terminal = vscode.window.createTerminal('Jeeves4coders Tests');
        if (selectedTests.includes('all')) {
            terminal.sendText('npm run jeeves:test');
        } else {
            terminal.sendText(`npx jeeves4coders run test_suite --types ${selectedTests.join(',')}`);
        }
        terminal.show();

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to run tests: ${error}`);
    }
}

async function runCodeReview() {
    const activeEditor = vscode.window.activeTextEditor;
    let targetFile = '';

    if (activeEditor) {
        targetFile = ` --file "${activeEditor.document.fileName}"`;
    }

    try {
        vscode.window.showInformationMessage('Running code review...');
        
        const terminal = vscode.window.createTerminal('Jeeves4coders Code Review');
        terminal.sendText(`npx jeeves4coders run code_review${targetFile}`);
        terminal.show();

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to run code review: ${error}`);
    }
}

async function showStatus() {
    try {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('Please open a workspace folder first');
            return;
        }

        // Check if Jeeves4coders is installed
        const { stdout } = await execAsync('npx jeeves4coders version', { 
            cwd: workspaceFolder.uri.fsPath 
        });

        const panel = vscode.window.createWebviewPanel(
            'jeeves4coders.status',
            'Jeeves4coders Status',
            vscode.ViewColumn.One,
            {
                enableScripts: true
            }
        );

        panel.webview.html = getStatusWebviewContent(stdout);

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to get status: ${error}`);
    }
}

async function openSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'jeeves4coders');
}

function getStatusWebviewContent(statusInfo: string): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jeeves4coders Status</title>
        <style>
            body {
                font-family: var(--vscode-font-family);
                color: var(--vscode-foreground);
                background-color: var(--vscode-editor-background);
                padding: 20px;
            }
            .header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            .robot-icon {
                font-size: 2em;
                margin-right: 10px;
            }
            .status-section {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid var(--vscode-panel-border);
                border-radius: 5px;
            }
            .status-good {
                border-left: 4px solid #4CAF50;
            }
            .status-warning {
                border-left: 4px solid #FF9800;
            }
            .status-error {
                border-left: 4px solid #F44336;
            }
            pre {
                background-color: var(--vscode-textCodeBlock-background);
                padding: 10px;
                border-radius: 3px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <span class="robot-icon">🤖</span>
            <h1>Jeeves4coders Status</h1>
        </div>
        
        <div class="status-section status-good">
            <h3>✅ Installation Status</h3>
            <p>Jeeves4coders is installed and ready to assist you!</p>
            <pre>${statusInfo}</pre>
        </div>
        
        <div class="status-section">
            <h3>🚀 Quick Actions</h3>
            <p>Use the Command Palette (Ctrl+Shift+P) and search for "Jeeves4coders" to access all features:</p>
            <ul>
                <li><strong>Initialize:</strong> Set up Jeeves4coders for your project</li>
                <li><strong>Run Workflow:</strong> Execute automation workflows</li>
                <li><strong>Run Tests:</strong> Execute comprehensive test suites</li>
                <li><strong>Code Review:</strong> Analyze code quality</li>
            </ul>
        </div>
        
        <div class="status-section">
            <h3>⚙️ Configuration</h3>
            <p>Configure Jeeves4coders in VS Code settings or create a <code>.jeeves4coders.json</code> file in your project root.</p>
        </div>
    </body>
    </html>`;
}

// Tree Data Providers
class JeevesStatusProvider implements vscode.TreeDataProvider<StatusItem> {
    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: StatusItem): Thenable<StatusItem[]> {
        if (!element) {
            return Promise.resolve([
                new StatusItem('Installation', 'Checking...', vscode.TreeItemCollapsibleState.None),
                new StatusItem('Configuration', 'Loading...', vscode.TreeItemCollapsibleState.None),
                new StatusItem('Last Run', 'Never', vscode.TreeItemCollapsibleState.None)
            ]);
        }
        return Promise.resolve([]);
    }
}

class JeevesWorkflowProvider implements vscode.TreeDataProvider<WorkflowItem> {
    getTreeItem(element: WorkflowItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: WorkflowItem): Thenable<WorkflowItem[]> {
        if (!element) {
            return Promise.resolve([
                new WorkflowItem('code_quality', 'Code Quality Analysis'),
                new WorkflowItem('full_analysis', 'Full Analysis'),
                new WorkflowItem('testing_only', 'Testing Only'),
                new WorkflowItem('ci_cd', 'CI/CD Pipeline'),
                new WorkflowItem('deployment', 'Deployment')
            ]);
        }
        return Promise.resolve([]);
    }
}

class JeevesResultsProvider implements vscode.TreeDataProvider<ResultItem> {
    getTreeItem(element: ResultItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ResultItem): Thenable<ResultItem[]> {
        if (!element) {
            return Promise.resolve([
                new ResultItem('Last Test Results', 'No results yet'),
                new ResultItem('Code Quality', 'No analysis yet'),
                new ResultItem('Build Status', 'No builds yet')
            ]);
        }
        return Promise.resolve([]);
    }
}

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}: ${this.description}`;
        this.description = description;
    }
}

class WorkflowItem extends vscode.TreeItem {
    constructor(
        public readonly workflow: string,
        public readonly description: string
    ) {
        super(description, vscode.TreeItemCollapsibleState.None);
        this.tooltip = `Run ${description}`;
        this.command = {
            command: 'jeeves4coders.runWorkflow',
            title: 'Run Workflow',
            arguments: [workflow]
        };
        this.contextValue = 'workflow';
    }
}

class ResultItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = `${this.label}: ${this.description}`;
        this.description = description;
    }
}

export function deactivate() {
    console.log('Jeeves4coders extension is now deactivated');
}
