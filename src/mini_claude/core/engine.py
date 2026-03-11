import os
import json
import subprocess
from groq import Groq
from ..tools.file_manager import generate_tree_summary, read_file, write_file, patch_file
from ..tools.terminal import run_command
from .session import SessionManager
from .storage import ProjectStorage

class OpenCodeEngine:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.session = SessionManager(session_id="latest")
        self.session.load()
        self.storage = ProjectStorage()
        self.mode = "PLAN"  
        self.model = "llama-3.3-70b-versatile"
        self.max_history = 15 

    def get_system_prompt(self):
        # Using the storage layer to get grounded project info
        rules = self.storage.get_project_rules()
        repo_map = generate_tree_summary() # or self.storage.get_repo_map()
        current_dir = os.getcwd()

        return f"""
# ROLE
You are an expert Senior AI Software Engineer. You are currently in **{self.mode}** mode.

# ENVIRONMENT
- **Root Directory**: {self.storage.root_dir}
- **Current Working Directory**: {current_dir}
- **Mode**: {self.mode} (Strict adherence required)

# REPO STRUCTURE
{repo_map}

# PROJECT RULES & CONTEXT
{rules if rules else "No specific rules provided. Follow standard clean code principles."}

# OPERATIONAL PROTOCOLS
1. **PLAN MODE**:
   - Focus on discovery, architecture, and step-by-step planning.
   - Use `read_file` to understand context.
   - Propose changes clearly but **NEVER** use `write_file`, `patch_file`, or `run_command`.
2. **BUILD MODE**:
   - Technical implementation.
   - You MUST run tests or verify code using `run_command` after writing files.
   - If a command fails, analyze the error and fix it immediately.

# TOOL USAGE GUIDELINES
- **read_file**: Read full content to ensure context.
- **patch_file**: Preferred for small changes to large files to save tokens.
- **write_file**: Use for creating new files or total rewrites.
- **run_command**: Use for `ls`, `grep`, `pytest`, `npm test`, or executing scripts.

# OUTPUT STYLE
- Be concise and technical.
- When in BUILD mode, explain what you are doing before calling the tool.
- If you reach a dead end, acknowledge it and suggest a new PLAN.
"""

    def get_tool_specs(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read content from a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create or overwrite a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    def compact_context(self):
        if len(self.session.history) <= self.max_history:
            return

        print("\n🧠 [Memory] Compacting context...")
        head = self.session.history[:1]
        body = self.session.history[1:-4]
        tail = self.session.history[-4:]

        body_str = ""
        for m in body:
            if isinstance(m, dict):
                body_str += f"{m.get('role')}: {m.get('content')}\n"
            else:
                body_str += f"assistant: {m.content}\n"

        try:
            summary_res = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Summarize this conversation briefly: {body_str}"}]
            )
            # FIX: Indexing the choice here to stop the list error
            summary_text = summary_res.choices.message.content
            self.session.history = head + [{"role": "system", "content": f"SUMMARY: {summary_text}"}] + tail
            self.session.persist()
        except Exception as e:
            print(f"Compaction failed: {e}")
            self.session.history = head + tail

    def chat(self, user_input):
        self.compact_context()
        self.session.history.append({"role": "user", "content": user_input})
        
        max_turns = 5
        turn = 0
        
        last_response = None
        
        while turn < max_turns:
            turn += 1
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.get_system_prompt()}] + self.session.history,
                tools=self.get_tool_specs(),
                tool_choice="auto"
            )
            
            # FIX: Indexing the choice here
            last_response = response.choices[0]
            response_message = last_response.message
            
            clean_message = {
                "role": response_message.role,
                "content": response_message.content or ""
            }
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                clean_message["tool_calls"] = response_message.tool_calls
            
            self.session.history.append(response_message)
            self.session.persist()

            if not response_message.tool_calls:
                return response_message.content

            for tool_call in response_message.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = ""

                if fn_name == "read_file":
                    result = read_file(args.get("path"))
                elif fn_name == "write_file":
                    if self.mode == "BUILD":
                        confirm = input(f"   Write {args.get('path')}? (y/n): ")
                        result = write_file(args.get("path"), args.get("content")) if confirm.lower() == 'y' else "Denied."
                    else:
                        result = "Error: Use BUILD mode."
                elif fn_name == "run_command":
                    if self.mode == "BUILD":
                        cmd = args.get("command")
                        confirm = input(f"   Run [{cmd}]? (y/n): ")
                        result = json.dumps(run_command(cmd)) if confirm.lower() == 'y' else "Denied."
                    else:
                        result = "Error: Use BUILD mode."

                self.session.history.append({
                    "role": "tool", 
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result)
                })
                self.session.persist()
                # print(last_response) # Removed or keep as per your original preference

        return response_message.content