import os

class ProjectStorage:
    def __init__(self):
        self.root_dir = self._find_project_root()
        self.config_dir = os.path.join(self.root_dir, ".claudemini")
        self.memory_file = os.path.join(self.root_dir, "CLAUDE.md")
        
        # Ensure the config directory exists for sessions and logs
        os.makedirs(self.config_dir, exist_ok=True)

    def _find_project_root(self):
        """Locates the root of the repo by looking for markers."""
        path = os.getcwd()
        while path != os.path.dirname(path):
            if any(os.path.exists(os.path.join(path, m)) for m in [".git", "pyproject.toml", "package.json"]):
                return path
            path = os.path.dirname(path)
        return os.getcwd()

    def get_project_rules(self):
        """Reads the CLAUDE.md file for the system prompt."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return f.read()
        return "Standard coding practices apply."

    def write_memory(self, content):
        """Allows the AI to update its own persistent rules."""
        with open(self.memory_file, "w") as f:
            f.write(content)