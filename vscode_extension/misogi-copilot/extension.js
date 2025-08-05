"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
async function getCompletion(prompt) {
    const config = vscode.workspace.getConfiguration('misogiCopilot');
    const apiKey = config.get('openaiApiKey') || process.env.OPENAI_API_KEY;
    if (!apiKey) {
        vscode.window.showErrorMessage('OpenAI API key not configured. Please set it in settings or environment variable OPENAI_API_KEY.');
        return '';
    }
    const url = 'https://api.openai.com/v1/chat/completions';
    const maxTokens = config.get('maxTokens') || 150;
    const temperature = config.get('temperature') || 0.7;
    const model = config.get('model') || 'gpt-3.5-turbo';
    try {
        const response = await axios_1.default.post(url, {
            model: model,
            messages: [
                {
                    role: 'system',
                    content: 'You are a helpful coding assistant. Complete the code based on the context provided. Only return the completion, no explanations.'
                },
                {
                    role: 'user',
                    content: `Complete this code:\n\n${prompt}`
                }
            ],
            max_tokens: maxTokens,
            temperature: temperature,
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
        });
        return response.data.choices[0].message.content.trim();
    }
    catch (error) {
        console.error('Error fetching completion:', error);
        if (error.response?.status === 401) {
            vscode.window.showErrorMessage('Invalid OpenAI API key. Please check your configuration.');
        }
        else if (error.response?.status === 429) {
            vscode.window.showErrorMessage('OpenAI API rate limit exceeded. Please try again later.');
        }
        else {
            vscode.window.showErrorMessage(`Error getting completion: ${error.message}`);
        }
        return '';
    }
}
async function getCodeSuggestion(context, language) {
    const config = vscode.workspace.getConfiguration('misogiCopilot');
    const apiKey = config.get('openaiApiKey') || process.env.OPENAI_API_KEY;
    if (!apiKey) {
        return '';
    }
    const url = 'https://api.openai.com/v1/chat/completions';
    const model = config.get('model') || 'gpt-3.5-turbo';
    try {
        const response = await axios_1.default.post(url, {
            model: model,
            messages: [
                {
                    role: 'system',
                    content: `You are a ${language} coding assistant. Provide helpful code suggestions and completions. Keep responses concise and focused on code.`
                },
                {
                    role: 'user',
                    content: context
                }
            ],
            max_tokens: 200,
            temperature: 0.3,
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
        });
        return response.data.choices[0].message.content.trim();
    }
    catch (error) {
        console.error('Error getting code suggestion:', error);
        return '';
    }
}
function activate(context) {
    console.log('Misogi Copilot extension is now active!');
    // Command for code completion
    const completeCodeDisposable = vscode.commands.registerCommand('extension.completeCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor found.');
            return;
        }
        const position = editor.selection.active;
        const textBeforeCursor = editor.document.getText(new vscode.Range(new vscode.Position(0, 0), position));
        // Show progress indicator
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Getting code completion...",
            cancellable: false
        }, async (progress) => {
            const completion = await getCompletion(textBeforeCursor);
            if (completion) {
                await editor.insertSnippet(new vscode.SnippetString(completion), position);
            }
        });
    });
    // Command for code suggestions
    const suggestCodeDisposable = vscode.commands.registerCommand('extension.suggestCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor found.');
            return;
        }
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);
        const language = editor.document.languageId;
        if (!selectedText) {
            vscode.window.showInformationMessage('Please select some code to get suggestions.');
            return;
        }
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Getting code suggestions...",
            cancellable: false
        }, async (progress) => {
            const suggestion = await getCodeSuggestion(`Improve this ${language} code:\n\n${selectedText}`, language);
            if (suggestion) {
                // Show suggestion in a new document
                const doc = await vscode.workspace.openTextDocument({
                    content: suggestion,
                    language: language
                });
                await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
        });
    });
    // Command to configure API key
    const configureApiKeyDisposable = vscode.commands.registerCommand('extension.configureApiKey', async () => {
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your OpenAI API Key',
            password: true,
            placeHolder: 'sk-...'
        });
        if (apiKey) {
            const config = vscode.workspace.getConfiguration('misogiCopilot');
            await config.update('openaiApiKey', apiKey, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage('API key configured successfully!');
        }
    });
    // Hover provider for inline suggestions
    const hoverProvider = vscode.languages.registerHoverProvider('*', {
        async provideHover(document, position, token) {
            const config = vscode.workspace.getConfiguration('misogiCopilot');
            const enableHover = config.get('enableHover') || false;
            if (!enableHover) {
                return;
            }
            const range = document.getWordRangeAtPosition(position);
            if (!range) {
                return;
            }
            const word = document.getText(range);
            const line = document.lineAt(position.line).text;
            // Simple suggestion for function calls or variables
            if (word.length > 2) {
                return new vscode.Hover(`💡 Misogi Copilot: Use Ctrl+Space (Option+Space on Mac) for AI completion`);
            }
        }
    });
    // Register all disposables
    context.subscriptions.push(completeCodeDisposable, suggestCodeDisposable, configureApiKeyDisposable, hoverProvider);
}
function deactivate() {
    console.log('Misogi Copilot extension is now deactivated.');
}
//# sourceMappingURL=extension.js.map