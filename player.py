from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Optional, Type
from card import Action
from enums import Resource
from util import Pos, Cost, CARDS_INCREASING_HAND_CNT, BROWSE_DISCOUNT_BUILDINGS

if TYPE_CHECKING:
    from card import Playable, Landscape, Knight, Fleet, Building, Village, Town, Path
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
        self.landscapeCards: Dict[Landscape, Pos] = {}
        self.knightsPlayed: Dict[Knight, Pos] = {}
        self.fleetPlayed:  Dict[Fleet, Pos] = {}
        self.buildingsPlayed: Dict[Building, Pos] = {}
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
        pos = self.initialLandPos.pop()
        print(pos, card)
        self.landscapeCards[card] = pos
        self.game.mainBoard.set_square(pos, card)

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
            self.landscapeCards[newLand] = pos

    def play_card_from_hand(self, card: Playable) -> None:
        if isinstance(card, Action):
            self.play_action_card(card)
            return

        if not self.can_cover_cost(card.cost):
            print('you cannot afford to play this')
            return

        townOnly: bool = card.townOnly if isinstance(card, Building) else False
        pos: Optional[Pos] = self.get_new_card_position(Playable, townOnly)
        if pos is None:
            return

        self.game.mainBoard.set_square(pos, card)
        self.cardsInHand.remove(card)
        self.refresh_hand_board()
        self.pay(card.cost)

    def build_infrastructure(self, infraType: Type[Village | Town | Path]) -> None:
        if self.game.infraCardsLeft[infraType] < 1:
            print(f'no more cards {infraType} left')
            return
        if not self.can_cover_cost(infraType.cost):
            print(f'you cannot afford this: {infraType}')

        pos: Optional[Pos] = self.get_new_card_position(infraType)
        if pos is None:
            return

        self.game.infraCardsLeft[infraType] -= 1
        if infraType is Path:
            newCard = Path()
        else:
            newCard = infraType(self.game.mainBoard, pos, self)

        self.game.mainBoard.set_square(pos, newCard)
        self.pay(infraType.cost)
        if infraType is Village:
            self.place_new_land(pos)


    def pay(self, cost: Cost | int) -> None:
        self.game.display.print_msg('now you need to pay')
        costToPay = copy.copy(cost)

        while not (costToPay.is_zero() if isinstance(cost, Cost) else costToPay == 0):
            card: Landscape = self.select_card_to_pay(None if isinstance(cost, int) else costToPay)

            if isinstance(cost, Cost):
                costToPay.take(card.resource)
            else:
                cost -= 1
            card.resourcesHeld -= 1
            self.game.mainBoard.refresh_square(self.landscapeCards[card])

    def refill_hand(self) -> None:
        maxCardsInHand = self.get_hand_cards_cnt()
        if len(self.cardsInHand) < maxCardsInHand:
            while len(self.cardsInHand) < maxCardsInHand:
                pile = self.select_pile()
                payToBrowse = 1 if self.has_browse_discount() else 2
                if self.can_cover_cost(payToBrowse) and self.decide_browse_pile():
                    self.pay(payToBrowse)
                else:
                    self.cardsInHand.append(pile.pop())
                    self.refresh_hand_board()
        else:
            if len(self.cardsInHand) > maxCardsInHand:
                while len(self.cardsInHand) > maxCardsInHand:
                    idx = self.select_card_to_throw_away()
                    self.cardsInHand.pop(idx)
                    self.refresh_hand_board()
            if self.swap_one_card():
                idx = self.select_card_to_throw_away()
                self.cardsInHand.pop(idx)
                self.refresh_hand_board()
                self.refill_hand()

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
    def get_new_card_position(self, infraType: Type[Village | Path | Town | Playable], townOnly=False) -> Optional[Pos]:
        pass

    @abstractmethod
    def select_card_to_pay(self, resource: Optional[Resource]) -> Landscape:
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
