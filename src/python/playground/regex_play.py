import re
# Find all Matches
text_to_search = 'abc abc abc def abc'
pattern = re.compile(r'abc')
pattern.finditer(text_to_search)

# more memory efficient than findall which returns a list of all matches

# Using Groups (match objects)
# Group example to capture parts of a pattern
pattern = r"(\w+) (\w+)"
text = "John Doe"

match = re.match(pattern, text)

if match:
    print(f"Full match: {match.group(0)}")
    print(f"First group: {match.group(1)}")
    print(f"Second group: {match.group(2)}")

    # • Each match object provides methods like:
    # • match.group() - The matched string.
    # • match.start() - Start index of the match.
    # • match.end() - End index of the match (exclusive).
    # • match.span() - Tuple of(start, end).

text = "The rain in Spain stays mainly in the plain."

# Search for the word "rain"
match = re.search(r"rain", text)

if match:
  print(f"Found '{match.group()}' at {match.start()}-{match.end()}")
