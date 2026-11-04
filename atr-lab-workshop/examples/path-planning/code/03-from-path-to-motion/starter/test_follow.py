"""Checks for follow.py. Run:  python3 test_follow.py"""
import math
import unittest

from astar import astar
from follow import simplify, simulate, steer
from grid import MAPS, load_map


class FollowTest(unittest.TestCase):
    def setUp(self):
        self.grid, self.start, self.goal = load_map(MAPS / "warehouse.txt")
        self.path, _ = astar(self.grid, self.start, self.goal)

    def test_simplify_keeps_the_ends_and_drops_straight_runs(self):
        corners = simplify(self.path)
        self.assertEqual((corners[0], corners[-1]), (self.start, self.goal))
        self.assertLess(len(corners), len(self.path))
        self.assertEqual(simplify([(0, 0), (0, 1), (0, 2)]), [(0, 0), (0, 2)])

    def test_steer_turns_toward_the_target_within_the_limit(self):
        heading = steer(0.0, (0.0, 0.0), (0.0, 1.0), max_turn=0.2)
        self.assertAlmostEqual(heading, 0.2)
        self.assertAlmostEqual(steer(0.0, (0.0, 0.0), (1.0, 0.1), max_turn=1.0), math.atan2(0.1, 1.0))

    def test_robot_reaches_the_goal_without_crashing(self):
        _, reached, crashed = simulate(self.grid, self.path)
        self.assertFalse(crashed)
        self.assertTrue(reached)


if __name__ == "__main__":
    unittest.main(verbosity=2)
