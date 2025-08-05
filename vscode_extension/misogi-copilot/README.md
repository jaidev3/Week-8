# Misogi Copilot - VS Code AI Assistant Extension

An intelligent VS Code extension that mimics Cursor IDE's AI assistant functionality with agent orchestration and state management.

## Features

### Day 1 Implementation ✅

- **🤖 Chat Interface**: Clean webview panel with bi-directional communication
- **🔄 Agent Orchestration**: Simplified agent flow with Input → Processing → LLM → Response
- **💾 State Management**: Conversation history persistence using VS Code's state API
- **🔧 Context Awareness**: Automatic detection of active file, selected text, and workspace info
- **⚡ Real-time Communication**: WebView messaging for instant responses
- **🎨 VS Code Theme Integration**: UI that matches your VS Code theme

## Installation & Setup

### Prerequisites
- VS Code 1.77.0 or higher
- Node.js 16.x or higher
- OpenAI API key

### Development Setup

1. **Clone and Install Dependencies**
   ```bash
   cd vscode_extension/misogi-copilot
   npm install
   ```

2. **Configure API Key**
   - Copy `env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-openai-api-key-here
     ```

3. **Compile and Run**
   ```bash
   npm run compile
   ```
   - Press F5 in VS Code to launch Extension Development Host
   - Or use `Ctrl+Shift+P` → "Developer: Reload Window"

## Usage

### Commands

- **`Ctrl+Shift+C`** (Mac: `Cmd+Shift+C`) - Open Chat Panel
- **`Ctrl+Space`** (Mac: `Option+Space`) - Complete Code
- **`Ctrl+Shift+S`** (Mac: `Cmd+Shift+S`) - Suggest Code Improvements

### Chat Interface

1. **Open Chat Panel**: Use `Ctrl+Shift+C` or Command Palette → "Misogi Copilot: Open Chat Panel"
2. **Ask Questions**: Type your coding questions in the input field
3. **Context Awareness**: The AI automatically sees your active file and selected text
4. **Clear History**: Click the 🗑️ button to start a new conversation

### Configuration

Access settings via `File > Preferences > Settings` → search "Misogi Copilot":

- **API Key**: Your OpenAI API key
- **Model**: Choose between GPT-3.5-turbo, GPT-4, or GPT-4-turbo
- **Max Tokens**: Control response length (50-1000)
- **Temperature**: Creativity level (0-2)
- **Enable Hover**: Show AI hints on hover

## Architecture

### Core Components

```
src/
├── agent/
│   ├── chatAgent.ts      # AI agent with simplified flow
│   └── state.ts          # State interfaces and types
├── chatPanel.ts          # WebView panel provider
├── stateManager.ts       # Conversation persistence
├── extension.ts          # Main extension entry point
├── openaiService.ts      # OpenAI API integration
├── completionProvider.ts # Inline completions
├── hoverProvider.ts      # Hover hints
└── commands.ts           # Extension commands

media/
├── chat.css             # Chat UI styles
└── chat.js              # Chat UI JavaScript
```

### Agent Flow

1. **Input Processing**: Capture user message and context
2. **Context Enrichment**: Add VS Code workspace information
3. **LLM Processing**: Send to OpenAI with system prompt
4. **Response Formatting**: Return structured response
5. **State Persistence**: Save conversation history

### State Management

- **Session Storage**: Conversations persist across VS Code restarts
- **Context Tracking**: Active file, selected text, language detection
- **History Limits**: Max 10 sessions, 100 messages per session
- **Automatic Cleanup**: Old sessions cleaned up after 30 days

## Example Interactions

### Code Review
```
User: "Review this function for performance issues"
[Selected code is automatically included]

AI: "I can see you've selected a function that processes an array. Here are some performance optimizations:
1. Use Array.forEach() instead of for loops for better readability
2. Consider using Set for faster lookups if you're checking membership
3. The nested loop has O(n²) complexity - consider using a Map for O(n) solution"
```

### Code Completion
```
User: "Complete this React component"
[Current file context is included]

AI: "Based on your component structure, here's the completion:
- Add proper TypeScript interfaces for props
- Implement error boundaries
- Add loading states for better UX"
```

### Debugging Help
```
User: "Why is this API call failing?"
[Error context and code automatically included]

AI: "Looking at your API call, I can see a few potential issues:
1. Missing error handling for network failures
2. Incorrect Content-Type header
3. The endpoint URL seems to have a typo in the path"
```

## Troubleshooting

### Common Issues

**Extension not activating:**
- Check VS Code version (requires 1.77.0+)
- Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

**API Key not working:**
- Verify key in settings or `.env` file
- Check OpenAI account has sufficient credits
- Ensure key has correct permissions

**Chat panel not opening:**
- Try command palette: "Misogi Copilot: Open Chat Panel"
- Check Developer Console for errors: `Help > Toggle Developer Tools`

**Compilation errors:**
```bash
npm run compile
# Check for TypeScript errors
```

## Development

### Building from Source

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run tests
npm test

# Package extension
vsce package
```

### Future Enhancements (Roadmap)

- **🔄 Full LangGraph Integration**: Complete agent orchestration with complex workflows
- **📁 File System Operations**: Create, edit, and manage files through chat
- **🔍 Code Search**: Semantic search across workspace
- **🧪 Test Generation**: Automatic test case creation
- **📊 Code Analytics**: Complexity analysis and metrics
- **🎯 Custom Agents**: Specialized agents for different programming languages
- **🔗 Git Integration**: Commit message generation, PR reviews
- **📝 Documentation**: Auto-generate documentation from code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with VS Code Extension API
- Powered by OpenAI GPT models
- Inspired by Cursor IDE's AI assistant functionality

---

**Made with ❤️ for developers who want AI-powered coding assistance in VS Code**