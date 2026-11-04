"""Occupancy grids: load a map file and list the free neighbors of a cell.

A map file is text: '#' is a wall, '.' is free floor, 'S' is the start and 'G' is the goal.
A cell is a (row, column) pair; row 0 is the top line of the file.

Run it to print the map:  python3 grid.py
"""
from pathlib import Path

MAPS = Path(__file__).resolve().parents[2] / "maps"
WALL = "#"
SIDE_STEPS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL_STEPS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def load_map(path):
    """Read a map file and return (grid, start, goal); grid[row][col] is True where there is a wall."""
    lines = [line for line in Path(path).read_text().splitlines() if line.strip()]
    grid, start, goal = [], None, None
    for row, line in enumerate(lines):
        cells = []
        for col, char in enumerate(line):
            if char == "S":
                start = (row, col)
            elif char == "G":
                goal = (row, col)
            cells.append(char == WALL)
        grid.append(cells)
    return grid, start, goal


def is_free(grid, cell):
    """True when the cell is inside the map and not a wall."""
    row, col = cell
    return 0 <= row < len(grid) and 0 <= col < len(grid[0]) and not grid[row][col]


def neighbors(grid, cell, diagonal=False):
    """The free cells one step away. Diagonal steps may not cut the corner of a wall."""
    row, col = cell
    steps = SIDE_STEPS + (DIAGONAL_STEPS if diagonal else [])
    found = []
    for d_row, d_col in steps:
        nxt = (row + d_row, col + d_col)
        if not is_free(grid, nxt):
            continue
        if d_row and d_col and not (is_free(grid, (row + d_row, col)) and is_free(grid, (row, col + d_col))):
            continue
        found.append(nxt)
    return found


def show(grid, path=(), start=None, goal=None):
    """The map as text, with the path drawn as '*'."""
    on_path = set(path)
    rows = []
    for r, cells in enumerate(grid):
        line = ""
        for c, wall in enumerate(cells):
            if (r, c) == start:
                line += "S"
            elif (r, c) == goal:
                line += "G"
            elif (r, c) in on_path:
                line += "*"
            else:
                line += WALL if wall else "."
        rows.append(line)
    return "\n".join(rows)


if __name__ == "__main__":
    grid, start, goal = load_map(MAPS / "warehouse.txt")
    print(show(grid, start=start, goal=goal))
    print(f"\n{len(grid)} rows x {len(grid[0])} columns, start {start}, goal {goal}")
    print(f"neighbors of the start: {neighbors(grid, start)}")
