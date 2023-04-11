from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Optional, Type

from enums import Resource
from util import Pos, Cost, CARDS_INCREASING_HAND_CNT

if TYPE_CHECKING:
    from card import Playable, Landscape, Knight, Fleet, Building, Settlement, Village, Town, Path
    from game import Game
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

    def can_cover_cost(self, cost: Cost) -> bool:
        return self.get_resources_available() >= cost

    def setup_land_card(self, card: Landscape):
        pos = self.initialLandPos.pop()
        print(pos, card)
        self.landscapeCards[card] = pos
        self.game.mainBoard.set_square(pos, card)

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

    def build_infrastructure(self, infraType: Type[Village | Town | Path]) -> None:
        if self.game.infraCardsLeft[infraType] < 1:
            print(f'no more cards {infraType} left')
            return
        if not self.can_cover_cost(infraType.cost):
            print(f'you cannot afford this: {infraType}')

        pos: Optional[Pos] = self.get_new_infra_position(infraType)
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

    @abstractmethod
    def get_new_infra_position(self, infraType: Type[Village | Town | Path]) -> Optional[Pos]:
        pass

    @abstractmethod
    def pay(self, cost: Cost) -> None:
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
    def refill_hand(self) -> None:
        pass

    @abstractmethod
    def pick_any_resource(self) -> None:
        pass

    @abstractmethod
    def grab_any_resource(self) -> None:
        pass