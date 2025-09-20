file_path = './data/file.txt'
bad_path = 'DNE'
try:
    with open(bad_path, 'r') as b:
        b.read()
except FileNotFoundError:
    print("file not found dummy!")

try:
    with open(file_path, 'a') as f:
        f.write("hey Jamal\n")
except FileNotFoundError:
    print("file not found dummy!")

with open(file_path, 'r') as r_file:
    print(r_file.read())

