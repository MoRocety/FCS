import os
import ast

def get_dependencies_from_file(filepath):
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read())
    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                module = node.module if node.module else ''
                dependencies.add(f"{module}.{alias.name}")
    return dependencies

def get_all_py_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def main():
    folder_path = "."  # Change this to the folder containing your .py files
    requirements_file = "requirements.txt"

    all_dependencies = set()

    for filepath in get_all_py_files(folder_path):
        dependencies = get_dependencies_from_file(filepath)
        all_dependencies.update(dependencies)

    with open(requirements_file, 'w') as req_file:
        req_file.write('\n'.join(sorted(all_dependencies)))

    print(f"Dependencies written to {requirements_file}.")

if __name__ == "__main__":
    main()
