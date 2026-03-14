**Title:** Mini Claude - A Modular CLI Chatbot Inspired by OpenCode and Claude

**Introduction:**
Mini Claude is a Python-based modular CLI chatbot that draws inspiration from OpenCode and Claude. This repository provides a basic structure and tools to get started with building your own conversational interfaces. Mini Claude features a separate memory layer, allowing for more advanced conversation management and context understanding.

**Key Features:**
* Modular architecture for easy customization and extension
* Separate memory layer for advanced conversation management and context understanding
* CLI-based interface for user interaction
* Inspired by OpenCode and Claude, with a focus on simplicity and ease of use

**Getting Started:**
To set up the Mini Claude repository locally, follow these steps:
1. Clone the repository using `git clone https://github.com/your-username/mini-claude.git`
2. Install the required dependencies by running `pip install -r requirements.txt`
3. Navigate to the repository root directory and run `python mini_agent.py` to start the chatbot

**Directory Structure:**
The repository is organized into the following directories:
* `src/mini_claude/`: contains the core chatbot logic and modules
* `src/mini_claude/core/`: contains the engine and provider modules for the chatbot
* `src/mini_claude/tools/`: contains utility functions for file management and terminal interactions
* `src/mini_claude/memory/`: contains the memory layer implementation for conversation management and context understanding

**Configuration:**
To configure the chatbot, create a `.mini_claude_config.json` file in the repository root directory with the following format:
```json
{
    "memory": {
        "size": 100,
        "expiration": 3600
    },
    "cli": {
        "prompt": "mini-claude> ",
        "welcome_message": "Welcome to Mini Claude! Type 'help' for commands."
    }
}
```
Replace the values with your desired settings for the memory layer and CLI interface.

**Usage:**
To interact with the chatbot, simply run `python mini_agent.py` and follow the prompts. You can customize the chatbot's behavior by modifying the `src/mini_claude/core/engine.py` and `src/mini_claude/core/provider.py` files.

**Memory Layer:**
The memory layer is a key feature of Mini Claude, allowing for advanced conversation management and context understanding.

1. The Short-Term Memory (session.py)
This handles the immediate conversation history.

Persistence: Every message (User, Assistant, or Tool result) is saved to .opencode/sessions/latest.json the moment it happens.

Auto-Resumption: When the engine starts, it calls session.load(), allowing you to pick up exactly where you left off.

Context Cleaning: We implemented a "Strip" logic that removes extra SDK fields (like annotations) before saving, ensuring the Groq API doesn't reject the history later.

2. The Context Manager (compact_context)
This is the "Memory Optimization" logic located within the engine.

Sliding Window: It monitors the history length. Once it hits your max_history (15 turns), it triggers a compaction.

Summarization: It uses a smaller, faster model (Llama-3.1-8b) to turn the middle of the conversation into a single "Technical Status Report," saving thousands of tokens while keeping the "Goal" and "Recent Actions" intact.

3. The Long-Term Memory & Grounding (storage.py)
This is the "Project Knowledge" layer.

Root Detection: It identifies the project root so the AI knows its boundaries.

CLAUDE.md Integration: This acts as the "Permanent Memory." It’s where the AI reads its custom project instructions and coding standards every time you run a command.

Environment Mapping: It provides the "Repo Map" to the system prompt, so the AI always knows the current file structure without you having to explain it.

**Contributing:**
We welcome contributions to the Mini Claude repository! If you'd like to add a new feature or fix a bug, please submit a pull request with a clear description of your changes.

**License:**
Mini Claude is licensed under the MIT License. See `LICENSE` for details.
