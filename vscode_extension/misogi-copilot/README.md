# Misogi Copilot - AI Coding Assistant for VS Code

A powerful AI-powered coding assistant extension for Visual Studio Code that leverages OpenAI's GPT models to provide intelligent code completions, suggestions, and help.

## Features

### 🚀 Inline Code Completions
- **Smart Completions**: Get AI-powered code completions as you type
- **Context-Aware**: Uses surrounding code context for better suggestions
- **Multi-Language Support**: Works with all programming languages supported by VS Code

### 💡 Code Suggestions & Reviews
- **Code Analysis**: Get intelligent suggestions for code improvements
- **Best Practices**: Receive recommendations following coding best practices
- **Performance Tips**: Get suggestions for performance optimizations
- **Security Insights**: Identify potential security issues

### 🔍 AI-Powered Hover Help
- **Smart Tooltips**: Get AI explanations when hovering over code symbols
- **Contextual Help**: Understand functions, variables, and code patterns
- **Learning Assistant**: Perfect for learning new languages or frameworks

### ⚙️ Configurable Settings
- **Multiple Models**: Choose from GPT-3.5-turbo, GPT-4, or GPT-4-turbo
- **Adjustable Parameters**: Customize temperature, max tokens, and more
- **Toggle Features**: Enable/disable specific features as needed

## Installation

1. Install the extension from the VS Code Marketplace
2. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
3. Configure your API key using the command palette

## Setup

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Copy the API key (starts with `sk-`)

### 2. Configure the Extension

#### Option A: Using .env File (Recommended)
1. Open VS Code Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run command: `Misogi Copilot: Configure API Key`
3. Choose "Create .env file (Recommended)"
4. Enter your OpenAI API key
5. The extension will create a `.env` file in your workspace root

**Manual Setup:**
1. Create a `.env` file in your project root
2. Add your API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
3. The extension will automatically detect and use it

#### Option B: Using VS Code Settings
1. Open VS Code Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run command: `Misogi Copilot: Configure API Key`
3. Choose "Use VS Code Settings"
4. Enter your OpenAI API key
5. The key will be stored in VS Code's global settings

### 3. Security Note
- The `.env` file is automatically added to `.gitignore` to prevent accidental commits
- Never commit your API key to version control
- The `.env` method is recommended as it keeps secrets local to your project

## Usage

### Inline Code Completions
- Simply start typing code
- Completions will appear automatically
- Press `Tab` to accept suggestions
- Use `Option+Space` (Mac) or `Ctrl+Space` (Windows/Linux) to manually trigger completions

### Code Suggestions
1. Select the code you want to analyze
2. Use `Cmd+Shift+S` (Mac) or `Ctrl+Shift+S` (Windows/Linux)
3. Or run: `Misogi Copilot: Suggest Code Improvements`
4. View suggestions in a new document

### Hover Help
1. Enable in settings: `misogiCopilot.enableHover`
2. Hover over any code symbol
3. Get AI-powered explanations and help

## Commands

| Command | Description | Shortcut |
|---------|-------------|----------|
| `Misogi Copilot: Complete Code` | Get AI code completion | `Option+Space` (Mac), `Ctrl+Space` (Win/Linux) |
| `Misogi Copilot: Suggest Code Improvements` | Analyze selected code | `Cmd+Shift+S` (Mac), `Ctrl+Shift+S` (Win/Linux) |
| `Misogi Copilot: Configure API Key` | Set up OpenAI API key | - |

## Configuration

Access settings via `File > Preferences > Settings` and search for "Misogi Copilot":

| Setting | Description | Default |
|---------|-------------|---------|
| `misogiCopilot.openaiApiKey` | Your OpenAI API key | "" |
| `misogiCopilot.model` | OpenAI model to use | "gpt-3.5-turbo" |
| `misogiCopilot.maxTokens` | Maximum tokens for completions | 150 |
| `misogiCopilot.temperature` | AI creativity level (0-2) | 0.7 |
| `misogiCopilot.enableHover` | Enable hover help | false |

### Available Models
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-4` - More capable, higher quality
- `gpt-4-turbo-preview` - Latest GPT-4 with improved performance

## Status Bar

The extension shows its status in the VS Code status bar:
- 🤖 **Misogi Copilot ✓** - Ready and configured
- 🤖 **Misogi Copilot ⚠** - API key required (click to configure)

## Privacy & Security

- Your code is sent to OpenAI's API for processing
- API calls are made directly from your machine to OpenAI
- No code is stored or logged by this extension
- Your API key is stored securely in VS Code settings

## Troubleshooting

### Common Issues

**"OpenAI API key not configured"**
- Run `Misogi Copilot: Configure API Key` command
- Ensure your API key starts with `sk-`
- Check that you have sufficient OpenAI credits
- If using .env file, make sure it's in your workspace root
- Verify the .env file contains: `OPENAI_API_KEY=sk-your-key`

**"Failed to get code completion"**
- Check your internet connection
- Verify your OpenAI API key is valid
- Ensure you have sufficient API credits
- Try reducing `maxTokens` in settings

**Completions not appearing**
- Make sure you're typing in a supported file type
- Check that the extension is active (status bar shows ✓)
- Try manually triggering with the keyboard shortcut

### Performance Tips
- Use `gpt-3.5-turbo` for faster responses
- Reduce `maxTokens` for quicker completions
- Disable `enableHover` if you experience lag

## Requirements

- VS Code 1.77.0 or higher
- OpenAI API key with sufficient credits
- Internet connection

## Contributing

Found a bug or have a feature request? Please open an issue on our GitHub repository.

## License

This extension is provided as-is. Please review OpenAI's usage policies when using their API.

---

**Enjoy coding with AI assistance! 🚀**
