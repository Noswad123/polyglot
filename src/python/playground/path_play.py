import os
from pathlib import Path

# Checking if a file exists
file_exists = os.path.exists('example.txt')
print(f"Does 'example.txt' exist? {file_exists}")

# Creating a directory
os.makedirs('new_directory', exist_ok=True)

# Listing files in a directory
files = os.listdir('.')
print(f"Files in current directory: {files}")

# Using pathlib for similar operations
path = Path('example.txt')
print(path.is_file())  # Check if it's a file
print(path.is_dir())   # Check if it's a directory

# Creating a directory using pathlib
Path('another_directory').mkdir(exist_ok=True)

# Listing files in a directory using pathlib
paths = Path('.').iterdir()
for path in paths:
    print(path)
