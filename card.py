from __future__ import annotations

from abc import ABC
from typing import Optional, List, TYPE_CHECKING
from enums import Resource, BuildingType, ActionCardType, EventCardType
from util import Cost, Pos
if TYPE_CHECKING:
    from player import Player
    from board import Board


class Card(ABC):
    def __init__(self, name: str, player: Optional[Player]):
        self.name = name
        self.player = player

    def __str__(self):
        return self.name

class MetaCard(Card):
    def __init__(self, name: str):
        super().__init__(name, None)

class Landscape(Card):
    def __init__(self, name: str, resource: Resource, diceNumber: int, player: Optional[Player] = None):
        super().__init__(name, player)
        self.resource: Resource = resource
        self.diceNumber = diceNumber
        self.resourcesHeld = 0
        self.pos: Optional[Pos] = None

class Path(Card):
    def __init__(self, player: Optional[Player] = None):
        super().__init__('path', player)

    cost: Cost = Cost(brick=2, wood=1)

class Settlement(Card, ABC):
    def __init__(self, name: str, pos: Pos, player: Player):
        super().__init__(name, player)
        self.player = player
        self.pos: Pos = pos

class Village(Settlement):
    def __init__(self, board: Board, pos: Pos, player):
        super().__init__('village', pos, player)
        self.squares: List[Pos] = [pos.up(), pos.down()]
        for pos in self.squares:
            card = board.get_square(pos)
            if card is not None:
                card.settlement = self

    cost: Cost = Cost(wood=1, sheep=1, brick=1, grain=1)

class Town(Settlement):
    def __init__(self, board: Board, pos: Pos, player):
        super().__init__('town', pos, player)
        self.cards: List[Building | Knight | Fleet] = []
        self.squares: List[Pos] = [pos.up(), pos.down(), pos.up(2), pos.down(2)]
        for pos in self.squares:
            card = board.get_square(pos)
            if card is not None:
                card.settlement = self

    cost: Cost = Cost(rock=3, grain=2)

class Event(Card):
    def __init__(self, name: str, eventType: EventCardType):
        super().__init__(name, None)
        self.eventType: EventCardType = eventType

class Playable(Card, ABC):
    def __init__(self, name: str, player: Optional[Player]):
        super().__init__(name, player)
        self.pos: Optional[Pos] = None

class Action(Playable):
    def __init__(self, name: str, actionType: ActionCardType, player: Optional[Player] = None):
        super().__init__(name, player)
        self.actionType = actionType

class Building(Playable):
    def __init__(self, name: str, buildingType: BuildingType, cost: Cost, townOnly: bool, victoryPoints: int, tradePoints: int, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost: Cost = cost
        self.townOnly: bool = townOnly
        self.victoryPoints: int = victoryPoints
        self.tradePoints: int = tradePoints
        self.buildingType: BuildingType = buildingType
        self.settlement: Optional[Settlement] = None

class Knight(Playable):
    def __init__(self, name: str, cost: Cost, tournamentStrength: int, battleStrength: int, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost: Cost = cost
        self.tournamentStrength: int = tournamentStrength
        self.battleStrength: int = battleStrength
        self.settlement: Optional[Settlement] = None

class Fleet(Playable):
    def __init__(self, name: str, cost: Cost, affectedResource: Resource, tradePoints, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost: Cost = cost
        self.affectedResource: Resource = affectedResource
        self.tradePoints: int = tradePoints
        self.settlement: Optional[Settlement] = None