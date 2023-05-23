import unittest, sys
from unittest.mock import MagicMock
from card import Action, Fleet, Knight, Building, Town, SettlementSlot
from enums import Resource
from util import Cost, Pos

sys.modules['display_handler'] = MagicMock()
from game import Game

sys.modules[Game.__module__].DisplayHandler = MagicMock()

class TestStack(unittest.TestCase):
    def test_card_event_builder(self):
        game = Game()
        p1, p2 = game.player1, game.player2
        sys.modules[Game.__module__].print = MagicMock()

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
        sys.modules[Game.__module__].print = print

    def test_card_event_civil_war(self):
        game = Game()
        p1, p2 = game.player1, game.player2
        sys.modules[Game.__module__].print = MagicMock()

        k = Knight('mike', Cost(), 1, 1)
        b = Building('mill', Cost(), False, 1, 1)
        p2.knightsPlayed.append(k)
        p1.buildingsPlayed.append(b)

        town = Town(Pos(2, 2), p1)
        town.cards.append(k)
        k.settlement, k.player, k.pos = town, p2, Pos(2, 2)

        p2.settlements.append(town)

        p1.has_unit_to_remove_in_civil_war = MagicMock(return_value=False)
        p2.has_unit_to_remove_in_civil_war = MagicMock(return_value=True)
        p1.select_opponents_unit_to_remove = MagicMock(return_value=k)

        game.card_event_civil_war()

        self.assertEqual(len(p1.cardsInHand), 0)
        self.assertEqual(len(p2.cardsInHand), 1)
        self.assertIsNone(k.player)
        self.assertIsNone(k.pos)
        self.assertIsNone(k.settlement)
        self.assertEqual(len(town.cards), 1)

        slot = town.cards[0]
        self.assertTrue(isinstance(slot, SettlementSlot))
        self.assertIs(slot.player, p2)
        self.assertEqual(slot.pos, Pos(2, 2))
        self.assertIs(slot.settlement, town)

        sys.modules[Game.__module__].print = print
