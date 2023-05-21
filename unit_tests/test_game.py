import unittest, sys

from card import Action, Fleet, Knight, Building
from enums import Resource
from game import Game
from unittest.mock import MagicMock

from util import Cost

sys.modules[Game.__module__].DisplayHandler = MagicMock()

class TestStack(unittest.TestCase):
    def test_card_event_builder(self):
        game = Game()
        p1, p2 = game.player1, game.player2

        p1.cardsInHand.append(Action('bishop'))
        p2.cardsInHand.append(Action('arson'))

        pile1 = [
            Building('warehouse', Cost(), False, 0, 0),
            Knight('jose', Cost(), 1, 1)
        ]

        pile2 = [
            Fleet('fleet_wood', Cost(), Resource.WOOD, 1),
            Action('caravan')
        ]

        p1.select_pile = MagicMock(return_value=pile1)
        p1.select_card_from_choice = MagicMock(return_value=pile1[1])  # jose
        p1.select_card_to_throw_away = MagicMock(return_value=p1.cardsInHand[0])

        p2.select_pile = MagicMock(return_value=pile2)
        p2.select_card_from_choice = MagicMock(return_value=pile2[0])  # fleet_wood
        p2.select_card_to_throw_away = MagicMock(return_value=p2.cardsInHand[0])

        game.card_event_builder()

        self.assertEqual(len(p1.cardsInHand), 1)
        self.assertEqual(p1.cardsInHand[0].name, 'jose')
        self.assertEqual(list(map(lambda c: c.name, pile1)), ['warehouse', 'bishop'])

        self.assertEqual(len(p2.cardsInHand), 1)
        self.assertEqual(p2.cardsInHand[0].name, 'fleet_wood')
        self.assertEqual(list(map(lambda c: c.name, pile2)), ['caravan', 'arson'])

    def test_card_event_civil_war(self):
        game = Game()
        p1, p2 = game.player1, game.player2

        k = Knight('mike', Cost(), 1, 1)
        b = Building('mill', Cost(), False, 1, 1)
        p2.knightsPlayed.append(k)
        p1.buildingsPlayed.append(b)

        p1.has_unit_to_remove_in_civil_war = MagicMock(return_value=False)
        p2.has_unit_to_remove_in_civil_war = MagicMock(return_value=True)
        p1.select_opponents_unit_to_remove = MagicMock(return_value=k)
        p1.take_back_to_hand = MagicMock()
        p2.take_back_to_hand = MagicMock()

        game.card_event_civil_war()

        p1.take_back_to_hand.assert_called_once()
        p2.take_back_to_hand.assert_not_called()

        # TODO - interconnect properly and run deeper test
