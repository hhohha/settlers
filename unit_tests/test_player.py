import unittest, sys
from random import randint
from typing import Optional
from unittest.mock import MagicMock

import config
from board import Board
from card import Town, Village, Building, Landscape, Knight, Fleet, Action, SettlementSlot
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

    def test_setup_land_cards(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))

        self.assertEqual(len(p.initialLandPos), 6)

        p.setup_initial_land_card(Landscape('gold', Resource.GOLD, 1))
        p.setup_initial_land_card(Landscape('wood', Resource.WOOD, 2))
        p.setup_initial_land_card(Landscape('sheep', Resource.SHEEP, 3))
        p.setup_initial_land_card(Landscape('grain', Resource.GRAIN, 4))
        p.setup_initial_land_card(Landscape('rock', Resource.ROCK, 5))
        p.setup_initial_land_card(Landscape('brick', Resource.BRICK, 6))

        self.assertEqual(len(p.landscapeCards), 6)
        self.assertEqual(p.landscapeCards[0].name, 'gold')
        self.assertEqual(p.landscapeCards[0].pos, Pos(5, 3))

        self.assertEqual(p.landscapeCards[1].name, 'wood')
        self.assertEqual(p.landscapeCards[1].pos, Pos(5, 1))

        self.assertEqual(p.landscapeCards[2].name, 'sheep')
        self.assertEqual(p.landscapeCards[2].pos, Pos(9, 3))

        self.assertEqual(p.landscapeCards[3].name, 'grain')
        self.assertEqual(p.landscapeCards[3].pos, Pos(9, 1))

        self.assertEqual(p.landscapeCards[4].name, 'rock')
        self.assertEqual(p.landscapeCards[4].pos, Pos(7, 3))

        self.assertEqual(p.landscapeCards[5].name, 'brick')
        self.assertEqual(p.landscapeCards[5].pos, Pos(7, 1))

        self.assertEqual(len(p.initialLandPos), 0)

        with self.assertRaises(AssertionError):
            p.setup_initial_land_card(Landscape('brick', Resource.BRICK, 6))

    def test_card_in_hand(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertFalse(p.card_in_hand('warehouse'))

        p.cardsInHand.append(Building('warehouse', Cost(), False, 0, 0))
        self.assertTrue(p.card_in_hand('warehouse'))

        p.cardsInHand.append(Knight('gustav', Cost(), 0, 0))
        self.assertTrue(p.card_in_hand('warehouse'))
        self.assertTrue(p.card_in_hand('gustav'))
        self.assertFalse(p.card_in_hand('church'))

    def test_has_browse_discount(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertFalse(p.has_browse_discount())
        p.buildingsPlayed.append(Building('warehouse', Cost(), False, 0, 0))
        self.assertFalse(p.has_browse_discount())
        p.buildingsPlayed.append(Building('town_hall', Cost(), False, 0, 0))
        self.assertTrue(p.has_browse_discount())

    def test_get_tournament_strength(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertEqual(p.get_tournament_strength(), 0)

        p.knightsPlayed.append(Knight('gustav', Cost(), 2, 1))
        p.knightsPlayed.append(Knight('konrad', Cost(), 3, 2))
        p.knightsPlayed.append(Knight('leo', Cost(), 0, 1))
        self.assertEqual(p.get_tournament_strength(), 5)

    def test_get_trade_strength(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertEqual(p.get_trade_strength(), 0)

        p.fleetPlayed.append(Fleet('fleet1', Cost(), Resource.WOOD, 1))
        p.fleetPlayed.append(Fleet('fleet2', Cost(), Resource.BRICK, 1))
        p.buildingsPlayed.append(Building('buliding1', Cost(), True, 1, 1))
        p.buildingsPlayed.append(Building('buliding1', Cost(), False, 0, 3))
        self.assertEqual(p.get_trade_strength(), 6)

    def test_get_battle_strength(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        self.assertEqual(p.get_battle_strength(), 0)

        p.knightsPlayed.append(Knight('gareth', Cost(), 0, 1))
        p.knightsPlayed.append(Knight('lancelot', Cost(), 2, 5))
        p.knightsPlayed.append(Knight('kay', Cost(), 0, 0))

        self.assertEqual(p.get_battle_strength(), 6)

        p.buildingsPlayed.append(Building('smithy', Cost(), True, 1, 1))
        self.assertEqual(p.get_battle_strength(), 9)

        p.knightsPlayed = []
        self.assertEqual(p.get_battle_strength(), 0)

    def test_get_hand_cards_cnt(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(7, 2))
        defCnt = config.STARTING_HAND_CARD_CNT
        self.assertEqual(p.get_hand_cards_cnt(), defCnt)

        p.buildingsPlayed.append(Building('building1', Cost(), True, 0, 0))
        p.buildingsPlayed.append(Building('library', Cost(), True, 0, 0))
        p.buildingsPlayed.append(Building('building2', Cost(), True, 0, 0))
        p.buildingsPlayed.append(Building('cloister', Cost(), True, 0, 0))
        self.assertEqual(p.get_hand_cards_cnt(), defCnt + 2)

    def test_place_new_land_no_scout(self):
        gameMock = MagicMock()
        gameMock.landscapeCards = [
            Landscape('brick', Resource.BRICK, 3),
            Landscape('sheep', Resource.SHEEP, 4),
            Landscape('rock', Resource.ROCK, 1),
            Landscape('gold', Resource.GOLD, 2),
        ]
        gameMock.mainBoard = Board(Pos(5, 5), Pos(50, 50))
        p = Player(gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        p.place_new_land(Pos(3, 2))

        land = p.game.mainBoard.get_square(Pos(4, 1))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'gold')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(4, 1))

        land = p.game.mainBoard.get_square(Pos(4, 3))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'rock')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(4, 3))

        self.assertEqual(len(p.game.landscapeCards), 2)
        self.assertEqual(len(p.landscapeCards), 2)
        self.assertEqual(p.landscapeCards[0].name, 'gold')
        self.assertEqual(p.landscapeCards[1].name, 'rock')

        p.place_new_land(Pos(1, 2))

        land = p.game.mainBoard.get_square(Pos(0, 1))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'sheep')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(0, 1))

        land = p.game.mainBoard.get_square(Pos(0, 3))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'brick')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(0, 3))

        self.assertEqual(len(p.game.landscapeCards), 0)
        self.assertEqual(len(p.landscapeCards), 4)
        self.assertEqual(p.landscapeCards[2].name, 'sheep')
        self.assertEqual(p.landscapeCards[3].name, 'brick')

    def test_place_new_land_with_scout(self):
        gameMock = MagicMock()
        gameMock.landscapeCards = [
            Landscape('brick', Resource.BRICK, 3),
            Landscape('sheep', Resource.SHEEP, 4),
            Landscape('rock', Resource.ROCK, 1),
            Landscape('gold', Resource.GOLD, 2),
        ]
        gameMock.mainBoard = Board(Pos(5, 5), Pos(50, 50))
        p = Player(gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        p.cardsInHand.append(Action('scout'))
        p.decide_use_scout = MagicMock(return_value=True)
        p.select_new_land = MagicMock(side_effect=[gameMock.landscapeCards[2], gameMock.landscapeCards[1]])

        p.place_new_land(Pos(1, 2))

        land = p.game.mainBoard.get_square(Pos(0, 1))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'rock')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(0, 1))

        land = p.game.mainBoard.get_square(Pos(0, 3))
        self.assertIsNotNone(land)
        self.assertTrue(isinstance(land, Landscape) and land.name == 'sheep')
        self.assertIs(land.player, p)
        self.assertEqual(land.pos, Pos(0, 3))

        self.assertEqual(len(p.game.landscapeCards), 2)
        self.assertEqual(len(p.landscapeCards), 2)
        self.assertEqual(p.landscapeCards[0].name, 'rock')
        self.assertEqual(p.landscapeCards[1].name, 'sheep')

    def test_spy_can_steal(self):
        # conveniently, opponent == self - testing stealing from self
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        self.assertFalse(p.spy_can_steal_card())

        p.cardsInHand.append(Building('b1', Cost(), True, 0, 0))
        p.cardsInHand.append(Building('b2', Cost(), True, 0, 0))
        self.assertFalse(p.spy_can_steal_card())

        p.cardsInHand.append(Fleet('f1', Cost(), Resource.ROCK, 1))
        p.cardsInHand.append(Building('b3', Cost(), True, 0, 0))
        self.assertTrue(p.spy_can_steal_card())

    def test_get_advance_resource_cnt(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        self.assertEqual(p.get_advance_resource_cnt(), 0)

        p.buildingsPlayed.append(Building('town_hall', Cost(), True, 1, 1))
        p.buildingsPlayed.append(Building('mill', Cost(), True, 1, 1))
        self.assertEqual(p.get_advance_resource_cnt(), 0)

        p.buildingsPlayed.append(Building('library', Cost(), True, 1, 1))
        p.buildingsPlayed.append(Building('warehouse', Cost(), True, 1, 1))
        p.buildingsPlayed.append(Building('cloister', Cost(), True, 1, 1))
        self.assertEqual(p.get_advance_resource_cnt(), 2)


    def test_remove_action_card(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        with self.assertRaises(AssertionError):
            p.remove_action_card('bishop')

        p.cardsInHand = [
            Action('bishop'),
            Building('b1', Cost(), False, 1, 1),
            Action('ambush')
        ]

        p.remove_action_card('ambush')
        self.assertEqual(len(p.cardsInHand), 2)
        self.assertEqual(p.cardsInHand[0].name, 'bishop')
        self.assertEqual(p.cardsInHand[1].name, 'b1')

    def test_take_back_to_hand(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        building = Building('b1', Cost(), True, 1, 1)
        village = Village(Pos(2, 2), p)
        village.cards.append(building)
        building.pos, building.player, building.settlement = Pos(3, 2), p, village
        p.buildingsPlayed.append(building)

        p.take_back_to_hand(building)
        self.assertIsNone(building.player)
        self.assertIsNone(building.pos)
        self.assertIsNone(building.settlement)
        self.assertEqual(len(p.cardsInHand), 1)
        self.assertEqual(p.cardsInHand[0].name, 'b1')
        self.assertEqual(len(p.buildingsPlayed), 0)
        self.assertEqual(len(village.cards), 1)
        self.assertTrue(isinstance(village.cards[0], SettlementSlot))
        self.assertEqual(village.cards[0].pos, Pos(3, 2))
        self.assertIs(village.cards[0].player, p)
        self.assertIs(village.cards[0].settlement, village)

    def test_action_card_get_toss_winner(self):
        p1 = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        p2 = Player(self.gameMock, self.handBoardMock, 2, False, Pos(2, 2))
        p1.opponent, p2.opponent = p2, p1

        p1.opponent.use_defence = MagicMock(return_value=False)
        p1.opponent.remove_action_card = MagicMock()
        p1.wait_for_ok = MagicMock()
        sys.modules[Player.__module__].print = MagicMock()

        with self.assertRaises(AssertionError):
            p1.action_card_get_toss_winner('bad_name')

        for i in range(1, 6):
            sys.modules[Player.__module__].randint = MagicMock(return_value=i)
            winner = p1.action_card_get_toss_winner('ambush')
            self.assertIs(winner, p1 if i <= 5 else p2)

        p1.opponent.use_defence = MagicMock(return_value=True)
        for i in range(1, 6):
            sys.modules[Player.__module__].randint = MagicMock(return_value=i)
            winner = p1.action_card_get_toss_winner('black_knight')
            self.assertIs(winner, p1 if i <= 2 else p2)

        sys.modules[Player.__module__].print = print

    def test_play_spy(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        p.wait_for_ok = MagicMock()
        p.opponent = MagicMock()
        p.opponent.cardsInHand = [
            Knight('knight1', Cost(), 2, 3),
            Fleet('fleet1', Cost(), Resource.ROCK, 1),
            Action('bishop')
        ]
        p.select_card_to_steal_by_spy = MagicMock(return_value=p.opponent.cardsInHand[2])

        p.play_action_card_spy()
        self.assertEqual(len(p.opponent.cardsInHand), 2)
        self.assertEqual(len(p.cardsInHand), 1)
        self.assertTrue(isinstance(p.cardsInHand[0], Action))

        p.opponent.cardsInHand = [
            Building('b1', Cost(), True, 2, 3),
            Building('b2', Cost(), False, 1, 1)
        ]
        p.play_action_card_spy()
        self.assertEqual(len(p.opponent.cardsInHand), 2)
        self.assertEqual(len(p.cardsInHand), 1)

    def init_players(self):
        player1 = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        player2 = Player(self.gameMock, self.handBoardMock, 2, False, Pos(2, 2))
        player1.opponent, player2.opponent = player2, player1
        player1.wait_for_ok = MagicMock()
        player2.wait_for_ok = MagicMock()
        return player1, player2

    def test_play_arson(self):
        b = Building('building1', Cost(), True, 1, 1)

        # 1. I win and cannot burn anything
        p1, p2 = self.init_players()
        p1.buildingsPlayed.append(b)
        p1.action_card_get_toss_winner = MagicMock(return_value=p1)

        p1.play_action_card_arson()
        self.assertTrue(p1.wait_for_ok.called)

        # 2. i win and i can burn something
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p1)
        p2.buildingsPlayed.append(b)
        p1.select_building_to_burn = MagicMock(return_value=b)
        p2.take_back_to_hand = MagicMock()

        p1.play_action_card_arson()
        self.assertTrue(p2.take_back_to_hand.called)

        # 3. i lose and have nothing to burn
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p2)
        p2.buildingsPlayed.append(b)

        p1.play_action_card_arson()
        self.assertTrue(p1.wait_for_ok.called)

        # 4. i lose and cannot have something to be burnt
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p2)
        p1.buildingsPlayed.append(b)
        p2.select_building_to_burn = MagicMock(return_value=b)
        p1.take_back_to_hand = MagicMock()

        p1.play_action_card_arson()
        self.assertTrue(p1.take_back_to_hand.called)

    def test_play_black_knight(self):
        k = Knight('building1', Cost(), 2, 3)

        # 1. I win and cannot kill anyone
        p1, p2 = self.init_players()
        p1.knightsPlayed.append(k)
        p1.action_card_get_toss_winner = MagicMock(return_value=p1)

        p1.play_action_card_black_knight()
        self.assertTrue(p1.wait_for_ok.called)

        # 2. i win and i can kill someone
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p1)
        p2.knightsPlayed.append(k)
        p1.select_knight_to_kill = MagicMock(return_value=k)
        p2.take_back_to_hand = MagicMock()

        p1.play_action_card_black_knight()
        self.assertTrue(p2.take_back_to_hand.called)

        # 3. i lose and have nothing to burn
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p2)
        p2.knightsPlayed.append(k)

        p1.play_action_card_black_knight()
        self.assertTrue(p1.wait_for_ok.called)

        # 4. i lose and cannot have something to be burnt
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p2)
        p1.knightsPlayed.append(k)
        p2.select_knight_to_kill = MagicMock(return_value=k)
        p1.take_back_to_hand = MagicMock()

        p1.play_action_card_black_knight()
        self.assertTrue(p1.take_back_to_hand.called)

    def test_play_ambush(self):
        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p1)
        p1.grab_any_resource_if_possible = MagicMock()

        p1.play_action_card_ambush()
        self.assertEqual(len(p1.grab_any_resource_if_possible.mock_calls), 2)

        p1, p2 = self.init_players()
        p1.action_card_get_toss_winner = MagicMock(return_value=p2)
        p2.grab_any_resource_if_possible = MagicMock()

        p1.play_action_card_ambush()
        self.assertEqual(len(p2.grab_any_resource_if_possible.mock_calls), 2)

    def test_play_trader(self):
        p1, p2 = self.init_players()
        p1.grab_any_resource_if_possible = MagicMock()
        p1.give_any_resource = MagicMock()

        p1.play_action_card_trader()
        self.assertEqual(len(p1.grab_any_resource_if_possible.mock_calls), 2)
        self.assertEqual(len(p1.give_any_resource.mock_calls), 1)

    def test_play_caravan(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        p.wait_for_ok = MagicMock()
        p.trade_with_caravan = MagicMock()

        p.play_action_card_caravan()
        p.wait_for_ok.assert_called_once()
        p.trade_with_caravan.assert_not_called()

        p.wait_for_ok.reset_mock()
        p.landscapeCards.append(Landscape('wood', Resource.WOOD, 1))
        p.landscapeCards[0].resourcesHeld = 1

        p.play_action_card_caravan()
        p.wait_for_ok.assert_not_called()
        self.assertEqual(len(p.trade_with_caravan.mock_calls), 2)

    def test_play_card_from_hand(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        # create a settlement, slot and interconnect them
        slot = SettlementSlot(Pos(1, 1), p)
        settlement = Village(Pos(3, 3), p)
        slot.settlement = settlement
        settlement.cards.append(slot)

        p.pay = MagicMock()
        p.refresh_hand_board = MagicMock()
        p.can_cover_cost = MagicMock(return_value=True)
        p.game.mainBoard.get_square = MagicMock(return_value=slot)

        card = Building('mill', Cost(wood=1), False, 1, 1)
        p.cardsInHand.append(card)

        p.play_card_from_hand(card, Pos(1, 1))

        self.assertEqual(len(p.cardsInHand), 0)
        self.assertEqual(len(p.buildingsPlayed), 1)
        self.assertEqual(p.buildingsPlayed[0].name, 'mill')
        self.assertEqual(card.pos, Pos(1, 1))
        self.assertIs(card.settlement, settlement)
        self.assertIs(card.player, p)
        self.assertEqual(len(settlement.cards), 1)
        self.assertEqual(settlement.cards[0].name, 'mill')

        slot2 = SettlementSlot(Pos(1, 0), p)
        slot2.settlement = settlement
        settlement.cards.append(slot2)

        p.game.mainBoard.get_square = MagicMock(return_value=slot2)

        card = Knight('rambo', Cost(), 1, 1)
        p.cardsInHand.append(card)

        p.select_new_card_position = MagicMock(return_value=Pos(1, 3))
        p.play_card_from_hand(card)

        self.assertEqual(len(p.cardsInHand), 0)
        self.assertEqual(len(p.buildingsPlayed), 1)
        self.assertEqual(len(p.knightsPlayed), 1)
        self.assertEqual(p.knightsPlayed[0].name, 'rambo')
        self.assertEqual(card.pos, Pos(1, 3))
        self.assertIs(card.settlement, settlement)
        self.assertIs(card.player, p)
        self.assertEqual(len(settlement.cards), 2)
        self.assertEqual(settlement.cards[1].name, 'rambo')

    def test_lose_ambush_resources(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        p.lose_ambush_resources()
        self.assertEqual(p.get_resources_available(), Cost())

        p.landscapeCards = [
            Landscape('wood', Resource.WOOD, 1),
            Landscape('sheep', Resource.SHEEP, 2),
            Landscape('grain', Resource.GRAIN, 3),
            Landscape('rock', Resource.ROCK, 4),
            Landscape('sheep', Resource.SHEEP, 5)
        ]
        p.landscapeCards[0].resourcesHeld = 0
        p.landscapeCards[1].resourcesHeld = 2
        p.landscapeCards[2].resourcesHeld = 3
        p.landscapeCards[3].resourcesHeld = 3
        p.landscapeCards[4].resourcesHeld = 1

        p.landscapeCards[0].pos = Pos(0, 0)
        p.landscapeCards[1].pos = Pos(0, 0)
        p.landscapeCards[2].pos = Pos(0, 0)
        p.landscapeCards[3].pos = Pos(0, 0)
        p.landscapeCards[4].pos = Pos(0, 0)


        p.lose_ambush_resources()
        self.assertEqual(p.get_resources_available(), Cost(grain=3))

    def test_get_resource_cost(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))

        self.assertEqual(p.get_resource_cost(Resource.WOOD), 3)
        self.assertEqual(p.get_resource_cost(Resource.GOLD), 3)

        p.buildingsPlayed.append(Building('mill', Cost(), True, 1, 0))
        self.assertEqual(p.get_resource_cost(Resource.GOLD), 3)

        p.buildingsPlayed.append(Building('mint', Cost(), True, 1, 0))
        self.assertEqual(p.get_resource_cost(Resource.GOLD), 1)

        p.fleetPlayed.append(Fleet('fleet_brick', Cost(), Resource.BRICK, 0))
        self.assertEqual(p.get_resource_cost(Resource.WOOD), 3)
        self.assertEqual(p.get_resource_cost(Resource.BRICK), 2)

    def test_trade(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        sys.modules[Player.__module__].print = MagicMock()

        land = Landscape('sheep', Resource.SHEEP, 1)
        land.pos = Pos(1, 1)
        p.landscapeCards.append(land)

        p.buildingsPlayed.append(Building('mint', Cost(), True, 1, 0))
        p.select_resource_to_trade_for = MagicMock(return_value=Resource.GOLD)
        p.can_cover_cost = MagicMock(return_value=True)
        p.pay = MagicMock
        p.select_resource_to_purchase = MagicMock(return_value=land)

        p.trade()
        self.assertEqual(p.get_resources_available(), Cost(sheep=1))
        sys.modules[Player.__module__].print = print

    def give_resource(self, player: Player, cost: Cost):
        def find_land(p: Player, res: Resource) -> Optional[Landscape]:
            for l in p.landscapeCards:
                if l.resource == res and l.resourcesHeld < 3:
                    return l

        while not cost.is_zero():
            for resource in Resource:
                if cost.get(resource) > 0:
                    cost.take(resource)
                    land = find_land(player, resource)
                    if land is not None:
                        land.resourcesHeld += 1
                    else:
                        player.landscapeCards.append(Landscape(resource.value, resource, randint(1, 6)))
                        player.landscapeCards[-1].resourcesHeld = 1

    def test_can_grab_resource(self):
        p1, p2 = self.init_players()

        self.assertFalse(p1.can_grab_resource_from_opponent())

        p1.landscapeCards = [
            Landscape('wood', Resource.WOOD, 1),
            Landscape('gold', Resource.GOLD, 2),
            Landscape('rock', Resource.ROCK, 3),
            Landscape('sheep', Resource.SHEEP, 4),
            Landscape('brick', Resource.BRICK, 5),
            Landscape('grain', Resource.GRAIN, 6)
        ]
        p2.landscapeCards = [
            Landscape('wood', Resource.WOOD, 1),
            Landscape('gold', Resource.GOLD, 2),
            Landscape('rock', Resource.ROCK, 3),
            Landscape('sheep', Resource.SHEEP, 4),
            Landscape('brick', Resource.BRICK, 5),
            Landscape('grain', Resource.GRAIN, 6)
        ]
        self.assertFalse(p1.can_grab_resource_from_opponent())

        self.give_resource(p1, Cost(grain=1))
        self.assertFalse(p1.can_grab_resource_from_opponent())

        self.give_resource(p2, Cost(grain=1))
        self.give_resource(p1, Cost(grain=2))
        self.assertFalse(p1.can_grab_resource_from_opponent())

        self.give_resource(p2, Cost(wood=1))
        self.give_resource(p2, Cost(wood=1))
        self.assertTrue(p1.can_grab_resource_from_opponent())

    def test_place_village_and_town(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        p.place_village_to_board(Pos(2, 3))

        self.assertEqual(len(p.settlements), 1)
        newSettlement = p.settlements[0]
        self.assertEqual(newSettlement.name, 'village')
        self.assertEqual(len(newSettlement.cards) ,2)
        for i in range(2):
            slot = newSettlement.cards[i]
            self.assertTrue(isinstance(slot, SettlementSlot))
            self.assertIs(slot.settlement, newSettlement)

        p.game.mainBoard.get_square = MagicMock(return_value=newSettlement)

        p.place_town_to_board(Pos(2, 2))
        self.assertTrue(isinstance(newSettlement, Town))
        self.assertEqual(newSettlement.name, 'town')
        self.assertEqual(len(newSettlement.cards), 4)

        for i in range(4):
            slot = newSettlement.cards[i]
            self.assertTrue(isinstance(slot, SettlementSlot))
            self.assertIs(slot.settlement, newSettlement)

    def test_refill_hand_take_card(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        pile = [
            Building('warehouse', Cost(), True, 1, 1),
            Action('bishop'),
            Knight('gustav', Cost(), 1, 1),
        ]

        p.refill_hand_take_card(pile)
        self.assertEqual(len(pile), 2)
        self.assertEqual(len(p.cardsInHand), 1)
        self.assertEqual(p.cardsInHand[0].name, 'warehouse')

        p.can_cover_cost = MagicMock(return_value=True)
        p.decide_browse_pile = MagicMock(return_value=True)
        p.pay = MagicMock()
        p.select_card_from_choice = MagicMock(return_value=pile[1])

        p.refill_hand_take_card(pile)
        self.assertEqual(len(pile), 1)
        self.assertEqual(len(p.cardsInHand), 2)
        self.assertEqual(p.cardsInHand[0].name, 'warehouse')
        self.assertEqual(p.cardsInHand[1].name, 'gustav')

    def test_refill_hand_remove_card(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        pile = [Action('witch')]

        p.cardsInHand = [
            Building('warehouse', Cost(), True, 1, 1),
            Action('bishop'),
            Knight('gustav', Cost(), 1, 1),
        ]

        p.select_card_to_throw_away = MagicMock(return_value=p.cardsInHand[1])
        p.refill_hand_remove_card(pile)

        self.assertEqual(len(pile), 2)
        self.assertEqual(pile[1].name, 'bishop')
        self.assertEqual(len(p.cardsInHand), 2)
        self.assertEqual(p.cardsInHand[0].name, 'warehouse')
        self.assertEqual(p.cardsInHand[1].name, 'gustav')

    def test_refill_hand(self):
        p = Player(self.gameMock, self.handBoardMock, 1, False, Pos(2, 2))
        pile = [
            Building('warehouse', Cost(), True, 1, 1),
            Action('bishop'),
            Knight('gustav', Cost(), 1, 1),
        ]
        p.select_pile = MagicMock(return_value=pile)

        p.refill_hand()
        # hand: [warehouse, bishop, gustav]
        # pile: []
        self.assertEqual(len(pile), 0)
        self.assertEqual(len(p.cardsInHand), 3)
        self.assertEqual(list(map(lambda x: x.name, p.cardsInHand)), ['warehouse', 'bishop', 'gustav'])

        pile2 = [
            Building('church', Cost(), True, 1, 1),
            Action('arson'),
            Knight('konrad', Cost(), 1, 1),
        ]

        p.select_pile = MagicMock(return_value=pile2)
        p.get_hand_cards_cnt = MagicMock(return_value=5)
        p.refill_hand()
        # hand: [warehouse, bishop, gustav, church, arson]
        # pile: [konrad]

        self.assertEqual(len(pile2), 1)
        self.assertEqual(len(p.cardsInHand), 5)
        self.assertEqual(list(map(lambda x: x.name, p.cardsInHand)), ['warehouse', 'bishop', 'gustav', 'church', 'arson'])
        self.assertEqual(list(map(lambda x: x.name, pile2)), ['konrad'])


        p.get_hand_cards_cnt = MagicMock(return_value=4)
        p.decide_swap_one_card = MagicMock(return_value=False)
        p.select_card_to_throw_away = MagicMock(return_value=p.cardsInHand[2])  # gustav
        p.refill_hand()
        # hand: [warehouse, bishop, church, arson]
        # pile: [konrad, gustav]

        self.assertEqual(len(pile2), 2)
        self.assertEqual(len(p.cardsInHand), 4)
        self.assertEqual(list(map(lambda x: x.name, p.cardsInHand)), ['warehouse', 'bishop', 'church', 'arson'])
        self.assertEqual(list(map(lambda x: x.name, pile2)), ['konrad', 'gustav'])

        p.decide_swap_one_card = MagicMock(return_value=True)
        p.select_card_to_throw_away = MagicMock(return_value=p.cardsInHand[1])  # bishop
        p.select_card_from_choice = MagicMock(return_value=pile2[1])            # gustav
        p.can_cover_cost = MagicMock(return_value=True)
        p.decide_browse_pile = MagicMock(return_value=True)
        p.pay = MagicMock()

        p.refill_hand()
        # hand: [warehouse, church, arson, gustav]
        # pile: [konrad, bishop]
        self.assertEqual(len(p.cardsInHand), 4)
        self.assertEqual(len(pile2), 2)
        self.assertEqual(list(map(lambda x: x.name, p.cardsInHand)), ['warehouse', 'church', 'arson', 'gustav'])
        self.assertEqual(list(map(lambda x: x.name, pile2)), ['konrad', 'bishop'])