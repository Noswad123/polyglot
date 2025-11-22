import os
import re

def camel_to_snake(name: str) -> str:
    # Split camelCase or PascalCase into words and join with underscores
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def rename_files_in_dir(root_dir: str):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            new_name = camel_to_snake(name) + ext

            if new_name != filename:
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_name)
                print(f"Renaming: {filename} -> {new_name}")
                os.rename(old_path, new_path)

if __name__ == "__main__":
    rename_files_in_dir("../katas")
