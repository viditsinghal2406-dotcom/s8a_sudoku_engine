"""
Sudoku Engine — core logic
Used by both CLI (sudoku.py) and web app (app.py)
"""

import random
import copy

DIFFICULTY = {
    "easy":   (32, 36),
    "medium": (46, 49),
    "hard":   (52, 55),
}


def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def solve(board):
    pos = find_empty(board)
    if not pos:
        return True
    row, col = pos
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0
    return False


def count_solutions(board, limit=2):
    pos = find_empty(board)
    if not pos:
        return 1
    row, col = pos
    total = 0
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            total += count_solutions(board, limit)
            board[row][col] = 0
            if total >= limit:
                return total
    return total


def fill_board(board):
    pos = find_empty(board)
    if not pos:
        return True
    row, col = pos
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if fill_board(board):
                return True
            board[row][col] = 0
    return False


def generate_puzzle(difficulty="medium"):
    solution = [[0] * 9 for _ in range(9)]
    fill_board(solution)
    puzzle = copy.deepcopy(solution)

    min_remove, max_remove = DIFFICULTY[difficulty]
    target = random.randint(min_remove, max_remove)

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if removed >= target:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        test = copy.deepcopy(puzzle)
        if count_solutions(test) != 1:
            puzzle[r][c] = backup
        else:
            removed += 1

    return puzzle, solution


def count_clues(board):
    return sum(1 for r in board for c in r if c != 0)


def get_hint(board, solution):
    """Return (row, col, value) for a random empty cell."""
    empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
    if not empties:
        return None
    r, c = random.choice(empties)
    return r, c, solution[r][c]


def check_board(board, original, solution):
    """Return list of (row, col) cells that are wrong."""
    wrong = []
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0 and original[r][c] == 0:
                if board[r][c] != solution[r][c]:
                    wrong.append((r, c))
    return wrong


def is_solved(board, solution):
    return board == solution