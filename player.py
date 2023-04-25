from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Optional, Type
from card import Action, Buildable, Building, Playable, SettlementSlot, Village, Town, Path, Knight, Fleet
from config import BROWSE_DISCOUNT_BUILDINGS, CARDS_INCREASING_HAND_CNT, STOLEN_AMBUSH_RESOURCES
from enums import Resource
from util import Pos, Cost

if TYPE_CHECKING:
    from card import Landscape
    from game import Game, Pile
    from board import Board

class Player(ABC):
    def __init__(self, game: Game, handBoard: Board, number: int, handBoardVisible: bool, midPos: Pos):
        self.game: Game = game
        self.opponent: Optional[Player] = None
        self.handBoard = handBoard
        self.number: int = number
        self.victoryPoints = 0
        self.tradePoints = 0
        self.tournamentPoints = 0
        self.battlePoints = 0
        self.cardsInHandCnt: int = 3
        self.cardsInHand: List[Playable] = []
        self.landscapeCards: List[Landscape] = []
        self.knightsPlayed: List[Knight] = []
        self.fleetPlayed:  List[Fleet] = []
        self.buildingsPlayed: List[Building] = []
        self.handBoardVisible: bool = handBoardVisible
        self.midPos: Pos = midPos
        self.initialLandPos: List[Pos] = [midPos.up(), midPos.down(), midPos + Pos(2, 1), midPos + Pos(2, -1),
                                          midPos + Pos(-2, 1), midPos + Pos(-2, -1)]

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

    def setup_land_card(self, card: Landscape):
        card.pos = self.initialLandPos.pop()
        self.landscapeCards.append(card)
        self.game.mainBoard.set_square(card.pos, card)

    def has_browse_discount(self) -> bool:
        for cardName in BROWSE_DISCOUNT_BUILDINGS:
            if cardName in map(lambda b: b.name, self.buildingsPlayed):
                return True
        return False

    def get_tournament_strength(self) -> int:
        return sum(map(lambda k: k.tournamentStrength, self.knightsPlayed))

    def get_trade_strength(self):
        return sum(map(lambda b: b.tradePoints, self.buildingsPlayed)) + sum(map(lambda f: f.tradePoints, self.fleetPlayed))

    def get_battle_strength(self):
        strength = sum(map(lambda k: k.battleStrength, self.knightsPlayed))
        if 'smithy' in map(lambda b: b.name, self.buildingsPlayed):
            strength += len(self.knightsPlayed)
        return strength

    def take_card(self, card: Playable) -> None:
        self.cardsInHand.append(card)
        self.game.player1Board.set_next_square(card)

    def add_card(self, card: Playable):
        if len(self.cardsInHand) >= self.get_hand_cards_cnt():
            raise ValueError(f'cannot take a card, already at max')
        self.cardsInHand.append(card)

    def refresh_hand_board(self):
        self.handBoard.clear()
        for card in self.cardsInHand:
            self.handBoard.set_next_square(card)

    def is_next_to(self, pos: Pos, cardType: Type) -> bool:
        posRight, posLeft = pos.right(), pos.left()
        b = self.game.mainBoard
        if posRight.x < b.size.x and isinstance(b.get_square(posRight), cardType):
            return True

        return posLeft.x >= 0 and isinstance(b.get_square(posLeft), cardType)

    def get_hand_cards_cnt(self) -> int:
        return self.cardsInHandCnt + len([True for b in self.buildingsPlayed if b.name in CARDS_INCREASING_HAND_CNT])

    def place_new_land(self, villagePos: Pos) -> None:
        if villagePos.x > self.midPos.x:
            landPositions = villagePos.up().right(), villagePos.down().right()
        else:
            landPositions = villagePos.up().left(), villagePos.down().left()

        for pos in landPositions:
            newLand = self.game.landscapeCards.pop()
            self.game.mainBoard.set_square(pos, newLand)
            newLand.player = self
            self.landscapeCards.append(newLand)
            newLand.pos = pos

    def play_card_from_hand(self, card: Playable) -> None:
        if isinstance(card, Action):
            self.play_action_card(card)
            return

        assert isinstance(card, Buildable)

        if not self.can_cover_cost(card.cost):
            print('you cannot afford to play this')
            return

        townOnly: bool = card.townOnly if isinstance(card, Building) else False
        pos: Optional[Pos] = self.get_new_card_position(Buildable, townOnly)
        if pos is None:
            return

        self.game.mainBoard.set_square(pos, card)
        card.pos = pos

        if isinstance(card, Building):
            self.buildingsPlayed.append(card)
        elif isinstance(card, Knight):
            self.knightsPlayed.append(card)
        elif isinstance(card, Fleet):
            self.fleetPlayed.append(card)

        self.apply_card_effect()
        self.cardsInHand.remove(card)
        self.refresh_hand_board()
        self.pay(card.cost)

    def apply_card_effect(self) -> None:
            # TODO - implement this
        pass

    def get_unprotected_resources_cnt(self) -> int:
        return sum(map(lambda l: 0 if l.protectedByWarehouse else l.resourcesHeld, self.landscapeCards))

    def lose_ambush_resources(self):
        for land in self.landscapeCards:
            if land.resource.value in STOLEN_AMBUSH_RESOURCES:
                land.resourcesHeld = 0
                self.game.mainBoard.refresh_square(land.pos)

    def build_infrastructure(self, infraType: Type[Town | Village | Path]) -> None:
        if self.game.infraCardsLeft[infraType] < 1:
            print(f'no more cards {infraType} left')
            return
        if not self.can_cover_cost(infraType.cost):
            print(f'you cannot afford this: {infraType}')
            return

        pos: Optional[Pos] = self.get_new_card_position(infraType)
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
            self.game.mainBoard.set_square(pos, Path(pos, self))
        else:
            assert False, f'build infrastructure got bad infratype: {infraType}'

    def place_village_to_board(self, pos: Pos) -> None:
        newVillage = Village(pos, self)
        self.game.mainBoard.set_square(pos, newVillage)
        for p in [pos.up(), pos.down()]:
            slot = SettlementSlot(p)
            self.game.mainBoard.set_square(p, slot)
            slot.settlement = newVillage
            newVillage.slots.append(slot)

    def place_town_to_board(self, pos: Pos) -> None:
        newTown = Town(pos, self)
        self.game.mainBoard.set_square(pos, newTown)

        for p in [pos.up(), pos.down()]:
            slot = self.game.mainBoard.get_square(p)
            assert isinstance(slot, SettlementSlot) or isinstance(slot, Buildable)
            newTown.slots.append(slot)
            slot.settlement = newTown

        for p in [pos.up(2), pos.down(2)]:
            slot = SettlementSlot(p)
            self.game.mainBoard.set_square(p, slot)
            slot.settlement = newTown
            newTown.slots.append(slot)


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
            land: Landscape = self.select_card_to_pay(None)
            assert land.pos is not None
            cost -= 1
            land.resourcesHeld -= 1
            self.game.mainBoard.refresh_square(land.pos)

    def pay(self, cost: Cost | int) -> None:
        self.game.display.print_msg('now you need to pay')
        if isinstance(cost, Cost):
            return self.pay_specific(cost)
        else:
            return self.pay_any(cost)


    #TODO - refactor duplicated code
    def refill_hand(self, canSwap: bool) -> None:
        maxCardsInHand = self.get_hand_cards_cnt()
        if len(self.cardsInHand) < maxCardsInHand:
            while len(self.cardsInHand) < maxCardsInHand:
                pile = self.select_pile()
                payToBrowse = 1 if self.has_browse_discount() else 2
                if self.can_cover_cost(payToBrowse) and self.decide_browse_pile():
                    self.pay(payToBrowse)
                    self.get_card_from_choice(pile)
                else:
                    self.cardsInHand.append(pile.pop())
                    self.refresh_hand_board()
        else:
            if len(self.cardsInHand) > maxCardsInHand:
                while len(self.cardsInHand) > maxCardsInHand:
                    idx = self.select_card_to_throw_away()
                    self.cardsInHand.pop(idx)
                    self.refresh_hand_board()
            if canSwap and self.swap_one_card():
                idx = self.select_card_to_throw_away()
                removedCard = self.cardsInHand.pop(idx)
                self.refresh_hand_board()
                pile = self.select_pile()
                payToBrowse = 1 if self.has_browse_discount() else 2
                if self.can_cover_cost(payToBrowse) and self.decide_browse_pile():
                    self.pay(payToBrowse)
                    self.get_card_from_choice(pile)
                else:
                    self.cardsInHand.append(pile.pop(0))
                    self.refresh_hand_board()
                pile.append(removedCard)

    @abstractmethod
    def get_card_from_choice(self, pile: Pile) -> None:
        pass

    @abstractmethod
    def select_pile(self) -> Pile:
        pass

    @abstractmethod
    def swap_one_card(self) -> bool:
        pass

    @abstractmethod
    def play_action_card(self, card: Action) -> None:
        pass

    @abstractmethod
    def get_new_card_position(self, infraType: Type[Village | Path | Town | Buildable], townOnly=False) -> Optional[Pos]:
        pass

    @abstractmethod
    def select_card_to_pay(self, resource: Optional[Cost]) -> Landscape:
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
    def grab_any_resource(self) -> None:
        pass

    @abstractmethod
    def decide_browse_pile(self) -> bool:
        pass

    @abstractmethod
    def select_card_to_throw_away(self) -> int:
        pass
