import * as vscode from 'vscode';
import { ChatSession, ChatMessage } from './agent/state';
import { v4 as uuidv4 } from 'uuid';

export class StateManager {
    private context: vscode.ExtensionContext;
    private readonly STORAGE_KEY = 'misogiCopilot.chatSessions';
    private readonly MAX_SESSIONS = 10;
    private readonly MAX_MESSAGES_PER_SESSION = 100;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    // Session Management
    public async createNewSession(): Promise<ChatSession> {
        const session: ChatSession = {
            id: uuidv4(),
            messages: [],
            createdAt: Date.now(),
            lastActivity: Date.now()
        };

        await this.saveSession(session);
        return session;
    }

    public async saveSession(session: ChatSession): Promise<void> {
        try {
            const sessions = await this.getAllSessions();
            const existingIndex = sessions.findIndex(s => s.id === session.id);

            if (existingIndex >= 0) {
                sessions[existingIndex] = session;
            } else {
                sessions.unshift(session);
            }

            // Limit number of sessions
            if (sessions.length > this.MAX_SESSIONS) {
                sessions.splice(this.MAX_SESSIONS);
            }

            // Limit messages per session
            sessions.forEach(s => {
                if (s.messages.length > this.MAX_MESSAGES_PER_SESSION) {
                    s.messages = s.messages.slice(-this.MAX_MESSAGES_PER_SESSION);
                }
            });

            await this.context.globalState.update(this.STORAGE_KEY, sessions);
        } catch (error) {
            console.error('Failed to save session:', error);
        }
    }

    public async getSession(sessionId: string): Promise<ChatSession | undefined> {
        try {
            const sessions = await this.getAllSessions();
            return sessions.find(s => s.id === sessionId);
        } catch (error) {
            console.error('Failed to get session:', error);
            return undefined;
        }
    }

    public async getAllSessions(): Promise<ChatSession[]> {
        try {
            const sessions = this.context.globalState.get<ChatSession[]>(this.STORAGE_KEY, []);
            // Sort by last activity (most recent first)
            return sessions.sort((a, b) => b.lastActivity - a.lastActivity);
        } catch (error) {
            console.error('Failed to get all sessions:', error);
            return [];
        }
    }

    public async deleteSession(sessionId: string): Promise<void> {
        try {
            const sessions = await this.getAllSessions();
            const filteredSessions = sessions.filter(s => s.id !== sessionId);
            await this.context.globalState.update(this.STORAGE_KEY, filteredSessions);
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    }

    public async clearAllSessions(): Promise<void> {
        try {
            await this.context.globalState.update(this.STORAGE_KEY, []);
        } catch (error) {
            console.error('Failed to clear all sessions:', error);
        }
    }

    // Message Management
    public async addMessageToSession(sessionId: string, message: ChatMessage): Promise<void> {
        try {
            const session = await this.getSession(sessionId);
            if (session) {
                session.messages.push(message);
                session.lastActivity = Date.now();
                await this.saveSession(session);
            }
        } catch (error) {
            console.error('Failed to add message to session:', error);
        }
    }

    public async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
        try {
            const session = await this.getSession(sessionId);
            return session?.messages || [];
        } catch (error) {
            console.error('Failed to get session messages:', error);
            return [];
        }
    }

    public async updateSessionActivity(sessionId: string): Promise<void> {
        try {
            const session = await this.getSession(sessionId);
            if (session) {
                session.lastActivity = Date.now();
                await this.saveSession(session);
            }
        } catch (error) {
            console.error('Failed to update session activity:', error);
        }
    }

    // Context Management
    public async saveUserPreferences(preferences: any): Promise<void> {
        try {
            await this.context.globalState.update('misogiCopilot.userPreferences', preferences);
        } catch (error) {
            console.error('Failed to save user preferences:', error);
        }
    }

    public async getUserPreferences(): Promise<any> {
        try {
            return this.context.globalState.get('misogiCopilot.userPreferences', {});
        } catch (error) {
            console.error('Failed to get user preferences:', error);
            return {};
        }
    }

    // Workspace Context
    public async saveWorkspaceContext(context: any): Promise<void> {
        try {
            const workspaceKey = this.getWorkspaceKey();
            await this.context.workspaceState.update(`misogiCopilot.context.${workspaceKey}`, context);
        } catch (error) {
            console.error('Failed to save workspace context:', error);
        }
    }

    public async getWorkspaceContext(): Promise<any> {
        try {
            const workspaceKey = this.getWorkspaceKey();
            return this.context.workspaceState.get(`misogiCopilot.context.${workspaceKey}`, {});
        } catch (error) {
            console.error('Failed to get workspace context:', error);
            return {};
        }
    }

    private getWorkspaceKey(): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            return workspaceFolder.name.replace(/[^a-zA-Z0-9]/g, '_');
        }
        return 'default';
    }

    // Analytics and Statistics
    public async getUsageStatistics(): Promise<any> {
        try {
            const sessions = await this.getAllSessions();
            const totalMessages = sessions.reduce((sum, session) => sum + session.messages.length, 0);
            const userMessages = sessions.reduce((sum, session) => 
                sum + session.messages.filter(msg => msg.role === 'user').length, 0);
            const assistantMessages = sessions.reduce((sum, session) => 
                sum + session.messages.filter(msg => msg.role === 'assistant').length, 0);

            return {
                totalSessions: sessions.length,
                totalMessages,
                userMessages,
                assistantMessages,
                averageMessagesPerSession: sessions.length > 0 ? totalMessages / sessions.length : 0,
                oldestSession: sessions.length > 0 ? Math.min(...sessions.map(s => s.createdAt)) : null,
                mostRecentActivity: sessions.length > 0 ? Math.max(...sessions.map(s => s.lastActivity)) : null
            };
        } catch (error) {
            console.error('Failed to get usage statistics:', error);
            return {
                totalSessions: 0,
                totalMessages: 0,
                userMessages: 0,
                assistantMessages: 0,
                averageMessagesPerSession: 0,
                oldestSession: null,
                mostRecentActivity: null
            };
        }
    }

    // Cleanup and Maintenance
    public async cleanupOldSessions(maxAge: number = 30 * 24 * 60 * 60 * 1000): Promise<void> {
        try {
            const sessions = await this.getAllSessions();
            const cutoffTime = Date.now() - maxAge;
            const activeSessions = sessions.filter(session => session.lastActivity > cutoffTime);
            
            if (activeSessions.length !== sessions.length) {
                await this.context.globalState.update(this.STORAGE_KEY, activeSessions);
                console.log(`Cleaned up ${sessions.length - activeSessions.length} old sessions`);
            }
        } catch (error) {
            console.error('Failed to cleanup old sessions:', error);
        }
    }

    public async exportSessions(): Promise<string> {
        try {
            const sessions = await this.getAllSessions();
            return JSON.stringify(sessions, null, 2);
        } catch (error) {
            console.error('Failed to export sessions:', error);
            return '[]';
        }
    }

    public async importSessions(data: string): Promise<boolean> {
        try {
            const sessions = JSON.parse(data) as ChatSession[];
            if (Array.isArray(sessions)) {
                await this.context.globalState.update(this.STORAGE_KEY, sessions);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to import sessions:', error);
            return false;
        }
    }
}