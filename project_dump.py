import os

EXCLUDE_DIRS = {'.venv', 'venv', '__pycache__', '.github', '.git', '.idea', '.vscode', 'build', 'dist', '.mypy_cache'}
OUTPUT_FILE = "project_code_dump.txt"
INCLUDE_YAML_FILES = {'config.yaml', 'params.yaml', 'schema.yaml'}


def is_valid_directory(dirname):
    return not any(part in EXCLUDE_DIRS for part in dirname.split(os.sep))


def print_directory_tree(start_path: str, indent: str = "", exclude_dirs=None, out_lines=None) -> list:
    """
    Recursively builds the directory structure starting from `start_path`.
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS
    if out_lines is None:
        out_lines = []

    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        return

    for item in items:
        item_path = os.path.join(start_path, item)
        if os.path.isdir(item_path):
            if item in exclude_dirs:
                continue
            out_lines.append(f"{indent}📁 {item}/")
            print_directory_tree(item_path, indent + "    ", exclude_dirs, out_lines)
        else:
            out_lines.append(f"{indent}📄 {item}")

    return out_lines


def list_target_files(root_dir):
    py_files = []
    yaml_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if is_valid_directory(os.path.join(dirpath, d))]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_dir)

            if filename.endswith('.py'):
                py_files.append((rel_path, full_path))
            elif filename in INCLUDE_YAML_FILES:
                yaml_files.append((rel_path, full_path))

    return sorted(py_files), sorted(yaml_files)


def dump_project_code_to_file(root_dir='.'):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_file:
        out_file.write(f"\n📦 Project Structure of: {os.path.abspath(root_dir)}\n\n")

        # Directory structure
        tree_lines = print_directory_tree(root_dir, out_lines=[])
        out_file.write("\n".join(tree_lines))
        out_file.write("\n\n--- PYTHON CODE DUMP ---\n\n")

        # File lists
        py_files, yaml_files = list_target_files(root_dir)

        # Dump .py files
        for rel_path, full_path in py_files:
            out_file.write(f"\n{'=' * 80}\n")
            out_file.write(f"# FILE: {rel_path}\n")
            out_file.write(f"{'=' * 80}\n\n")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    out_file.write(code.strip() + "\n")
            except Exception as e:
                out_file.write(f"Error reading {rel_path}: {e}\n")

        # Dump YAML files
        out_file.write("\n\n--- YAML CONFIG FILES DUMP ---\n\n")
        for rel_path, full_path in yaml_files:
            out_file.write(f"\n{'=' * 80}\n")
            out_file.write(f"# YAML FILE: {rel_path}\n")
            out_file.write(f"{'=' * 80}\n\n")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    out_file.write(content.strip() + "\n")
            except Exception as e:
                out_file.write(f"Error reading {rel_path}: {e}\n")

    print(f"\n✅ Full project dump saved to: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    dump_project_code_to_file(ROOT_DIR)
