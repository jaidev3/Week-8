export interface ConversationState {
    messages: any[]; // Simplified for now
    currentInput: string;
    context: {
        activeFile?: string;
        selectedText?: string;
        language?: string;
        workspaceInfo?: string;
    };
    isTyping: boolean;
    error?: string;
    sessionId: string;
    aiResponse?: string; // Add AI response field
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    context?: {
        file?: string;
        selection?: string;
        language?: string;
    };
}

export interface ChatSession {
    id: string;
    messages: ChatMessage[];
    createdAt: number;
    lastActivity: number;
}