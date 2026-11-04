"""A* search on an occupancy grid.

Run it to plan across the warehouse and compare heuristics:  python3 astar.py
"""
import heapq
import math

from grid import MAPS, load_map, neighbors, show


def zero(cell, goal):
    """No heuristic: A* becomes Dijkstra's algorithm and explores in every direction."""
    return 0.0


def manhattan(cell, goal):
    """Steps along rows plus steps along columns: exact for 4-connected moves."""
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def euclidean(cell, goal):
    """Straight-line distance: never overestimates, so A* stays optimal with diagonal moves too."""
    return math.hypot(cell[0] - goal[0], cell[1] - goal[1])


def step_cost(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def reconstruct(came_from, goal):
    path = [goal]
    while came_from[path[-1]] is not None:
        path.append(came_from[path[-1]])
    return path[::-1]


def astar(grid, start, goal, heuristic=manhattan, diagonal=False):
    """Return (path, expanded): the cells from start to goal ([] if unreachable) and how many cells were expanded."""
    open_set = [(heuristic(start, goal), 0.0, start)]
    cost_so_far = {start: 0.0}
    came_from = {start: None}
    closed = set()
    while open_set:
        _, cost, cell = heapq.heappop(open_set)
        if cell in closed:
            continue
        closed.add(cell)
        if cell == goal:
            return reconstruct(came_from, goal), len(closed)
        for nxt in neighbors(grid, cell, diagonal):
            new_cost = cost + step_cost(cell, nxt)
            if new_cost < cost_so_far.get(nxt, math.inf):
                cost_so_far[nxt] = new_cost
                came_from[nxt] = cell
                heapq.heappush(open_set, (new_cost + heuristic(nxt, goal), new_cost, nxt))
    return [], len(closed)


if __name__ == "__main__":
    grid, start, goal = load_map(MAPS / "warehouse.txt")
    path, _ = astar(grid, start, goal)
    print(show(grid, path, start, goal))
    print(f"\npath: {len(path) - 1} steps")
    for name, h in (("zero (Dijkstra)", zero), ("manhattan", manhattan), ("euclidean", euclidean)):
        found, expanded = astar(grid, start, goal, h)
        print(f"{name:>16}: {len(found) - 1} steps, {expanded} cells expanded")
