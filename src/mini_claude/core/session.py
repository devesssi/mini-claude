import os
import json

class SessionManager:
    def __init__(self, session_id="default"):
        self.storage_dir = ".claudemini/sessions"
        self.session_path = os.path.join(self.storage_dir, f"{session_id}.json")
        self.history = []
        os.makedirs(self.storage_dir, exist_ok=True)

    def add_message(self, role, content, tool_calls=None, tool_call_id=None, name=None):
        message = {"role": role, "content": content}
        if tool_calls: message["tool_calls"] = tool_calls
        if tool_call_id: message["tool_call_id"] = tool_call_id
        if name: message["name"] = name
        self.history.append(message)
        self.persist()

    def persist(self):
        """Save history to disk, handling non-dict objects if they exist."""
        serializable = []
        for m in self.history:
            # If it's a Groq/OpenAI object, convert to dict
            if hasattr(m, "model_dump"):
                serializable.append(m.model_dump())
            else:
                serializable.append(m)
        
        with open(self.session_path, "w") as f:
            json.dump(serializable, f, indent=2)

    def load(self):
        if os.path.exists(self.session_path):
            with open(self.session_path, "r") as f:
                self.history = json.load(f)
        return self.history