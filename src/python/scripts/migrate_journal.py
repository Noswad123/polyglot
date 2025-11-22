import re
import os
from collections import defaultdict

# Files to process (add more as needed)
files = ['Exercise.txt', 'Random.txt', 'Read.txt', 'Code.txt', 'Love.txt', 'Action.txt', 'Amusement.txt', 'Music.txt']

date_re = re.compile(
    r'Date:\s+([A-Za-z]+) (\d+), (\d{4}) at ([\d:]+)\s*([AP]M)', re.MULTILINE)

# Nested dict: {year: {month: {day: {time: {source_file: [notes]}}}}}
data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

for fname in files:
    with open(fname, 'r') as f:
        raw = f.read()
    entries = re.split(r'(?=Date:)', raw)
    for entry in entries:
        m = date_re.search(entry)
        if not m:
            continue
        month, day, year, time, ampm = m.groups()
        day = str(int(day))
        time_short = time[:5]
        time_fmt = f"{time_short} {ampm}"

        # Get just the main notes
        parts = entry.split('\n\n', 1)
        notes = []
        if len(parts) == 2:
            note_block = parts[1].strip()
            if note_block:
                # Preserve existing subheaders (lines starting with **)
                lines = [l for l in note_block.splitlines() if l.strip()]
                notes = lines

        # Use file base name (without extension) as subheader
        source_name = os.path.splitext(os.path.basename(fname))[0].capitalize()
        data[year][month][day][time_fmt].setdefault(source_name, []).extend(notes)

# Output to .norg files
for year in data:
    folder = f"Y{year}"
    os.makedirs(folder, exist_ok=True)
    for month in data[year]:
        path = os.path.join(folder, f"{month}.norg")
        with open(path, "w") as f:
            for day in sorted(data[year][month], key=int):
                for time in sorted(data[year][month][day]):
                    f.write(f"* {month} {day} @ {time}\n")
                    for source in sorted(data[year][month][day][time]):
                        notes = data[year][month][day][time][source]
                        f.write(f"    ** {source}\n")
                        for note in notes:
                            if note.strip().startswith("**"):
                                f.write(f"        {note.strip()}\n")
                            else:
                                f.write(f"        - {note.strip()}\n")
                        f.write("\n")
