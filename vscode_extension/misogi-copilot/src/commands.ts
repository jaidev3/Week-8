import * as vscode from 'vscode';
import { OpenAIService } from './openaiService';

export class MisogiCommands {
    private openaiService: OpenAIService;

    constructor(openaiService: OpenAIService) {
        this.openaiService = openaiService;
    }

    public registerCommands(context: vscode.ExtensionContext): void {
        // Register the complete code command
        const completeCodeCommand = vscode.commands.registerCommand('extension.completeCode', async () => {
            await this.completeCode();
        });

        // Register the suggest code command
        const suggestCodeCommand = vscode.commands.registerCommand('extension.suggestCode', async () => {
            await this.suggestCode();
        });

        // Register the configure API key command
        const configureApiKeyCommand = vscode.commands.registerCommand('extension.configureApiKey', async () => {
            await this.configureApiKey();
        });

        context.subscriptions.push(completeCodeCommand, suggestCodeCommand, configureApiKeyCommand);
    }

    private async completeCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        if (!this.openaiService.isConfigured()) {
            vscode.window.showErrorMessage('OpenAI API key not configured. Please run "Misogi Copilot: Configure API Key" command.');
            return;
        }

        const document = editor.document;
        const position = editor.selection.active;
        const currentLine = document.lineAt(position.line);
        const textBeforeCursor = currentLine.text.substring(0, position.character);

        if (textBeforeCursor.trim() === '') {
            vscode.window.showInformationMessage('Place cursor after some code to get completion');
            return;
        }

        try {
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Misogi Copilot",
                cancellable: false
            }, async (progress) => {
                progress.report({ message: "Getting AI code completion..." });

                // Get surrounding context
                const startLine = Math.max(0, position.line - 10);
                const endLine = Math.min(document.lineCount - 1, position.line + 10);
                const contextRange = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
                const context = document.getText(contextRange);

                const language = document.languageId;
                const completion = await this.openaiService.getCodeCompletion(textBeforeCursor, language, context);

                if (completion && completion.trim() !== '') {
                    // Insert the completion at the cursor position
                    await editor.edit(editBuilder => {
                        editBuilder.insert(position, completion);
                    });
                    
                    vscode.window.showInformationMessage('Code completion inserted!');
                } else {
                    vscode.window.showInformationMessage('No completion suggestions available');
                }
            });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            vscode.window.showErrorMessage(`Failed to get code completion: ${errorMessage}`);
        }
    }

    private async suggestCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        if (!this.openaiService.isConfigured()) {
            vscode.window.showErrorMessage('OpenAI API key not configured. Please run "Misogi Copilot: Configure API Key" command.');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showErrorMessage('Please select some code to get suggestions');
            return;
        }

        const selectedText = editor.document.getText(selection);
        const language = editor.document.languageId;

        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Misogi Copilot",
                cancellable: false
            }, async (progress) => {
                progress.report({ message: "Analyzing code and generating suggestions..." });

                const suggestions = await this.openaiService.getCodeSuggestions(selectedText, language);

                if (suggestions && suggestions.trim() !== '') {
                    // Show suggestions in a new document
                    const doc = await vscode.workspace.openTextDocument({
                        content: `# Code Suggestions from Misogi Copilot\n\n## Original Code:\n\`\`\`${language}\n${selectedText}\n\`\`\`\n\n## Suggestions:\n\n${suggestions}`,
                        language: 'markdown'
                    });
                    
                    await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                } else {
                    vscode.window.showInformationMessage('No suggestions available for the selected code');
                }
            });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            vscode.window.showErrorMessage(`Failed to get code suggestions: ${errorMessage}`);
        }
    }

    private async configureApiKey(): Promise<void> {
        const options = [
            'Create .env file (Recommended)',
            'Use VS Code Settings',
            'Cancel'
        ];

        const choice = await vscode.window.showQuickPick(options, {
            placeHolder: 'How would you like to configure your OpenAI API key?'
        });

        if (!choice || choice === 'Cancel') {
            return;
        }

        if (choice === 'Create .env file (Recommended)') {
            await this.createEnvFile();
        } else if (choice === 'Use VS Code Settings') {
            await this.configureViaSettings();
        }
    }

    private async createEnvFile(): Promise<void> {
        if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('Please open a workspace folder first to create a .env file.');
            return;
        }

        const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
        const envPath = vscode.Uri.file(workspaceRoot + '/.env');

        try {
            // Check if .env already exists
            try {
                await vscode.workspace.fs.stat(envPath);
                const overwrite = await vscode.window.showWarningMessage(
                    '.env file already exists. Do you want to open it for editing?',
                    'Open File',
                    'Cancel'
                );
                
                if (overwrite === 'Open File') {
                    const doc = await vscode.workspace.openTextDocument(envPath);
                    await vscode.window.showTextDocument(doc);
                }
                return;
            } catch {
                // File doesn't exist, continue to create it
            }

            const apiKey = await vscode.window.showInputBox({
                prompt: 'Enter your OpenAI API Key',
                password: true,
                placeHolder: 'sk-...',
                validateInput: (value) => {
                    if (!value || value.trim() === '') {
                        return 'API key cannot be empty';
                    }
                    if (!value.startsWith('sk-')) {
                        return 'OpenAI API keys typically start with "sk-"';
                    }
                    return null;
                }
            });

            if (apiKey) {
                const envContent = `# Misogi Copilot Environment Variables
# Your OpenAI API Key
OPENAI_API_KEY=${apiKey.trim()}

# Optional: Organization ID (if you have one)
# OPENAI_ORG_ID=your-org-id-here
`;

                await vscode.workspace.fs.writeFile(envPath, Buffer.from(envContent, 'utf8'));
                
                vscode.window.showInformationMessage(
                    'OpenAI API key configured successfully in .env file!',
                    'Open .env File'
                ).then(selection => {
                    if (selection === 'Open .env File') {
                        vscode.workspace.openTextDocument(envPath).then(doc => {
                            vscode.window.showTextDocument(doc);
                        });
                    }
                });
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create .env file: ${error}`);
        }
    }

    private async configureViaSettings(): Promise<void> {
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your OpenAI API Key',
            password: true,
            placeHolder: 'sk-...',
            validateInput: (value) => {
                if (!value || value.trim() === '') {
                    return 'API key cannot be empty';
                }
                if (!value.startsWith('sk-')) {
                    return 'OpenAI API keys typically start with "sk-"';
                }
                return null;
            }
        });

        if (apiKey) {
            const config = vscode.workspace.getConfiguration('misogiCopilot');
            await config.update('openaiApiKey', apiKey.trim(), vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage('OpenAI API key configured successfully in VS Code settings!');
        }
    }
}