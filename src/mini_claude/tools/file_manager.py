import os

def generate_tree_summary(root_dir=".", max_depth=3):
    tree = []
    ignore_list = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'build', 'dist','.egg-info'}
    
    def walk(directory, prefix=""):
        # Stop if we go too deep (prevents 8 million chars!)
        depth = prefix.count("    ")
        if depth >= max_depth:
            return

        items = sorted(os.listdir(directory))
        # Filter items
        items = [i for i in items if i not in ignore_list and not i.startswith('.')]
        
        for i, item in enumerate(items):
            path = os.path.join(directory, item)
            is_last = (i == len(items) - 1)
            
            # Choose the "branch" character
            connector = "└── " if is_last else "├── "
            tree.append(f"{prefix}{connector}{item}")
            
            if os.path.isdir(path):
                # Recurse into the folder
                extension = "    " if is_last else "│   "
                walk(path, prefix + extension)

    tree.append(os.path.basename(os.path.abspath(root_dir)) + "/")
    walk(root_dir)
    return "\n".join(tree)

def get_repo_map(root_dir="."):
    repo_map = []
    # AGGRESSIVE IGNORE LIST
    ignore_list = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv', 
        'build', 'dist', 'AppData', 'Local', 'Roaming'
    }
    
    for root, dirs, files in os.walk(root_dir):
        # Stop deep-scanning ignored folders
        dirs[:] = [d for d in dirs if d not in ignore_list]
        
        for file in files:
            # Skip heavy binaries and hidden files
            if file.startswith('.') or file.endswith(('.exe', '.dll', '.zip', '.png', '.jpg')):
                continue
                
            rel_path = os.path.relpath(os.path.join(root, file), root_dir)
            repo_map.append(rel_path)
            
            # SAFETY VALVE: If the map gets too long, stop adding to it
            if len("\n".join(repo_map)) > 5000:
                repo_map.append("... [Map Truncated: Too many files] ...")
                break
        else: continue
        break
                
    return "\n".join(repo_map)

def read_file(path):
    """Simple tool to read file content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path, content):
    """Simple tool to create or overwrite a file."""
    try:
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def patch_file(filename, search_text, replace_text):
    """Replicates OpenCode's 'Edit' tool (Atomic changes)."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if search_text in content:
            new_content = content.replace(search_text, replace_text)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return "Patch applied successfully."
        return "Search text not found. Patch failed."
    except Exception as e:
        return f"Error patching file: {str(e)}"