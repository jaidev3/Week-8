import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import OpenAI from 'openai';

// Load environment variables from .env file
function loadEnvFile(workspaceRoot: string): { [key: string]: string } {
    const envPath = path.join(workspaceRoot, '.env');
    const env: { [key: string]: string } = {};
    
    try {
        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf8');
            const lines = envContent.split('\n');
            
            for (const line of lines) {
                const trimmedLine = line.trim();
                if (trimmedLine && !trimmedLine.startsWith('#')) {
                    const [key, ...valueParts] = trimmedLine.split('=');
                    if (key && valueParts.length > 0) {
                        const value = valueParts.join('=').replace(/^["']|["']$/g, ''); // Remove quotes
                        env[key.trim()] = value.trim();
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error reading .env file:', error);
    }
    
    return env;
}

export class OpenAIService {
    private openai: OpenAI | null = null;
    private config: vscode.WorkspaceConfiguration;
    private envVars: { [key: string]: string } = {};

    constructor() {
        this.config = vscode.workspace.getConfiguration('misogiCopilot');
        this.loadEnvironmentVariables();
        this.initializeOpenAI();
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('misogiCopilot')) {
                this.initializeOpenAI();
            }
        });

        // Watch for .env file changes
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            const envPath = path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, '.env');
            const envWatcher = fs.watchFile(envPath, { interval: 1000 }, () => {
                this.loadEnvironmentVariables();
                this.initializeOpenAI();
            });
        }
    }

    private loadEnvironmentVariables(): void {
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            this.envVars = loadEnvFile(workspaceRoot);
        }
    }

    private initializeOpenAI(): void {
        // Priority: 1. .env file, 2. VS Code settings, 3. environment variable
        let apiKey = this.envVars['OPENAI_API_KEY'] || 
                     this.config.get<string>('openaiApiKey') || 
                     process.env.OPENAI_API_KEY;

        if (apiKey && apiKey.trim() !== '') {
            this.openai = new OpenAI({
                apiKey: apiKey.trim()
            });
        } else {
            this.openai = null;
        }
    }

    public isConfigured(): boolean {
        return this.openai !== null;
    }

    public async getCodeCompletion(prompt: string, language: string, context?: string): Promise<string> {
        if (!this.openai) {
            throw new Error('OpenAI API key not configured. Please set your API key in settings.');
        }

        const model = this.config.get<string>('model', 'gpt-4.1-nano');
        const maxTokens = this.config.get<number>('maxTokens', 450);
        const temperature = this.config.get<number>('temperature', 0.2);

        const systemPrompt = `You are an expert ${language} programmer. Provide code completions that are:
1. Syntactically correct
2. Follow best practices
3. Are contextually appropriate
4. Include helpful comments when needed
5. Only return the code completion, no explanations

Current context: ${context || 'None'}`;

        try {
            const response = await this.openai.chat.completions.create({
                model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: `Complete this code:\n\n${prompt}` }
                ],
                max_tokens: maxTokens,
                temperature,
                stop: ['\n\n', '```']
            });

            return response.choices[0]?.message?.content?.trim() || '';
        } catch (error) {
            console.error('OpenAI API Error:', error);
            throw new Error(`Failed to get code completion: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    public async getCodeSuggestions(code: string, language: string): Promise<string> {
        if (!this.openai) {
            throw new Error('OpenAI API key not configured. Please set your API key in settings.');
        }

        const model = this.config.get<string>('model', 'gpt-4o-mini');
        const maxTokens = this.config.get<number>('maxTokens', 300);
        const temperature = this.config.get<number>('temperature', 0.7);

        const systemPrompt = `You are an expert ${language} code reviewer. Analyze the provided code and suggest improvements for:
1. Performance optimizations
2. Code readability
3. Best practices
4. Potential bugs
5. Security issues

Provide specific, actionable suggestions with brief explanations.`;

        try {
            const response = await this.openai.chat.completions.create({
                model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: `Review this ${language} code:\n\n${code}` }
                ],
                max_tokens: maxTokens,
                temperature
            });

            return response.choices[0]?.message?.content?.trim() || '';
        } catch (error) {
            console.error('OpenAI API Error:', error);
            throw new Error(`Failed to get code suggestions: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    public async getHoverHelp(code: string, language: string, symbol: string): Promise<string> {
        if (!this.openai) {
            return '';
        }

        const model = this.config.get<string>('model', 'gpt-3.5-turbo');
        
        const systemPrompt = `You are a helpful coding assistant. Provide brief, helpful information about the symbol "${symbol}" in the context of the provided ${language} code. Keep responses concise (1-2 sentences).`;

        try {
            const response = await this.openai.chat.completions.create({
                model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: `Explain "${symbol}" in this context:\n\n${code}` }
                ],
                max_tokens: 100,
                temperature: 0.3
            });

            return response.choices[0]?.message?.content?.trim() || '';
        } catch (error) {
            console.error('OpenAI API Error:', error);
            return '';
        }
    }
}