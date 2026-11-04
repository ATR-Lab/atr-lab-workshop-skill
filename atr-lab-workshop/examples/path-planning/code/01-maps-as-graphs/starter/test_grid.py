"""Checks for grid.py. Run:  python3 test_grid.py"""
import unittest

from grid import MAPS, load_map, neighbors


class GridTest(unittest.TestCase):
    def setUp(self):
        self.grid, self.start, self.goal = load_map(MAPS / "warehouse.txt")

    def test_map_size_and_markers(self):
        self.assertEqual((len(self.grid), len(self.grid[0])), (12, 20))
        self.assertEqual(self.start, (1, 1))
        self.assertEqual(self.goal, (10, 18))

    def test_walls(self):
        self.assertTrue(self.grid[0][0])
        self.assertFalse(self.grid[1][1])

    def test_neighbors_of_the_start(self):
        self.assertEqual(sorted(neighbors(self.grid, self.start)), [(1, 2), (2, 1)])

    def test_neighbors_stay_inside_the_map(self):
        for cell in neighbors(self.grid, (10, 18)):
            self.assertTrue(0 <= cell[0] < 12 and 0 <= cell[1] < 20)

    def test_diagonal_steps_do_not_cut_corners(self):
        self.assertNotIn((2, 2), neighbors(self.grid, (1, 1), diagonal=True))
        self.assertIn((10, 17), neighbors(self.grid, (9, 18), diagonal=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
