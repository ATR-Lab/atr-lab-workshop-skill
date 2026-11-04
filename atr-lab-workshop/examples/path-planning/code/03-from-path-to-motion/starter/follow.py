"""Drive a simulated differential-drive robot along an A* path.

The robot is a point at (x, y) in map units (x = column, y = row; cell centers sit at .5) with a heading in
radians. Each tick it picks a look-ahead point on the path, turns toward it at a limited rate and moves forward.

Run it:  python3 follow.py            (add --plot to draw it, if matplotlib is installed)
"""
import math
import sys

from astar import astar
from grid import MAPS, load_map, show


def simplify(path):
    """Keep the start, every corner and the goal: the cells where the direction changes."""
    # TODO step 1: keep path[0], every cell where the step direction changes, and path[-1].
    raise NotImplementedError("simplify: your turn")


def center(cell):
    """(x, y) of a cell's center."""
    return cell[1] + 0.5, cell[0] + 0.5


def lookahead_point(waypoints, index, position, lookahead):
    """Advance past waypoints closer than the look-ahead distance; return (target point, new index)."""
    # TODO step 2: while the waypoint at `index` is closer than `lookahead` (and is not the last),
    # move index on. Return (center of that waypoint, index).
    raise NotImplementedError("lookahead_point: your turn")


def steer(heading, position, target, max_turn):
    """The new heading: turn toward the target, by at most max_turn radians."""
    # TODO step 3: the angle to the target is atan2(dy, dx). Wrap the error into [-pi, pi)
    # and turn by it, clamped to +/- max_turn.
    raise NotImplementedError("steer: your turn")


def simulate(grid, path, lookahead=0.6, speed=0.1, max_turn=0.35, max_ticks=3000):
    """Return (trajectory, reached, crashed). The robot starts on the first cell, facing the second waypoint."""
    waypoints = simplify(path)
    x, y = center(waypoints[0])
    goal = center(waypoints[-1])
    first = center(waypoints[1]) if len(waypoints) > 1 else goal
    heading = math.atan2(first[1] - y, first[0] - x)
    trajectory = [(x, y)]
    index = 1
    for _ in range(max_ticks):
        if math.dist((x, y), goal) < speed:
            return trajectory, True, False
        target, index = lookahead_point(waypoints, index, (x, y), lookahead)
        heading = steer(heading, (x, y), target, max_turn)
        x, y = x + speed * math.cos(heading), y + speed * math.sin(heading)
        trajectory.append((x, y))
        if grid[int(y)][int(x)]:
            return trajectory, False, True
    return trajectory, False, False


if __name__ == "__main__":
    grid, start, goal = load_map(MAPS / "warehouse.txt")
    path, _ = astar(grid, start, goal)
    trajectory, reached, crashed = simulate(grid, path)
    visited = {(int(py), int(px)) for px, py in trajectory}
    print(show(grid, visited, start, goal))
    print(f"\n{len(simplify(path))} waypoints, {len(trajectory)} ticks: "
          + ("reached the goal" if reached else "crashed into a wall" if crashed else "ran out of time"))
    if "--plot" in sys.argv:
        import matplotlib.pyplot as plt
        plt.imshow(grid, cmap="Greys", origin="upper", extent=(0, len(grid[0]), len(grid), 0))
        plt.plot(*zip(*trajectory), color="#003976")
        plt.title("Robot trajectory")
        plt.show()
