from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from random import randint
from typing import TYPE_CHECKING, List, Dict, Optional, Type, Set

import config
from card import Action, Buildable, Building, Playable, SettlementSlot, Village, Town, Path, Knight, Fleet, Settlement
from config import BROWSE_DISCOUNT_BUILDINGS, CARDS_INCREASING_HAND_CNT, STOLEN_AMBUSH_RESOURCES, ADVANCE_BUILDINGS, \
    MAX_LAND_RESOURCES
from enums import Resource
from util import Pos, Cost, DEFENCE_CARDS

if TYPE_CHECKING:
    from card import Landscape
    from game import Game, Pile
    from board import Board

class Player(ABC):
    def __init__(self, game: Game, handBoard: Board, number: int, cardsVisible: bool, midPos: Pos):
        self.game: Game = game
        self.opponent: Player = self
        self.handBoard = handBoard
        self.number: int = number
        self.victoryPoints = 0
        self.cardsInHandDefaultCnt: int = config.STARTING_HAND_CARD_CNT
        self.cardsInHand: List[Playable] = []
        self.landscapeCards: List[Landscape] = []
        self.knightsPlayed: List[Knight] = []
        self.fleetPlayed:  List[Fleet] = []
        self.buildingsPlayed: List[Building] = []
        self.settlements: List[Settlement] = []
        self.paths: List[Path] = []
        self.cardsVisible: bool = cardsVisible
        self.midPos: Pos = midPos
        self.initialLandPos: List[Pos] = [
            self.midPos.up(),
            self.midPos.down(),
            self.midPos.up().right(2),
            self.midPos.down().right(2),
            self.midPos.up().left(2),
            self.midPos.down().left(2)
        ]
    ####################################################################################################################
    #################   CALCULATING FUNCTIONS   ########################################################################
    ####################################################################################################################

    def get_victory_points(self) -> int:
        points: int = 0
        points += sum(map(lambda s: 2 if isinstance(s, Town) else 1, self.settlements))
        points += sum(map(lambda b: b.victoryPoints, self.buildingsPlayed))
        if self.get_trade_strength() > self.opponent.get_trade_strength():
            points += 1
        if self.get_battle_strength() > self.opponent.get_battle_strength():
            points += 1

        return points

    def get_resources_available(self) -> Cost:
        resources: Dict[Resource, int] = {
            Resource.BRICK: 0,
            Resource.WOOD: 0,
            Resource.ROCK: 0,
            Resource.GRAIN: 0,
            Resource.GOLD: 0,
            Resource.SHEEP: 0
        }

        for land in self.landscapeCards:
            resources[land.resource] += land.resourcesHeld

        return Cost(brick=resources[Resource.BRICK], wood=resources[Resource.WOOD], rock=resources[Resource.ROCK],
                    grain=resources[Resource.GRAIN], gold=resources[Resource.GOLD], sheep=resources[Resource.SHEEP])

    def can_cover_cost(self, cost: Cost | int) -> bool:
        if isinstance(cost, Cost):
            return self.get_resources_available() >= cost
        else:
            return self.get_resources_available().total() >= cost

    def card_in_hand(self, name: str) -> bool:
        return name in map(lambda n: n.name, self.cardsInHand)

    def has_browse_discount(self) -> bool:
        for cardName in BROWSE_DISCOUNT_BUILDINGS:
            if cardName in map(lambda b: b.name, self.buildingsPlayed):
                return True
        return False

    def get_tournament_strength(self) -> int:
        return sum(map(lambda k: k.tournamentStrength, self.knightsPlayed))

    def get_trade_strength(self) -> int:
        return sum(map(lambda b: b.tradePoints, self.buildingsPlayed)) + sum(map(lambda f: f.tradePoints, self.fleetPlayed))

    def get_battle_strength(self) -> int:
        strength = sum(map(lambda k: k.battleStrength, self.knightsPlayed))
        if 'smithy' in map(lambda b: b.name, self.buildingsPlayed):
            strength += len(self.knightsPlayed)
        return strength

    def get_hand_cards_cnt(self) -> int:
        return self.cardsInHandDefaultCnt + len([True for b in self.buildingsPlayed if b.name in CARDS_INCREASING_HAND_CNT])

    def spy_can_steal_card(self) -> bool:
        return any(map(lambda x: isinstance(x, (Fleet, Knight, Action)), self.opponent.cardsInHand))

    def get_advance_resource_cnt(self) -> int:
        return sum(map(lambda b: 1 if b.name in ADVANCE_BUILDINGS else 0, self.buildingsPlayed))

    def has_global_plaque_protection(self) -> bool:
        return 'aquaduct' in map(lambda b: b.name, self.buildingsPlayed)

    def get_unprotected_resources_cnt(self) -> int:
        return sum(map(lambda l: 0 if self.game.is_protected_by_warehouse(l) else l.resourcesHeld, self.landscapeCards))

    def get_resource_cost(self, resource: Resource) -> int:
        if resource == Resource.GOLD:
            return 1 if 'mint' in map(lambda b: b.name, self.buildingsPlayed) else 3

        return 2 if resource in map(lambda f: f.affectedResource, self.fleetPlayed) else 3

    def can_grab_resource_from_opponent(self) -> bool:
        resourcesCanReceive: Set[Resource] = set()
        resourcesCanGive: Set[Resource] = set()

        for land in self.landscapeCards:
            if land.resourcesHeld < MAX_LAND_RESOURCES:
                resourcesCanReceive.add(land.resource)

        for land in self.opponent.landscapeCards:
            if land.resourcesHeld > 0:
                resourcesCanGive.add(land.resource)

        return bool(resourcesCanReceive.intersection(resourcesCanGive))

    ####################################################################################################################
    #################   CARD PLACEMENT         #########################################################################
    ####################################################################################################################

    def setup_initial_land_card(self, card: Landscape) -> None:
        assert self.initialLandPos, 'cannot setup any more land'
        card.pos = self.initialLandPos.pop()
        self.landscapeCards.append(card)
        self.game.mainBoard.set_square(card.pos, card)

    def place_new_land(self, villagePos: Pos) -> None:
        assert villagePos.y == self.midPos.y and villagePos.x != self.midPos.x, 'invalid village position'
        scoutUse: bool = 'scout' in map(lambda x: x.name, self.cardsInHand) and self.decide_use_scout()

        if villagePos.x > self.midPos.x:
            landPositions = villagePos.up().right(), villagePos.down().right()
        else:
            landPositions = villagePos.up().left(), villagePos.down().left()

        for pos in landPositions:
            if scoutUse:
                newLand = self.select_new_land()
                self.game.landscapeCards.remove(newLand)
            else:
                newLand = self.game.landscapeCards.pop()
            self.game.mainBoard.set_square(pos, newLand)
            newLand.player = self
            self.landscapeCards.append(newLand)
            newLand.pos = pos

    def play_card_from_hand(self, card: Playable, pos: Optional[Pos]=None) -> None:
        if isinstance(card, Action):
            self.play_action_card(card)
            return

        assert isinstance(card, Buildable)

        if not self.can_cover_cost(card.cost):
            print('you cannot afford to play this')
            return

        townOnly: bool = card.townOnly if isinstance(card, Building) else False

        if pos is None:
            pos = self.select_new_card_position(Buildable, townOnly)
        if pos is None:
            return

        slot = self.game.mainBoard.get_square(pos)
        assert isinstance(slot, SettlementSlot), f'cannot place card to {pos}, slot is not valid'
        assert slot.settlement is not None

        card.settlement = slot.settlement
        card.settlement.cards.remove(slot)
        card.settlement.cards.append(card)
        self.game.mainBoard.set_square(pos, card)
        card.pos, card.player = pos, self

        if isinstance(card, Building):
            self.buildingsPlayed.append(card)
        elif isinstance(card, Knight):
            self.knightsPlayed.append(card)
        elif isinstance(card, Fleet):
            self.fleetPlayed.append(card)

        self.cardsInHand.remove(card)
        self.refresh_hand_board()
        self.pay(card.cost)

    def refresh_hand_board(self) -> None:
        self.game.display_cards_on_board(self.cardsInHand, self.handBoard)

    def build_infrastructure(self, infraType: Type[Town | Village | Path]) -> None:
        if self.game.infraCardsLeft[infraType] < 1:
            print(f'no more cards {infraType} left')
            return
        if not self.can_cover_cost(infraType.cost):
            print(f'you cannot afford this: {infraType}')
            return

        pos: Optional[Pos] = self.select_new_card_position(infraType)
        if pos is None:
            return

        self.game.infraCardsLeft[infraType] -= 1
        self.pay(infraType.cost)

        if infraType is Village:
            self.place_village_to_board(pos)
            self.place_new_land(pos)
        elif infraType is Town:
            self.place_town_to_board(pos)
        elif infraType is Path:
            path = Path(pos, self)
            self.paths.append(path)
            self.game.mainBoard.set_square(pos, path)
        else:
            assert False, f'build infrastructure got bad infratype: {infraType}'

    def place_town_to_board(self, pos: Pos) -> None:
        settlement = self.game.mainBoard.get_square(pos)
        assert isinstance(settlement, Village), f'cannot place town at {pos}'

        # type checking does not like class swap -> explicitly ignoring
        settlement.__class__ = Town  # type: ignore
        settlement.name = 'town'

        for p in [pos.up(2), pos.down(2)]:
            slot = SettlementSlot(p, self)
            self.game.mainBoard.set_square(p, slot)
            slot.settlement = settlement
            settlement.cards.append(slot)

        self.game.mainBoard.refresh_square(pos)

    def place_village_to_board(self, pos: Pos) -> None:
        newVillage = Village(pos, self)
        self.game.mainBoard.set_square(pos, newVillage)
        self.settlements.append(newVillage)

        for p in [pos.up(), pos.down()]:
            slot = SettlementSlot(p, self)
            self.game.mainBoard.set_square(p, slot)
            slot.settlement = newVillage
            newVillage.cards.append(slot)

    ####################################################################################################################
    #################   ACTION CARDS           #########################################################################
    ####################################################################################################################

    def play_action_card_spy(self) -> None:
        self.game.display_cards_on_board(self.opponent.cardsInHand, self.game.choiceBoard)
        if not self.spy_can_steal_card():
            self.game.display.print_msg('opponent has no unit to steal')
            self.wait_for_ok()
            return

        card = self.select_card_to_steal_by_spy()
        self.opponent.cardsInHand.remove(card)
        self.cardsInHand.append(card)
        self.refresh_hand_board()
        self.opponent.refresh_hand_board()

    def play_action_card_arson(self) -> None:
        winner = self.action_card_get_toss_winner('arson')
        if not winner.opponent.buildingsPlayed:
            self.game.display.print_msg(f'cannot burn anything')
            self.wait_for_ok()
            return

        burntBuilding: Building = winner.select_building_to_burn()
        winner.opponent.take_back_to_hand(burntBuilding)

    def play_action_card_black_knight(self) -> None:
        winner = self.action_card_get_toss_winner('black_knight')
        if not winner.opponent.knightsPlayed:
            self.game.display.print_msg('black knight cannot kill anyone')
            self.wait_for_ok()
            return

        killedKnight: Knight = winner.select_knight_to_kill()
        winner.opponent.take_back_to_hand(killedKnight)

    def play_action_card_ambush(self) -> None:
        winner = self.action_card_get_toss_winner('ambush')
        for _ in range(2):
            winner.grab_any_resource_if_possible()

    def play_action_card_trader(self) -> None:
        for _ in range(2):
            self.grab_any_resource_if_possible()

        self.give_any_resource()

    def remove_action_card(self, cardName: str) -> None:
        for card in self.cardsInHand:
            if isinstance(card, Action) and card.name == cardName:
                self.cardsInHand.remove(card)
                return
        assert False, f'player does not have action card {cardName}'

    def play_action_card_caravan(self) -> None:
        if sum(map(lambda c: c.resourcesHeld, self.landscapeCards)) == 0:
            self.game.display.print_msg('nothing to trade for')
            self.wait_for_ok()
            return

        for _ in range(2):
            self.trade_with_caravan()

    def play_action_card(self, card: Action) -> None:
        # following action cards can be played only at certain specific situation (not here):
        # alchemist, bishop, witch, scout

        if card.name == 'spy':
            self.play_action_card_spy()
        elif card.name == 'arson':
            self.play_action_card_arson()
        elif card.name == 'ambush':
            self.play_action_card_ambush()
        elif card.name == 'trader':
            self.play_action_card_trader()
        elif card.name == 'caravan':
            self.play_action_card_caravan()
        elif card.name == 'black_knight':
            self.play_action_card_black_knight()
        else:
            print(f'action card {card.name} cannot be played now')
            return

        self.cardsInHand.remove(card)
        self.refresh_hand_board()

    ####################################################################################################################
    #################   HELPER METHODS         #########################################################################
    ####################################################################################################################

    def trade(self) -> None:
        print('trading started')
        resourceToPay: Optional[Resource] = self.select_resource_to_trade_for()
        if resourceToPay is None:
            return

        rate: int = self.get_resource_cost(resourceToPay)
        print(f'{resourceToPay.value} can be traded with rate of {rate}')

        cost = Cost()
        cost.set(resourceToPay, rate)
        if not self.can_cover_cost(cost):
            print(f'trade not possible, not enough {resourceToPay.value} available')
            return

        self.pay(cost)
        land: Landscape = self.select_resource_to_purchase()
        land.resourcesHeld += 1

        assert land.pos is not None
        self.game.mainBoard.refresh_square(land.pos)

    def take_back_to_hand(self, card: Buildable) -> None:
        assert card.pos is not None and card.settlement is not None and card.player is self

        slot = SettlementSlot(card.pos, self)
        slot.settlement = card.settlement
        slot.settlement.cards.append(slot)
        slot.settlement.cards.remove(card)

        card.settlement, card.player, card.pos = None, None, None

        if isinstance(card, Building):
            self.buildingsPlayed.remove(card)
        elif isinstance(card, Knight):
            self.knightsPlayed.remove(card)
        elif isinstance(card, Fleet):
            self.fleetPlayed.remove(card)

        self.cardsInHand.append(card)
        self.refresh_hand_board()
        self.game.mainBoard.set_square(slot.pos, slot)

    def action_card_get_toss_winner(self, actionName: str) -> Player:
        assert actionName in DEFENCE_CARDS, f'no defence against {actionName}'

        if self.opponent.use_defence(actionName):
            self.opponent.remove_action_card(DEFENCE_CARDS[actionName])
            print(f'defence against {actionName} activated')
            actionSuccessFrom6 = 2
        else:
            print(f'defence against {actionName} NOT activated')
            actionSuccessFrom6 = 5

        self.game.display.print_msg('press ok to toss')
        self.wait_for_ok()

        toss = randint(1, 6)
        if toss <= actionSuccessFrom6:
            print(f'tossed {toss}, action succeeded')
            return self
        else:
            print(f'tossed {toss}, action failed')
            return self.opponent

    def lose_ambush_resources(self) -> None:
        for land in self.landscapeCards:
            if land.resource.value in STOLEN_AMBUSH_RESOURCES:
                land.resourcesHeld = 0
                assert land.pos is not None
                self.game.mainBoard.refresh_square(land.pos)

    def use_defence(self, action: str) -> bool:
        assert action in DEFENCE_CARDS, f'there is no defence against {action}'
        return self.card_in_hand(DEFENCE_CARDS[action]) and self.decide_use_defence(action)

    def pay(self, cost: Cost | int) -> None:
        self.game.display.print_msg('now you need to pay')
        if isinstance(cost, Cost):
            self.pay_specific(cost)
        else:
            self.pay_any(cost)

    def pay_specific(self, cost: Cost) -> None:
        costToPay = copy.copy(cost)
        while not costToPay.is_zero():
            land: Landscape = self.select_card_to_pay(costToPay)
            assert land.pos is not None
            costToPay.take(land.resource)
            land.resourcesHeld -= 1
            self.game.mainBoard.refresh_square(land.pos)

    def pay_any(self, cost: int) -> None:
        while cost > 0:
            land: Landscape = self.select_card_to_pay()
            assert land.pos is not None
            cost -= 1
            land.resourcesHeld -= 1
            self.game.mainBoard.refresh_square(land.pos)

    ####################################################################################################################
    #################   REFILL HAND METHODS                #############################################################
    ####################################################################################################################

    def refill_hand_take_card(self, pile: Pile) -> None:
        payToBrowse = 1 if self.has_browse_discount() else 2
        if self.can_cover_cost(payToBrowse) and self.decide_browse_pile():
            self.pay(payToBrowse)
            card = self.select_card_from_choice(pile)
        else:
            card = pile[0]

        pile.remove(card)
        self.cardsInHand.append(card)
        self.refresh_hand_board()

    def refill_hand_remove_card(self, pile: Pile) -> None:
        card = self.select_card_to_throw_away()
        self.cardsInHand.remove(card)
        pile.append(card)
        self.refresh_hand_board()

    def refill_hand(self) -> None:
        maxCardsInHand = self.get_hand_cards_cnt()
        if len(self.cardsInHand) < maxCardsInHand:
            while len(self.cardsInHand) < maxCardsInHand:
                pile = self.select_pile()
                self.refill_hand_take_card(pile)
        else:
            if len(self.cardsInHand) > maxCardsInHand:
                while len(self.cardsInHand) > maxCardsInHand:
                    pile = self.select_pile()
                    self.refill_hand_remove_card(pile)
            if self.decide_swap_one_card():
                pile = self.select_pile()
                self.refill_hand_remove_card(pile)
                self.refill_hand_take_card(pile)

    ####################################################################################################################
    #################   ALL DECISIONS ARE MADE IN ABSTRACT METHODS      ################################################
    ####################################################################################################################

    @abstractmethod
    def wait_for_ok(self) -> None:
        pass

    @abstractmethod
    def select_card_from_choice(self, pile: Pile) -> Playable:
        pass

    @abstractmethod
    def select_pile(self, unavailablePile: Optional[Pile]=None) -> Pile:
        pass

    @abstractmethod
    def decide_swap_one_card(self) -> bool:
        pass

    @abstractmethod
    def select_new_card_position(self, infraType: Type[Village | Path | Town | Buildable], townOnly=False) -> Optional[Pos]:
        pass

    @abstractmethod
    def select_card_to_pay(self, resource: Optional[Cost]=None) -> Landscape:
        pass

    @abstractmethod
    def initial_land_setup(self) -> None:
        pass

    @abstractmethod
    def pick_starting_cards(self) -> None:
        pass

    @abstractmethod
    def throw_dice(self) -> None:
        pass

    @abstractmethod
    def do_actions(self) -> None:
        pass

    @abstractmethod
    def pick_any_resource(self) -> None:
        pass

    @abstractmethod
    def grab_any_resource_if_possible(self) -> None:
        pass

    @abstractmethod
    def decide_browse_pile(self) -> bool:
        pass

    @abstractmethod
    def select_card_to_throw_away(self) -> Playable:
        pass

    @abstractmethod
    def select_opponents_unit_to_remove(self) -> Buildable:
        pass

    @abstractmethod
    def select_card_to_steal_by_spy(self) -> Knight | Fleet | Action:
        pass

    @abstractmethod
    def decide_use_defence(self, againstCard: str) -> bool:
        pass

    @abstractmethod
    def select_building_to_burn(self) -> Building:
        pass

    @abstractmethod
    def select_knight_to_kill(self) -> Knight:
        pass

    @abstractmethod
    def select_opponents_card_to_discard(self) -> Playable:
        pass

    @abstractmethod
    def give_any_resource(self) -> None:
        pass

    @abstractmethod
    def trade_with_caravan(self) -> None:
        pass

    @abstractmethod
    def select_resource_to_trade_for(self) -> Optional[Resource]:
        pass

    @abstractmethod
    def select_resource_to_purchase(self) -> Landscape:
        pass

    @abstractmethod
    def decide_use_scout(self) -> bool:
        pass

    @abstractmethod
    def select_new_land(self) -> Landscape:
        pass