import unittest, sys
from unittest.mock import MagicMock
from card import Action, Fleet, Knight, Building, Town, SettlementSlot, Landscape, Village
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

    def test_get_land_neighbors(self):
        game = Game()
        game.player1.midPos = Pos(3, 2)
        land = Landscape('wood', Resource.WOOD, 1)
        land.pos, land.player = Pos(1, 1), game.player1
        game.mainBoard.set_square(land.pos, land)

        self.assertEqual(game.get_land_neighbors(land), [])

        card = Building('warehouse', Cost(), True, 1, 1)
        card.pos = Pos(0, 1)  # in
        game.mainBoard.set_square(card.pos, card)

        self.assertEqual(len(game.get_land_neighbors(land)), 1)
        self.assertEqual(game.get_land_neighbors(land)[0].name, 'warehouse')

        card = Building('mill', Cost(), True, 1, 1)
        card.pos = Pos(2, 0) # in
        game.mainBoard.set_square(card.pos, card)

        card = Building('church', Cost(), True, 1, 1)
        card.pos = Pos(2, 1) # in
        game.mainBoard.set_square(card.pos, card)

        card = Knight('konrad', Cost(), 1, 1)
        card.pos = Pos(0, 3) # out
        game.mainBoard.set_square(card.pos, card)

        card = Fleet('fleet_wood', Cost(), Resource.WOOD, 1)
        card.pos = Pos(2, 4) # out
        game.mainBoard.set_square(card.pos, card)

        self.assertEqual(len(game.get_land_neighbors(land)), 3)
        self.assertEqual(sorted(list(map(lambda x: x.name, game.get_land_neighbors(land)))), ['church', 'mill', 'warehouse'])

        land = Landscape('brick', Resource.BRICK, 1)
        land.pos, land.player = Pos(1, 3), game.player1

        self.assertEqual(len(game.get_land_neighbors(land)), 2)
        self.assertEqual(sorted(list(map(lambda x: x.name, game.get_land_neighbors(land)))), ['fleet_wood', 'konrad'])

    def test_protected_by_warehouse(self):
        game = Game()
        game.player1.midPos = Pos(3, 2)

        land = Landscape('wood', Resource.WOOD, 1)
        land.pos, land.player = Pos(1, 1), game.player1

        self.assertFalse(game.is_protected_by_warehouse(land))
        self.assertEqual(game.get_neighboring_warehouse_cnt(land), 0)

        card = Building('warehouse', Cost(), True, 1, 1)
        card.pos = Pos(0, 0)  # in
        game.mainBoard.set_square(card.pos, card)

        self.assertTrue(game.is_protected_by_warehouse(land))
        self.assertEqual(game.get_neighboring_warehouse_cnt(land), 1)

        card = Building('warehouse', Cost(), True, 1, 1)
        card.pos = Pos(2, 1)  # in
        game.mainBoard.set_square(card.pos, card)

        card = Building('warehouse', Cost(), True, 1, 1)
        card.pos = Pos(0, 2)  # out
        game.mainBoard.set_square(card.pos, card)

        self.assertTrue(game.is_protected_by_warehouse(land))
        self.assertEqual(game.get_neighboring_warehouse_cnt(land), 2)

    def test_land_yield(self):
        game = Game()
        p = game.player1

        p.landscapeCards = [
            Landscape('wood', Resource.WOOD, 1),
            Landscape('gold', Resource.GOLD, 2),
            Landscape('rock', Resource.ROCK, 3),
            Landscape('wood', Resource.WOOD, 1),
            Landscape('brick', Resource.BRICK, 1),
            Landscape('wood', Resource.WOOD, 1)
        ]

        for land, pos in zip(p.landscapeCards, [(1, 1), (3, 1), (5, 1), (1, 3), (3, 3), (5, 3)]):
            land.pos, land.player = Pos(*pos), p
            game.mainBoard.set_square(land.pos, land)

        b = Building('sawmill', Cost(), False, 0, 0)
        b.pos = Pos(2, 0)
        game.mainBoard.set_square(b.pos, b)

        b = Building('sawmill', Cost(), False, 0, 0)
        b.pos = Pos(4, 3)
        game.mainBoard.set_square(b.pos, b)

        self.assertEqual(list(map(lambda l: game.get_land_yield(l), p.landscapeCards)), [2, 1, 1, 1, 1, 2])

        game.land_yield(2)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [0, 1, 0, 0, 0, 0])
        game.land_yield(2)
        game.land_yield(2)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [0, 3, 0, 0, 0, 0])
        game.land_yield(2)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [0, 3, 0, 0, 0, 0])
        game.land_yield(1)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [2, 3, 0, 1, 1, 2])
        game.land_yield(1)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [3, 3, 0, 2, 2, 3])
        game.land_yield(4)
        self.assertEqual(list(map(lambda l: l.resourcesHeld, p.landscapeCards)), [3, 3, 0, 2, 2, 3])

    def test_remove_card_from_board(self):
        game = Game()

        village = Village(Pos(1, 2), game.player1)
        card = Building('mill', Cost(), False, 0, 0)
        card.pos, card.player, card.settlement = Pos(1, 1), game.player1, village
        village.cards.append(card)

        game.mainBoard.set_square(village.pos, village)
        game.mainBoard.set_square(card.pos, card)

        game.remove_card_from_board(card)
        self.assertEqual(len(village.cards), 1)
        self.assertTrue(isinstance(village.cards[0], SettlementSlot))
        self.assertIs(village.cards[0].settlement, village)
