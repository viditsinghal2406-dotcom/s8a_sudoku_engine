"""
Series 8 — CORE | Project 8a
==============================
Sudoku Engine
- Solves any valid Sudoku using backtracking
- Generates puzzles at Easy / Medium / Hard difficulty
- Guarantees unique solution for every generated puzzle
- Playable interactive mode with hints + mistake tracking

Usage:
    python sudoku.py             → play a random Medium puzzle
    python sudoku.py --easy      → Easy puzzle
    python sudoku.py --hard      → Hard puzzle
    python sudoku.py --solve     → enter your own puzzle to solve
    python sudoku.py --generate  → just generate + show solution (no play)
"""

import random
import copy
import argparse
import time


# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────

def print_board(board, original=None, mistakes=None):
    print()
    print("     1 2 3   4 5 6   7 8 9")
    print("  ┌───────┬───────┬───────┐")
    for i, row in enumerate(board):
        if i in (3, 6):
            print("  ├───────┼───────┼───────┤")
        row_str = f" {i+1}│"
        for j, val in enumerate(row):
            is_clue   = original and original[i][j] != 0
            is_mistake = mistakes and (i, j) in mistakes

            if val == 0:
                cell = "·"
            elif is_mistake:
                cell = "✗"
            else:
                cell = str(val)

            row_str += f" {cell}"
            if j in (2, 5):
                row_str += " │"
        row_str += " │"
        print(row_str)
    print("  └───────┴───────┴───────┘")
    print()


# ─────────────────────────────────────────────
#  VALIDATOR
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  SOLVER
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  GENERATOR
# ─────────────────────────────────────────────

DIFFICULTY = {
    "easy":   (32, 36),
    "medium": (46, 49),
    "hard":   (52, 55),
}


def generate_full_board():
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    return board


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
    solution = generate_full_board()
    puzzle   = copy.deepcopy(solution)

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


# ─────────────────────────────────────────────
#  PLAY MODE
# ─────────────────────────────────────────────

def play(puzzle, solution, difficulty):
    board      = copy.deepcopy(puzzle)
    original   = copy.deepcopy(puzzle)
    mistakes   = set()
    hints_used = 0
    moves      = 0
    start_time = time.time()

    empty_total = 81 - count_clues(puzzle)

    print(f"\n  SUDOKU — {difficulty.upper()}  |  {empty_total} cells to fill")
    print()
    print("  Commands:")
    print("  row col num  → place a number      e.g.  3 5 7")
    print("  row col 0    → erase a cell         e.g.  3 5 0")
    print("  hint         → reveal a random cell (tracked)")
    print("  check        → check your board for errors")
    print("  solve        → give up and show solution")
    print("  quit         → exit")

    while True:
        print_board(board, original, mistakes)

        filled    = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)
        remaining = empty_total - (filled - count_clues(puzzle))
        elapsed   = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)

        print(f"  ⏱  {mins:02d}:{secs:02d}  |  {remaining} cells left  |  {len(mistakes)} mistake(s)  |  {hints_used} hint(s)")

        # Win condition
        if board == solution:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            print(f"\n  ✓ SOLVED!")
            print(f"  Time: {mins:02d}:{secs:02d}  |  Moves: {moves}  |  Mistakes: {len(mistakes)}  |  Hints: {hints_used}\n")
            break

        raw = input("\n  > ").strip().lower()
        if not raw:
            continue

        # ── QUIT ──
        if raw == "quit":
            print("\n  Quitting. Solution was:\n")
            print_board(solution)
            break

        # ── SOLVE ──
        if raw == "solve":
            print("\n  Solution:\n")
            print_board(solution)
            break

        # ── HINT ──
        if raw == "hint":
            empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
            if not empties:
                print("  No empty cells left!")
                continue
            r, c = random.choice(empties)
            board[r][c] = solution[r][c]
            mistakes.discard((r, c))
            hints_used += 1
            print(f"  Hint → Row {r+1}, Col {c+1} = {solution[r][c]}")
            continue

        # ── CHECK ──
        if raw == "check":
            wrong = [
                (r+1, c+1)
                for r in range(9) for c in range(9)
                if board[r][c] != 0 and original[r][c] == 0 and board[r][c] != solution[r][c]
            ]
            if not wrong:
                print("  ✓ All filled cells are correct so far!")
            else:
                print(f"  ✗ {len(wrong)} wrong cell(s) at: {wrong}")
            continue

        # ── MOVE ──
        parts = raw.split()
        if len(parts) != 3:
            print("  Invalid input. Use:  row col num   e.g. 3 5 7")
            continue

        try:
            r, c, num = int(parts[0])-1, int(parts[1])-1, int(parts[2])
        except ValueError:
            print("  Use numbers only.")
            continue

        if not (0 <= r <= 8 and 0 <= c <= 8):
            print("  Row and col must be between 1 and 9.")
            continue

        if not (0 <= num <= 9):
            print("  Number must be 1–9 (or 0 to erase).")
            continue

        if original[r][c] != 0:
            print("  That's a clue cell — can't be changed.")
            continue

        # Erase
        if num == 0:
            board[r][c] = 0
            mistakes.discard((r, c))
            print(f"  Erased ({r+1},{c+1})")
            continue

        # Place
        board[r][c] = num
        moves += 1

        if num == solution[r][c]:
            mistakes.discard((r, c))
            print(f"  ✓ Correct!")
        else:
            mistakes.add((r, c))
            print(f"  ✗ {num} is incorrect at ({r+1},{c+1})")


# ─────────────────────────────────────────────
#  MANUAL SOLVE MODE
# ─────────────────────────────────────────────

def input_board():
    print("\n  Enter your puzzle row by row.")
    print("  Use 0 or . for empty cells. Spaces optional.")
    print("  Example: 5 3 0 0 7 0 0 0 0\n")
    board = []
    for i in range(9):
        while True:
            raw = input(f"  Row {i+1}: ").strip().replace(".", "0").replace(" ", "")
            if len(raw) == 9 and raw.isdigit():
                board.append([int(ch) for ch in raw])
                break
            print("  ✗ Invalid. Enter exactly 9 digits.")
    return board


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sudoku Engine — 8a")
    group  = parser.add_mutually_exclusive_group()
    group.add_argument("--easy",     action="store_true", help="Easy puzzle")
    group.add_argument("--medium",   action="store_true", help="Medium puzzle (default)")
    group.add_argument("--hard",     action="store_true", help="Hard puzzle")
    group.add_argument("--solve",    action="store_true", help="Solve your own puzzle")
    group.add_argument("--generate", action="store_true", help="Generate + show solution only")
    args = parser.parse_args()

    print("\n  ╔══════════════════════════════╗")
    print("  ║     SUDOKU ENGINE  — 8a      ║")
    print("  ╚══════════════════════════════╝")

    # Manual solve mode
    if args.solve:
        puzzle = input_board()
        print_board(puzzle, puzzle)
        board_copy = copy.deepcopy(puzzle)
        t = time.time()
        if solve(board_copy):
            print_board(board_copy)
            print(f"  Solved in {(time.time()-t)*1000:.2f}ms\n")
        else:
            print("\n  ✗ No solution exists for this puzzle.\n")
        return

    # Difficulty
    if args.easy:   diff = "easy"
    elif args.hard: diff = "hard"
    else:           diff = "medium"

    print(f"\n  Generating {diff.upper()} puzzle...", end="", flush=True)
    t = time.time()
    puzzle, solution = generate_puzzle(diff)
    print(f" done ({time.time()-t:.2f}s)")
    print(f"  Clues: {count_clues(puzzle)}/81")

    # Generate only
    if args.generate:
        print_board(puzzle, puzzle)
        input("  Press Enter to reveal solution...")
        print_board(solution)
        return

    # Play
    play(puzzle, solution, diff)


if __name__ == "__main__":
    main()