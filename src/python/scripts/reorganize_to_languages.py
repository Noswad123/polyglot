import os
import shutil
from collections import defaultdict

# Map file extensions to language folders
LANG_EXTS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.go': 'go',
    '.lua': 'lua',
    # Add more as needed!
}

IGNORE_FILES = {
    'instructions.md', 'package.json', 'package-lock.json', 'tsconfig.json', 'tests'
}

KATAS_ROOT = 'src/katas'
LANG_ROOT = 'src/languages'

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_language_from_ext(filename):
    ext = os.path.splitext(filename)[1]
    return LANG_EXTS.get(ext, None)

def main(move_files=True):
    problems = [d for d in os.listdir(KATAS_ROOT) if os.path.isdir(os.path.join(KATAS_ROOT, d))]
    file_count = defaultdict(int)

    for problem in problems:
        kata_dir = os.path.join(KATAS_ROOT, problem)
        for fname in os.listdir(kata_dir):
            if fname in IGNORE_FILES or fname.startswith('test') or fname == 'tests':
                continue
            lang = get_language_from_ext(fname)
            if not lang:
                continue  # Skip files not in LANG_EXTS

            lang_dir = os.path.join(LANG_ROOT, lang, 'katas')
            ensure_dir(lang_dir)

            src_file = os.path.join(kata_dir, fname)
            dst_file = os.path.join(lang_dir, fname)
            if move_files:
                shutil.move(src_file, dst_file)
                print(f'Moved: {src_file} -> {dst_file}')
            else:
                shutil.copy2(src_file, dst_file)
                print(f'Copied: {src_file} -> {dst_file}')
            file_count[lang] += 1

    print('\nSummary:')
    for lang, count in file_count.items():
        print(f'{lang}: {count} files moved/copied.')

if __name__ == "__main__":
    main(move_files=True)  # Change to False to copy instead of move