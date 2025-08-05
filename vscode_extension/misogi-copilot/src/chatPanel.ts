import * as vscode from 'vscode';
import { ChatAgent } from './agent/chatAgent';
import { ChatMessage, ChatSession } from './agent/state';
import { StateManager } from './stateManager';
import { v4 as uuidv4 } from 'uuid';

export class ChatPanelProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'misogiCopilot.chatView';
    private _view?: vscode.WebviewView;
    private chatAgent?: ChatAgent;
    private currentSession!: ChatSession;
    private readonly _extensionUri: vscode.Uri;
    private stateManager: StateManager;

    constructor(private readonly extensionUri: vscode.Uri, private readonly context: vscode.ExtensionContext) {
        this._extensionUri = extensionUri;
        this.stateManager = new StateManager(context);
        this.initializeSession();
    }

    private async initializeSession() {
        try {
            this.currentSession = await this.stateManager.createNewSession();
        } catch (error) {
            console.error('Failed to initialize session:', error);
            this.currentSession = this.createNewSession();
        }
    }

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

        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.type) {
                    case 'sendMessage':
                        this.handleUserMessage(message.text);
                        break;
                    case 'clearHistory':
                        this.clearChatHistory();
                        break;
                    case 'ready':
                        this.initializeChatAgent();
                        break;
                }
            },
            undefined,
            []
        );
    }

    private async initializeChatAgent() {
        const config = vscode.workspace.getConfiguration('misogiCopilot');
        const apiKey = config.get<string>('openaiApiKey');
        
        if (!apiKey) {
            this.sendMessageToWebview({
                type: 'error',
                message: 'OpenAI API key not configured. Please configure your API key first.'
            });
            return;
        }

        try {
            this.chatAgent = new ChatAgent(apiKey);
            this.sendMessageToWebview({
                type: 'ready',
                message: 'Chat agent initialized successfully!'
            });
        } catch (error) {
            this.sendMessageToWebview({
                type: 'error',
                message: `Failed to initialize chat agent: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        }
    }

    private async handleUserMessage(text: string) {
        if (!this.chatAgent) {
            this.sendMessageToWebview({
                type: 'error',
                message: 'Chat agent not initialized. Please check your API key configuration.'
            });
            return;
        }

        // Add user message to session
        const userMessage: ChatMessage = {
            id: uuidv4(),
            role: 'user',
            content: text,
            timestamp: Date.now(),
            context: this.getCurrentContext()
        };

        this.currentSession.messages.push(userMessage);
        this.currentSession.lastActivity = Date.now();
        
        // Persist to state manager
        await this.stateManager.addMessageToSession(this.currentSession.id, userMessage);

        // Send user message to webview
        this.sendMessageToWebview({
            type: 'userMessage',
            message: userMessage
        });

        // Show typing indicator
        this.sendMessageToWebview({
            type: 'typing',
            isTyping: true
        });

        try {
            // Process message through LangGraph agent
            await this.chatAgent.streamMessage(
                text,
                this.getCurrentContext(),
                (state) => {
                    // Handle streaming updates
                    if (state.isTyping) {
                        this.sendMessageToWebview({
                            type: 'typing',
                            isTyping: true
                        });
                    }
                }
            );

            // Get the final response
            const result = await this.chatAgent.processMessage(text, this.getCurrentContext());
            
            if (result.error) {
                this.sendMessageToWebview({
                    type: 'error',
                    message: result.error
                });
                return;
            }

            // Extract AI response from the result
            if (result.aiResponse) {
                const assistantMessage: ChatMessage = {
                    id: uuidv4(),
                    role: 'assistant',
                    content: result.aiResponse,
                    timestamp: Date.now()
                };

                this.currentSession.messages.push(assistantMessage);
                this.currentSession.lastActivity = Date.now();
                
                // Persist to state manager
                await this.stateManager.addMessageToSession(this.currentSession.id, assistantMessage);

                this.sendMessageToWebview({
                    type: 'assistantMessage',
                    message: assistantMessage
                });
            }

        } catch (error) {
            this.sendMessageToWebview({
                type: 'error',
                message: `Error processing message: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        } finally {
            // Hide typing indicator
            this.sendMessageToWebview({
                type: 'typing',
                isTyping: false
            });
        }
    }

    private getCurrentContext() {
        const activeEditor = vscode.window.activeTextEditor;
        return {
            file: activeEditor?.document.fileName,
            selection: activeEditor?.document.getText(activeEditor.selection),
            language: activeEditor?.document.languageId,
        };
    }

    private createNewSession(): ChatSession {
        return {
            id: uuidv4(),
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now()
        };
    }

    private async clearChatHistory() {
        try {
            this.currentSession = await this.stateManager.createNewSession();
        } catch (error) {
            console.error('Failed to create new session:', error);
            this.currentSession = this.createNewSession();
        }
        
        this.sendMessageToWebview({
            type: 'clearHistory'
        });
    }

    private sendMessageToWebview(message: any) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }

    private getHtmlForWebview(webview: vscode.Webview): string {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.css'));

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Misogi Copilot Chat</title>
    <link href="${styleUri}" rel="stylesheet">
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h3>🤖 Misogi Copilot</h3>
            <button id="clearBtn" class="clear-btn" title="Clear chat history">🗑️</button>
        </div>
        
        <div id="chatMessages" class="chat-messages">
            <div class="welcome-message">
                <div class="message assistant">
                    <div class="message-content">
                        <p>👋 Hello! I'm Misogi Copilot, your AI coding assistant.</p>
                        <p>I can help you with:</p>
                        <ul>
                            <li>Code completion and suggestions</li>
                            <li>Code review and optimization</li>
                            <li>Debugging assistance</li>
                            <li>Explaining code concepts</li>
                        </ul>
                        <p>How can I assist you today?</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="typingIndicator" class="typing-indicator" style="display: none;">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="typing-text">Misogi is thinking...</span>
        </div>
        
        <div class="chat-input-container">
            <div class="input-wrapper">
                <textarea 
                    id="chatInput" 
                    placeholder="Ask me anything about your code..." 
                    rows="1"
                    maxlength="2000"
                ></textarea>
                <button id="sendBtn" class="send-btn" title="Send message">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                    </svg>
                </button>
            </div>
            <div class="input-info">
                <span id="charCount">0/2000</span>
                <span class="keyboard-hint">Press Ctrl+Enter to send</span>
            </div>
        </div>
    </div>
    
    <script src="${scriptUri}"></script>
</body>
</html>`;
    }
}

export class ChatPanel {
    public static currentPanel: ChatPanel | undefined;
    public static readonly viewType = 'misogiCopilot.chat';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ChatPanel.viewType,
            'Misogi Copilot Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.onDidChangeViewState(
            e => {
                if (this._panel.visible) {
                    this._update();
                }
            },
            null,
            this._disposables
        );
    }

    public dispose() {
        ChatPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.css'));

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Misogi Copilot Chat</title>
    <link href="${styleUri}" rel="stylesheet">
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h3>🤖 Misogi Copilot</h3>
            <button id="clearBtn" class="clear-btn" title="Clear chat history">🗑️</button>
        </div>
        
        <div id="chatMessages" class="chat-messages">
            <div class="welcome-message">
                <div class="message assistant">
                    <div class="message-content">
                        <p>👋 Hello! I'm Misogi Copilot, your AI coding assistant.</p>
                        <p>I can help you with:</p>
                        <ul>
                            <li>Code completion and suggestions</li>
                            <li>Code review and optimization</li>
                            <li>Debugging assistance</li>
                            <li>Explaining code concepts</li>
                        </ul>
                        <p>How can I assist you today?</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="typingIndicator" class="typing-indicator" style="display: none;">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="typing-text">Misogi is thinking...</span>
        </div>
        
        <div class="chat-input-container">
            <div class="input-wrapper">
                <textarea 
                    id="chatInput" 
                    placeholder="Ask me anything about your code..." 
                    rows="1"
                    maxlength="2000"
                ></textarea>
                <button id="sendBtn" class="send-btn" title="Send message">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                    </svg>
                </button>
            </div>
            <div class="input-info">
                <span id="charCount">0/2000</span>
                <span class="keyboard-hint">Press Ctrl+Enter to send</span>
            </div>
        </div>
    </div>
    
    <script src="${scriptUri}"></script>
</body>
</html>`;
    }
}