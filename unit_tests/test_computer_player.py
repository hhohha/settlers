import unittest

from unittest.mock import MagicMock
import config
from card import Building, Fleet, Knight, Action
from computer_player import ComputerPlayer
from enums import Resource
from util import Pos, Cost


class TestStack(unittest.TestCase):
    def test_init(self):
        p = ComputerPlayer(MagicMock(), MagicMock(), 2, Pos(7, 2))
        self.assertFalse(p.hasEmptyPath)
        self.assertIs(p.opponent, p)
        self.assertEqual(p.number, 2)
        self.assertEqual(p.victoryPoints, 0)
        self.assertEqual(p.cardsInHandDefaultCnt, config.STARTING_HAND_CARD_CNT)
        self.assertEqual(p.cardsInHand, [])
        self.assertEqual(p.landscapeCards, [])
        self.assertEqual(p.knightsPlayed, [])
        self.assertEqual(p.fleetPlayed, [])
        self.assertEqual(p.buildingsPlayed, [])
        self.assertEqual(p.settlements, [])
        self.assertEqual(p.paths, [])
        self.assertEqual(p.cardsVisible, False)
        self.assertEqual(p.midPos, Pos(7, 2))
        for idx, pos in enumerate([Pos(7, 1), Pos(7, 3), Pos(9, 1), Pos(9, 3), Pos(5, 1), Pos(5, 3)]):
            self.assertEqual(p.initialLandPos[idx], pos)

    def test_pick_starting_cards(self):
        p = ComputerPlayer(MagicMock(), MagicMock(), 2, Pos(7, 2))

        pile = [
            Building('warehouse', Cost(), False, 0, 0),
            Knight('jose', Cost(brick=1), 1, 1),
            Building('mill', Cost(), False, 1, 1),
            Fleet('fleet_wood', Cost(), Resource.WOOD, 1),
            Action('caravan'),
            Action('arson')
        ]
        p.select_pile = MagicMock(return_value=pile)

        p.pick_starting_cards()
        self.assertEqual(len(p.cardsInHand), 3)
        self.assertEqual(list(map(lambda c: c.name, p.cardsInHand)), ['warehouse', 'mill', 'jose'])
        self.assertEqual(list(map(lambda c: c.name, pile)), ['fleet_wood', 'caravan', 'arson'])

        p.cardsInHand = []
        pile = [
            Knight('jose', Cost(brick=1), 1, 1),
            Building('warehouse', Cost(), False, 0, 0),
            Knight('tonda', Cost(brick=1, rock=1), 1, 1),
            Building('warehouse', Cost(), False, 0, 0),
        ]
        p.select_pile = MagicMock(return_value=pile)
        p.pick_starting_cards()
        self.assertEqual(len(p.cardsInHand), 3)
        self.assertEqual(list(map(lambda c: c.name, p.cardsInHand)), ['warehouse', 'jose', 'warehouse'])
        self.assertEqual(list(map(lambda c: c.name, pile)), ['tonda'])

        p.cardsInHand = []
        pile = [
            Building('sawmill', Cost(), False, 0, 0),
            Building('brick_mill', Cost(), False, 0, 0),
            Building('cloister', Cost(), False, 0, 0),
            Building('steel_mill', Cost(), False, 0, 0),
            Building('spinning_mill', Cost(), False, 0, 0),
            Building('mill', Cost(), False, 0, 0),
        ]
        p.select_pile = MagicMock(return_value=pile)
        p.pick_starting_cards()
        self.assertEqual(len(p.cardsInHand), 3)
        self.assertEqual(list(map(lambda c: c.name, p.cardsInHand)), ['sawmill', 'brick_mill', 'steel_mill'])
        self.assertEqual(list(map(lambda c: c.name, pile)), ['cloister', 'spinning_mill', 'mill'])

        p.cardsInHand = []
        pile = [
            Building('cloister', Cost(), False, 0, 0),
            Action('arson'),
            Fleet('fleet_wood', Cost(), Resource.WOOD, 1),
            Knight('jose', Cost(brick=2), 1, 1),
            Action('scout')
        ]
        p.select_pile = MagicMock(return_value=pile)
        p.pick_starting_cards()
        self.assertEqual(len(p.cardsInHand), 3)
        self.assertEqual(list(map(lambda c: c.name, p.cardsInHand)), ['cloister', 'scout', 'fleet_wood'])
        self.assertEqual(list(map(lambda c: c.name, pile)), ['arson', 'jose'])

