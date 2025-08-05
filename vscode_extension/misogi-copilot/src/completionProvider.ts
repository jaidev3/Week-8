import * as vscode from 'vscode';
import { OpenAIService } from './openaiService';

export class MisogiCompletionProvider implements vscode.InlineCompletionItemProvider {
    private openaiService: OpenAIService;
    private lastCompletionTime: number = 0;
    private debounceDelay: number = 500; // 500ms debounce

    constructor(openaiService: OpenAIService) {
        this.openaiService = openaiService;
    }

    async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | vscode.InlineCompletionList | null> {
        console.log('Misogi Copilot: Completion requested', { 
            line: position.line, 
            character: position.character,
            triggerKind: context.triggerKind,
            language: document.languageId
        });
        
        // Check if OpenAI is configured
        if (!this.openaiService.isConfigured()) {
            console.log('Misogi Copilot: OpenAI not configured');
            return null;
        }

        // Debounce to avoid too many API calls
        const now = Date.now();
        if (now - this.lastCompletionTime < this.debounceDelay) {
            console.log('Misogi Copilot: Request debounced');
            return null;
        }
        this.lastCompletionTime = now;

        // Get current line and context
        const currentLine = document.lineAt(position.line);
        const textBeforeCursor = currentLine.text.substring(0, position.character);
        
        // Don't provide completions for empty lines
        if (textBeforeCursor.trim() === '') {
            console.log('Misogi Copilot: Empty line, skipping completion');
            return null;
        }

        console.log('Misogi Copilot: Processing completion for:', textBeforeCursor);

        try {
            // Get surrounding context (5 lines before and after)
            const startLine = Math.max(0, position.line - 5);
            const endLine = Math.min(document.lineCount - 1, position.line + 5);
            const contextRange = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
            const context = document.getText(contextRange);

            // Get the language
            const language = document.languageId;

            // Create the prompt
            const prompt = textBeforeCursor;

            // Get completion from OpenAI
            console.log('Misogi Copilot: Requesting completion from OpenAI...');
            const completion = await this.openaiService.getCodeCompletion(prompt, language, context);
            console.log('Misogi Copilot: Received completion:', completion);

            if (completion && completion.trim() !== '') {
                const item = new vscode.InlineCompletionItem(
                    completion,
                    new vscode.Range(position, position)
                );
                
                console.log('Misogi Copilot: Returning completion item');
                return [item];
            }

            console.log('Misogi Copilot: No completion returned');
            return null;
        } catch (error) {
            console.error('Error in completion provider:', error);
            // Show error message only if it's an API key issue
            if (error instanceof Error && error.message.includes('API key')) {
                vscode.window.showErrorMessage(`Misogi Copilot: ${error.message}`);
            }
            return null;
        }
    }
}