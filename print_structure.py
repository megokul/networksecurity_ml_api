import os


def print_directory_tree(start_path: str, indent: str = "", exclude_dirs=None) -> None:
    """
    Recursively prints the directory structure starting from `start_path`,
    excluding directories listed in `exclude_dirs`.

    Args:
        start_path (str): The root folder path to start from.
        indent (str): Used for indentation in recursive calls.
        exclude_dirs (set): Directory names to ignore.
    """
    if exclude_dirs is None:
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.github', '.git'}

    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        return  # Skip directories/files we can't access

    for item in items:
        item_path = os.path.join(start_path, item)

        if os.path.isdir(item_path):
            if item in exclude_dirs:
                continue
            print(f"{indent}📁 {item}/")
            print_directory_tree(item_path, indent + "    ", exclude_dirs)
        else:
            print(f"{indent}📄 {item}")


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"\n📦 Project Structure of: {ROOT_DIR}\n")
    print_directory_tree(ROOT_DIR)
