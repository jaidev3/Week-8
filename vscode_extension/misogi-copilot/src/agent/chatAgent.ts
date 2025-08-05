import { ConversationState, ChatMessage } from "./state";
import * as vscode from 'vscode';
import { v4 as uuidv4 } from 'uuid';
import OpenAI from 'openai';

export class ChatAgent {
    private openai: OpenAI;
    private model: string;

    constructor(apiKey: string, model: string = "gpt-4o-mini") {
        this.openai = new OpenAI({
            apiKey: apiKey,
        });
        this.model = model;
    }

    // Simplified agent flow without LangGraph for now
    private async processInput(input: string, context?: any): Promise<ConversationState> {
        const sessionId = uuidv4();
        
        try {
            // Step 1: Input processing
            const state: ConversationState = {
                messages: [],
                currentInput: input,
                context: context || {},
                isTyping: true,
                sessionId,
            };

            // Step 2: Context enrichment
            const enrichedContext = await this.enrichContext(state.context);
            
            // Step 3: Create messages and get LLM response
            const systemPrompt = this.createSystemPrompt(enrichedContext);
            
            const response = await this.openai.chat.completions.create({
                model: this.model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: input }
                ],
                temperature: 0.7,
                max_tokens: 1000,
            });
            
            const aiResponse = response.choices[0]?.message?.content || 'Sorry, I could not generate a response.';
            
            // Step 4: Return final state
            return {
                messages: [], // We'll handle message storage differently
                currentInput: input,
                context: enrichedContext,
                isTyping: false,
                sessionId,
                aiResponse, // Add the AI response to the state
            } as ConversationState & { aiResponse: string };
            
        } catch (error) {
            return {
                messages: [],
                currentInput: input,
                context: context || {},
                isTyping: false,
                error: `Agent error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                sessionId,
            };
        }
    }

    private async enrichContext(context: any): Promise<any> {
        // Get current VS Code context
        const activeEditor = vscode.window.activeTextEditor;
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        
        return {
            ...context,
            activeFile: activeEditor?.document.fileName,
            selectedText: activeEditor?.document.getText(activeEditor.selection),
            language: activeEditor?.document.languageId,
            workspaceInfo: workspaceFolder?.name,
        };
    }

    private createSystemPrompt(context: any): string {
        const basePrompt = `You are Misogi Copilot, an intelligent coding assistant for VS Code. You help developers with:
- Code completion and suggestions
- Code review and optimization
- Debugging assistance
- Explaining code concepts
- Best practices and patterns

You provide concise, helpful responses focused on the user's coding needs.`;

        let contextPrompt = "";
        
        if (context.activeFile) {
            contextPrompt += `\nCurrent file: ${context.activeFile}`;
        }
        
        if (context.language) {
            contextPrompt += `\nLanguage: ${context.language}`;
        }
        
        if (context.selectedText) {
            contextPrompt += `\nSelected code:\n\`\`\`${context.language || ''}\n${context.selectedText}\n\`\`\``;
        }
        
        if (context.workspaceInfo) {
            contextPrompt += `\nWorkspace: ${context.workspaceInfo}`;
        }

        return basePrompt + contextPrompt;
    }

    public async processMessage(input: string, context?: any): Promise<ConversationState> {
        return this.processInput(input, context);
    }

    public async streamMessage(input: string, context?: any, onUpdate?: (state: ConversationState) => void): Promise<ConversationState> {
        // For now, simulate streaming by calling onUpdate with typing state
        if (onUpdate) {
            onUpdate({
                messages: [],
                currentInput: input,
                context: context || {},
                isTyping: true,
                sessionId: uuidv4(),
            });
        }
        
        // Process the message
        const result = await this.processInput(input, context);
        
        // Call onUpdate with final result
        if (onUpdate) {
            onUpdate(result);
        }
        
        return result;
    }
}