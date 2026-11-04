"""Checks for astar.py. Run:  python3 test_astar.py"""
import unittest

from astar import astar, euclidean, manhattan, zero
from grid import MAPS, load_map, neighbors


class AStarTest(unittest.TestCase):
    def setUp(self):
        self.grid, self.start, self.goal = load_map(MAPS / "warehouse.txt")

    def test_path_joins_start_and_goal(self):
        path, _ = astar(self.grid, self.start, self.goal)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)

    def test_every_step_is_a_legal_move(self):
        path, _ = astar(self.grid, self.start, self.goal)
        for a, b in zip(path, path[1:]):
            self.assertIn(b, neighbors(self.grid, a))

    def test_heuristics_agree_on_the_shortest_length(self):
        lengths = {len(astar(self.grid, self.start, self.goal, h)[0]) for h in (zero, manhattan, euclidean)}
        self.assertEqual(len(lengths), 1)

    def test_a_heuristic_expands_fewer_cells(self):
        _, blind = astar(self.grid, self.start, self.goal, zero)
        _, guided = astar(self.grid, self.start, self.goal, manhattan)
        self.assertLess(guided, blind)

    def test_unreachable_goal_returns_no_path(self):
        walled = [row[:] for row in self.grid]
        for cell in neighbors(self.grid, self.goal):
            walled[cell[0]][cell[1]] = True
        self.assertEqual(astar(walled, self.start, self.goal)[0], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
