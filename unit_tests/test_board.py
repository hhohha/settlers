import unittest
from unittest.mock import MagicMock

import config
from board import Board
from card import MetaCard
from util import Pos


class TestStack(unittest.TestCase):
    def test_init(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertEqual(b.size, Pos(5, 5))
        self.assertEqual(b.squareSize, Pos(50, 50))
        self.assertEqual(len(b.squares), b.size.x * b.size.y)
        self.assertEqual(b.editedSquares, [])
        self.assertIsNone(b.topLeft)
        self.assertIsNone(b.bottomRight)
        self.assertEqual(b.spacing, config.CARD_IMG_SPACING)

    def test_to_int_and_pos(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertEqual(b.to_int(Pos(0, 0)), 0)
        self.assertEqual(b.to_int(Pos(1, 0)), 1)
        self.assertEqual(b.to_int(Pos(0, 1)), 5)
        self.assertEqual(b.to_int(Pos(4, 4)), 24)

        with self.assertRaises(AssertionError):
            b.to_int(Pos(4, 5))

        self.assertEqual(b.to_pos(0), Pos(0, 0))
        self.assertEqual(b.to_pos(1), Pos(1, 0))
        self.assertEqual(b.to_pos(5), Pos(0, 1))
        self.assertEqual(b.to_pos(24), Pos(4, 4))

        with self.assertRaises(AssertionError):
            b.to_pos(25)

    def test_get_set_square(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertIsNone(b.get_square(Pos(0, 0)))
        self.assertEqual(b.editedSquares, [])

        card = MetaCard('')
        b.set_square(Pos(1, 1), card)
        self.assertIs(b.get_square(Pos(1, 1)), card)
        self.assertEqual(len(b.editedSquares), 1)
        self.assertEqual(b.editedSquares[0], Pos(1, 1))