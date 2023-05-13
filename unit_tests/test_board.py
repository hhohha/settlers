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

    def test_get_set_clear_square(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertIsNone(b.get_square(Pos(0, 0)))
        self.assertEqual(b.editedSquares, [])

        card = MetaCard('')
        b.set_square(Pos(1, 1), card)
        self.assertIs(b.get_square(Pos(1, 1)), card)
        self.assertEqual(len(b.editedSquares), 1)
        self.assertEqual(b.editedSquares[0], Pos(1, 1))

        b.clear_square(Pos(1, 1))
        self.assertIsNone(b.get_square(Pos(1, 1)))
        self.assertEqual(len(b.editedSquares), 2)
        self.assertEqual(b.editedSquares[1], Pos(1, 1))

    def test_refresh(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertEqual(b.editedSquares, [])

        b.refresh_square(Pos(1, 1))
        self.assertEqual(len(b.editedSquares), 1)
        self.assertEqual(b.editedSquares[0], Pos(1, 1))

        with self.assertRaises(AssertionError):
            b.refresh_square(Pos(7, 1))

    def test_set_top_left(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        b.spacing = 2
        self.assertIsNone(b.topLeft)
        self.assertIsNone(b.bottomRight)
        b.set_top_left(Pos(0, 0))
        self.assertEqual(b.topLeft, Pos(0, 0))
        self.assertEqual(b.bottomRight, Pos(270, 270))

        b = Board(Pos(2, 10), Pos(20, 30))
        b.spacing = 3
        self.assertIsNone(b.topLeft)
        self.assertIsNone(b.bottomRight)
        b.set_top_left(Pos(50, 100))
        self.assertEqual(b.topLeft, Pos(50, 100))
        self.assertEqual(b.bottomRight, Pos(102, 460))

    def test_get_edited_squares(self):
        b = Board(Pos(5, 5), Pos(50, 50))
        self.assertEqual(len(b.editedSquares), 0)

        b.refresh_square(Pos(1, 0))
        b.refresh_square(Pos(1, 1))
        b.refresh_square(Pos(1, 2))

        self.assertEqual(len(b.editedSquares), 3)
        cnt = 2
        for pos in b.get_edited_squares():
            self.assertEqual(len(b.editedSquares), cnt)
            self.assertEqual(pos, Pos(1, cnt))
            cnt -= 1

        self.assertEqual(len(b.editedSquares), 0)

    def test_fill_clear(self):
        b = Board(Pos(2, 2), Pos(50, 50))

        b.fill_board(MetaCard('meta'))

        self.assertEqual(len(b.editedSquares), 4)
        for i in range(4):
            self.assertEqual(b.get_square(b.to_pos(i)).name, 'meta')
            self.assertEqual(b.editedSquares[i], b.to_pos(i))

        b.editedSquares = []

        b.clear()
        self.assertEqual(len(b.editedSquares), 4)
        for i in range(4):
            self.assertIsNone(b.get_square(b.to_pos(i)))
            self.assertEqual(b.editedSquares[i], b.to_pos(i))

