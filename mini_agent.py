import os
import json
from groq import Groq

# 1. Initialize Client
# Best practice: use os.environ.get("GROQ_API_KEY") 
client = Groq(api_key="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")

# 2. Define your Python functions (Tools)
def list_files():
    """Returns a list of files in the current directory."""
    return {"files": os.listdir(".")}

def read_file(filename):
    """Reads the contents of a file."""
    try:
        with open(filename, 'r') as f:
            return {"content": f.read()}
    except Exception as e:
        return {"error": str(e)}
    
def write_to_file(filename, content):
    """Creates or overwrites a file with the provided content."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return {"status": "success", "message": f"File {filename} written successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 3. Define the "Tool Specs" (What the AI sees)
tools = [
    
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Get a list of all files in the user's current project directory.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the text inside a specific file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file to read."}
                },
                "required": ["filename"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "write_to_file",
        "description": "Create a new file or update an existing one with new code or text.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the file to create/edit."},
                "content": {"type": "string", "description": "The full text content to put in the file."}
            },
            "required": ["filename", "content"]
        }
    }
    }
]

# 4. The Agent Loop
messages = [{"role": "system", "content": "You are a helpful coding assistant. Use tools to see the user's files."}]

print("--- Mini-Claude (Groq Edition) ---")
while True:
    user_prompt = input("\nYou: ")
    if user_prompt.lower() in ['exit', 'quit']: break
    
    messages.append({"role": "user", "content": user_prompt})

    # First request: Ask the AI what to do
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # Check if the AI wants to use a tool
    if response_message.tool_calls:
        messages.append(response_message) # Add AI's request to history
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"  [System: AI is calling {function_name} with {args}]")
            
            # Execute the local Python function
            if function_name == "list_files":
                result = list_files()
            elif function_name == "read_file":
                result = read_file(args.get("filename"))
            elif function_name == "write_to_file":
                result = write_to_file(args.get("filename"), args.get("content"))
            
            # Send the result back to the AI
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)
            })
        
        # Second request: Get final answer after tool use
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        print(f"\nAI: {final_response.choices[0].message.content}")
        messages.append(final_response.choices[0].message)
    else:
        print(f"\nAI: {response_message.content}")
        messages.append(response_message)