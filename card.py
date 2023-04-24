from __future__ import annotations
from abc import ABC
from typing import Optional, List, TYPE_CHECKING
from enums import Resource, BuildingType, ActionCardType, EventCardType
from util import Cost, Pos
if TYPE_CHECKING:
    from player import Player


class Card(ABC):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class MetaCard(Card):
    def __init__(self, name: str):
        super().__init__(name)

class SettlementSlot(Card):
    def __init__(self, pos: Pos):
        super().__init__('highlighted')
        self.pos = pos
        self.settlement: Optional[Settlement] = None

class Landscape(Card):
    def __init__(self, name: str, resource: Resource, diceNumber: int):
        super().__init__(name)
        self.resource: Resource = resource
        self.diceNumber = diceNumber
        self.resourcesHeld = 0
        self.pos: Optional[Pos] = None
        self.player: Optional[Player] = None
        self.protectedByWarehouse: bool = False

class Path(Card):
    def __init__(self, pos: Pos, player: Player):
        super().__init__('path')
        self.pos = pos
        self.player = player

    cost: Cost = Cost(brick=2, wood=1)

class Settlement(Card, ABC):
    def __init__(self, name: str, pos: Pos, player: Player):
        super().__init__(name)
        self.pos = pos
        self.player = player

class Village(Settlement):
    def __init__(self, pos: Pos, player: Player):
        super().__init__('village', pos, player)
        self.cards: List[Buildable] = []
        self.buildPos: List[Pos] = [pos.up(), pos.down()]

    cost: Cost = Cost(wood=1, sheep=1, brick=1, grain=1)

class Town(Settlement):
    def __init__(self, pos: Pos, player: Player):
        super().__init__('town', pos, player)
        self.cards: List[Buildable] = []
        self.buildPos: List[Pos] = [pos.up(), pos.down(), pos.up(2), pos.down(2)]

    cost: Cost = Cost(rock=3, grain=2)

class Event(Card):
    def __init__(self, name: str, eventType: EventCardType):
        super().__init__(name)
        self.eventType: EventCardType = eventType

class Playable(Card, ABC):
    def __init__(self, name: str):
        super().__init__(name)
        self.player: Optional[Player] = None

class Action(Playable):
    def __init__(self, name: str, actionType: ActionCardType):
        super().__init__(name)
        self.actionType = actionType

class Buildable(Playable, ABC):
    def __init__(self, name: str, cost: Cost):
        super().__init__(name)
        self.settlement: Optional[Settlement] = None
        self.pos: Optional[Pos] = None
        self.cost: Cost = cost

class Building(Buildable):
    def __init__(self, name: str, buildingType: BuildingType, cost: Cost, townOnly: bool, victoryPoints: int, tradePoints: int):
        super().__init__(name, cost)
        self.townOnly: bool = townOnly
        self.victoryPoints: int = victoryPoints
        self.tradePoints: int = tradePoints
        self.buildingType: BuildingType = buildingType

class Knight(Buildable):
    def __init__(self, name: str, cost: Cost, tournamentStrength: int, battleStrength: int):
        super().__init__(name, cost)
        self.tournamentStrength: int = tournamentStrength
        self.battleStrength: int = battleStrength

class Fleet(Buildable):
    def __init__(self, name: str, cost: Cost, affectedResource: Resource, tradePoints):
        super().__init__(name, cost)
        self.affectedResource: Resource = affectedResource
        self.tradePoints: int = tradePoints
