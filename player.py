from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Optional

from util import Pos

if TYPE_CHECKING:
    from card import Playable, Landscape, Knight, Fleet, Building
    from game import Game
    from board import Board

class Player(ABC):
    def __init__(self, game: Game, handBoard: Board, number: int, handBoardVisible: bool):
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
        if len(self.cardsInHand) >= self.cardsInHandCnt:
            raise ValueError(f'cannot take a card, already at max')
        self.cardsInHand.append(card)

    def refresh_hand_board(self):
        self.handBoard.clear()
        for card in self.cardsInHand:
            self.handBoard.set_next_square(card)

    @abstractmethod
    def initial_land_setup(self) -> None:
        pass

    @abstractmethod
    def pick_starting_cards(self) -> None:
        pass

    @abstractmethod
    def throw_dice(self) -> None:
        pass

    #@abstractmethod
    def do_actions(self) -> None:
        pass

    #@abstractmethod
    def refill_hand(self) -> None:
        pass

    @abstractmethod
    def pick_any_resource(self) -> None:
        pass

    @abstractmethod
    def grab_any_resource(self) -> None:
        pass