import os
import re
import sys


def remove_whitespace_comments_docstrings(file_path):
    with open(file_path, "r") as file:
        code = file.read()
    code = re.sub(r"#.*", "", code)
    code = re.sub(r"", "", code, flags=re.DOTALL)
    code = re.sub(r"", "", code, flags=re.DOTALL)
    code = re.sub(r"\n\s*\n", "\n", code)
    with open(file_path, "w") as file:
        file.write(code)


def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                remove_whitespace_comments_docstrings(file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <relative_directory_path>")
        sys.exit(1)
    relative_path = sys.argv[1]
    process_directory(relative_path)
