def is_word_present(board: list[list[str]], word: str) -> bool:
    if not word:
        return False
    if not board or not board[0]:
        return False

    rows = len(board)
    cols = len(board[0])

    # Track which cells are in the current path
    used = [[False for _ in range(cols)] for _ in range(rows)]

    def recurse_in_boggle(x: int, y: int, index: int) -> bool:
        """
        We are currently at board[x][y], which already matches word[index-1].
        Now we want to match word[index], word[index+1], ...
        """
        # If we've matched all characters in the word
        if index == len(word):
            return True

        # Explore all neighbors (8 directions)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue  # skip the current cell itself

                nx, ny = x + dx, y + dy

                # Check bounds and whether we already used this cell
                if 0 <= nx < rows and 0 <= ny < cols and not used[nx][ny]:
                    if board[nx][ny] == word[index]:
                        used[nx][ny] = True
                        if recurse_in_boggle(nx, ny, index + 1):
                            return True
                        used[nx][ny] = False  # backtrack

        return False

    # Try starting from every cell that matches the first character
    for x in range(rows):
        for y in range(cols):
            if board[x][y] == word[0]:
                used[x][y] = True
                if recurse_in_boggle(x, y, 1):
                    return True
                used[x][y] = False  # backtrack

    return False

