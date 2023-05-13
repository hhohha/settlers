import unittest
from unittest.mock import MagicMock

import config
from card import Town, Village, Building, Landscape
from enums import Resource
from player import Player
from util import Pos, Cost


class TestStack(unittest.TestCase):
    def setUp(self):
        self.gameMock = MagicMock()
        self.handBoardMock = MagicMock()
        Player.__abstractmethods__ = set()

    def test_init(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertIs(p.game, self.gameMock)
        self.assertIs(p.opponent, p)
        self.assertIs(p.handBoard, self.handBoardMock)
        self.assertEqual(p.number, 1)
        self.assertEqual(p.victoryPoints, 0)
        self.assertEqual(p.cardsInHandCnt, config.STARTING_HAND_CARD_CNT)
        self.assertEqual(p.cardsInHand, [])
        self.assertEqual(p.landscapeCards, [])
        self.assertEqual(p.knightsPlayed, [])
        self.assertEqual(p.fleetPlayed, [])
        self.assertEqual(p.buildingsPlayed, [])
        self.assertEqual(p.settlements, [])
        self.assertEqual(p.paths, [])
        self.assertEqual(p.handBoardVisible, False)
        self.assertEqual(p.midPos, Pos(7, 2))
        for idx, pos in enumerate([Pos(7, 1), Pos(7, 3), Pos(9, 1), Pos(9, 3), Pos(5, 1), Pos(5, 3)]):
            self.assertEqual(p.initialLandPos[idx], pos)

    def test_victory_points(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))

        p.opponent = MagicMock()
        p.opponent.get_trade_strength = MagicMock(return_value=4)
        p.opponent.get_battle_strength = MagicMock(return_value=2)
        self.assertEqual(p.get_victory_points(), 0)

        p.get_trade_strength = MagicMock(return_value=6)
        p.get_battle_strength = MagicMock(return_value=2)
        self.assertEqual(p.get_victory_points(), 1)

        p.get_battle_strength = MagicMock(return_value=3)
        self.assertEqual(p.get_victory_points(), 2)

        p.settlements.append(Town(Pos(1, 1), p))
        p.settlements.append(Village(Pos(1, 2), p))
        p.settlements.append(Village(Pos(1, 3), p))
        self.assertEqual(p.get_victory_points(), 6)

        p.buildingsPlayed.append(Building('', Cost(), False, 1, 0))
        p.buildingsPlayed.append(Building('', Cost(), False, 2, 0))
        self.assertEqual(p.get_victory_points(), 9)

    def test_get_resources(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))

        self.assertEqual(p.get_resources_available(), Cost())

        p.landscapeCards.append(Landscape('gold', Resource.GOLD, 1))
        p.landscapeCards.append(Landscape('wood', Resource.WOOD, 1))
        p.landscapeCards.append(Landscape('gold', Resource.GOLD, 1))
        p.landscapeCards.append(Landscape('brick', Resource.BRICK, 1))
        self.assertEqual(p.get_resources_available(), Cost())

        p.landscapeCards[0].resourcesHeld = 2
        self.assertEqual(p.get_resources_available(), Cost(gold=2))

        p.landscapeCards[1].resourcesHeld = 1
        p.landscapeCards[2].resourcesHeld = 2
        p.landscapeCards[3].resourcesHeld = 3
        self.assertEqual(p.get_resources_available(), Cost(gold=4, wood=1, brick=3))

    def test_can_cover_cost(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        p.get_resources_available = MagicMock(return_value=Cost())

        self.assertTrue(p.can_cover_cost(0))
        self.assertTrue(p.can_cover_cost(Cost()))
        self.assertFalse(p.can_cover_cost(1))
        self.assertFalse(p.can_cover_cost(Cost(rock=1)))

        p.get_resources_available = MagicMock(return_value=Cost(brick=1, rock=2, gold=3, grain=4))
        self.assertTrue(p.can_cover_cost(9))
        self.assertTrue(p.can_cover_cost(10))
        self.assertFalse(p.can_cover_cost(11))

        self.assertTrue(p.can_cover_cost(Cost(brick=1)))
        self.assertFalse(p.can_cover_cost(Cost(wood=1)))
        self.assertFalse(p.can_cover_cost(Cost(brick=2)))
        self.assertTrue(p.can_cover_cost(Cost(brick=1, rock=2, gold=3, grain=4)))
        self.assertFalse(p.can_cover_cost(Cost(brick=1, rock=2, gold=3, grain=5)))
        self.assertFalse(p.can_cover_cost(Cost(brick=1, rock=2, gold=3, grain=4, sheep=2)))

