import unittest
from util import Pos

class TestStack(unittest.TestCase):
    def test_init(self):
        p = Pos(0, 0)
        self.assertEqual(p.x, 0)
        self.assertEqual(p.y, 0)

    def test_pos_operations(self):
        p = Pos(1, 2) + Pos(2, 3)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 5)

        p = Pos(3, 4) - Pos(0, 1)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 3)

        p = Pos(3, 4) * Pos(2, 2)
        self.assertEqual(p.x, 6)
        self.assertEqual(p.y, 8)

        p = Pos(3, 4) // Pos(2, 2)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)

    def test_pos_comparisons(self):
        self.assertTrue(Pos(1, 2) < Pos(2, 4))
        self.assertFalse(Pos(1, 2) < Pos(1, 3))
        self.assertFalse(Pos(1, 2) < Pos(2, 2))

        self.assertTrue(Pos(3, 3) > Pos(2, 2))
        self.assertFalse(Pos(3, 3) > Pos(1, 3))
        self.assertFalse(Pos(3, 3) > Pos(3, 2))

        self.assertTrue(Pos(3, 3) >= Pos(2, 2))
        self.assertTrue(Pos(3, 3) >= Pos(1, 3))
        self.assertTrue(Pos(3, 3) >= Pos(3, 2))
        self.assertFalse(Pos(3, 3) >= Pos(4, 2))
        self.assertFalse(Pos(3, 3) >= Pos(2, 4))

    def test_int_operations(self):
        p = Pos(1, 2) + 3
        self.assertEqual(p.x, 4)
        self.assertEqual(p.y, 5)

        p = Pos(2, 3) - 2
        self.assertEqual(p.x, 0)
        self.assertEqual(p.y, 1)

        p = Pos(1, 2) * 3
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)

        p = Pos(2, 6) // 3
        self.assertEqual(p.x, 0)
        self.assertEqual(p.y, 2)

    def test_moves(self):
        p = Pos(3, 3)
        self.assertEqual(p.left(), Pos(2, 3))
        self.assertEqual(p.right(), Pos(4, 3))
        self.assertEqual(p.up(), Pos(3, 2))
        self.assertEqual(p.down(), Pos(3, 4))

        self.assertEqual(p.left(3), Pos(0, 3))
        self.assertEqual(p.right(3), Pos(6, 3))
        self.assertEqual(p.up(3), Pos(3, 0))
        self.assertEqual(p.down(3), Pos(3, 6))

        self.assertEqual(p.up().down(), p)
        self.assertEqual(p.right().left(), p)
        self.assertEqual(p.left(2).up(2), Pos(1, 1))

    def test_tuple(self):
        self.assertEqual(Pos(1, 1).tuple(), (1, 1))

if __name__ == '__main__':
    unittest.main()