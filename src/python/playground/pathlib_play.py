from pathlib import Path

# Define the path to the file
file_path = Path('./data/file.txt')

file_path.parent.mkdir(exist_ok=False)

bad_path = Path('DNE')

if bad_path.exists():
    print(bad_path.read_text())
else:
    print(f"File not found: {bad_path}")

# --- Appending to a file ---
# pathlib doesn't have a direct "append" method.
# You can read the content and then write it back with the new text.
# Note: For very large files, `with open(file_path, 'a')` is more memory-efficient.
try:
    # Read existing content, or start fresh if the file doesn't exist
    existing_content = file_path.read_text() if file_path.exists() else ""
    file_path.write_text(existing_content + "hey Jamal\n")
except Exception as e:
    print(f"An error occurred: {e}")

# --- Reading the entire file content ---
# Use .read_text() for a simple way to get the file's contents
print("--- File Content ---")
print(file_path.read_text())
