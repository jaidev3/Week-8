// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { OpenAIService } from './openaiService';
import { MisogiCompletionProvider } from './completionProvider';
import { MisogiHoverProvider } from './hoverProvider';
import { MisogiCommands } from './commands';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
	console.log('Misogi Copilot is now active!');

	// Initialize the OpenAI service
	const openaiService = new OpenAIService();

	// Initialize the completion provider
	const completionProvider = new MisogiCompletionProvider(openaiService);
	
	// Register the inline completion provider for all languages
	const completionProviderDisposable = vscode.languages.registerInlineCompletionItemProvider(
		{ pattern: '**' }, // All files
		completionProvider
	);

	// Initialize and register hover provider
	const hoverProvider = new MisogiHoverProvider(openaiService);
	const hoverProviderDisposable = vscode.languages.registerHoverProvider(
		{ pattern: '**' }, // All files
		hoverProvider
	);

	// Initialize and register commands
	const commands = new MisogiCommands(openaiService);
	commands.registerCommands(context);

	// Add status bar item to show extension status
	const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
	statusBarItem.text = '$(robot) Misogi Copilot';
	statusBarItem.tooltip = 'Misogi Copilot AI Assistant';
	statusBarItem.command = 'extension.configureApiKey';
	
	// Update status bar based on configuration
	const updateStatusBar = () => {
		if (openaiService.isConfigured()) {
			statusBarItem.text = '$(robot) Misogi Copilot ✓';
			statusBarItem.tooltip = 'Misogi Copilot AI Assistant - Ready';
			statusBarItem.backgroundColor = undefined;
		} else {
			statusBarItem.text = '$(robot) Misogi Copilot ⚠';
			statusBarItem.tooltip = 'Misogi Copilot AI Assistant - API Key Required';
			statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
		}
	};

	updateStatusBar();
	statusBarItem.show();

	// Listen for configuration changes to update status
	const configChangeDisposable = vscode.workspace.onDidChangeConfiguration((e) => {
		if (e.affectsConfiguration('misogiCopilot.openaiApiKey')) {
			updateStatusBar();
		}
	});

	// Show welcome message with setup instructions
	if (!openaiService.isConfigured()) {
		vscode.window.showInformationMessage(
			'Welcome to Misogi Copilot! Please configure your OpenAI API key to get started.',
			'Configure API Key'
		).then(selection => {
			if (selection === 'Configure API Key') {
				vscode.commands.executeCommand('extension.configureApiKey');
			}
		});
	}

	// Add all disposables to context
	context.subscriptions.push(
		completionProviderDisposable,
		hoverProviderDisposable,
		statusBarItem,
		configChangeDisposable
	);
}

// This method is called when your extension is deactivated
export function deactivate() {
	console.log('Misogi Copilot has been deactivated');
}
