import * as vscode from 'vscode';
import { OpenAIService } from './openaiService';

export class MisogiHoverProvider implements vscode.HoverProvider {
    private openaiService: OpenAIService;

    constructor(openaiService: OpenAIService) {
        this.openaiService = openaiService;
    }

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | null> {
        
        // Check if hover is enabled and OpenAI is configured
        const config = vscode.workspace.getConfiguration('misogiCopilot');
        const enableHover = config.get<boolean>('enableHover', false);
        
        if (!enableHover || !this.openaiService.isConfigured()) {
            return null;
        }

        // Get the word at the current position
        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return null;
        }

        const word = document.getText(wordRange);
        if (!word || word.trim() === '') {
            return null;
        }

        try {
            // Get surrounding context (10 lines before and after)
            const startLine = Math.max(0, position.line - 10);
            const endLine = Math.min(document.lineCount - 1, position.line + 10);
            const contextRange = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
            const context = document.getText(contextRange);

            // Get the language
            const language = document.languageId;

            // Get help from OpenAI
            const help = await this.openaiService.getHoverHelp(context, language, word);

            if (help && help.trim() !== '') {
                const markdown = new vscode.MarkdownString();
                markdown.appendMarkdown(`**Misogi Copilot AI Help**\n\n${help}`);
                markdown.supportHtml = true;
                
                return new vscode.Hover(markdown, wordRange);
            }

            return null;
        } catch (error) {
            console.error('Error in hover provider:', error);
            return null;
        }
    }
}