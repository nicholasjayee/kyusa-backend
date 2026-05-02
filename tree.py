import pathlib

def draw_tree(path, prefix="", ignore_list=None):
    """
    Recursively generates a tree structure while skipping specified files/folders.
    """
    if ignore_list is None:
        ignore_list = []

    # Filter out any items found in the ignore_list
    paths = [
        p for p in path.iterdir() 
        if p.name not in ignore_list
    ]
    
    # Sort: Directories first, then files, both alphabetically
    paths.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    
    for i, p in enumerate(paths):
        is_last = (i == len(paths) - 1)
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{p.name}")
        
        if p.is_dir():
            extension = "    " if is_last else "│   "
            draw_tree(p, prefix + extension, ignore_list)

if __name__ == "__main__":
    # Get current script directory
    current_dir = pathlib.Path(__file__).parent.resolve()

    # Define your skip list here
    # Works for both folder names and file names
    to_skip = [
        ".git", 
        "__pycache__", 
        ".venv", 
        "node_modules", 
        ".DS_Store",
        "venv",
        "env",
        "build",
        "dist",
        "logs",
        "tmp",
        "output",
        "data",
        "results",
        ".gemini",
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".mypy_cache",
        ".plans"
    ]
    
    print(f"Project Root: {current_dir.name}/")
    draw_tree(current_dir, ignore_list=to_skip)