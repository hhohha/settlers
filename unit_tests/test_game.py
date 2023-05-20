import unittest, sys
from game import Game
from unittest.mock import MagicMock

sys.modules[Game.__module__].DisplayHandler = MagicMock()

class TestStack(unittest.TestCase):
    def test_init(self):
        game = Game()

        self.assertIs(game.player1.opponent, game.player2)
        self.assertIs(game.player2.opponent, game.player1)
        self.assertIs(game.currentPlayer, game.player1)

