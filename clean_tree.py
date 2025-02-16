import os

EXCLUDE_DIRS = {"__pycache__", "bin", "etc", "lib", "share", ".git", ".venv", "env", "venv"}
EXCLUDE_FILES = {".DS_Store", "pyvenv.cfg"}
MAX_DEPTH = 3  # Adjust depth level as needed

def generate_tree(root_dir, indent="", level=0):
    """ Recursively prints the directory tree up to MAX_DEPTH levels """
    if level > MAX_DEPTH:
        return

    try:
        items = sorted(os.listdir(root_dir))
    except PermissionError:
        return

    items = [item for item in items if item not in EXCLUDE_DIRS and item not in EXCLUDE_FILES]

    for index, item in enumerate(items):
        path = os.path.join(root_dir, item)
        is_last = index == len(items) - 1
        prefix = "└── " if is_last else "├── "
        print(indent + prefix + item)

        if os.path.isdir(path):
            new_indent = indent + ("    " if is_last else "│   ")
            generate_tree(path, new_indent, level + 1)

if __name__ == "__main__":
    project_root = "."  # Change this if running from a different directory
    print("transcription_project/")
    generate_tree(project_root)
