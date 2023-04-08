from abc import ABC
from typing import Optional
from enums import Resource, BuildingType, ActionCardType, EventCardType
from player import Player
from util import Cost


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
        self.resourceYield = 1 # how many resources gained when yielding, can be increased by mills
        self.isProtectedByWarehouse = False

class Path(Card):
    def __init__(self, player: Optional[Player] = None):
        super().__init__('path', player)
        self.cost: Cost = Cost(brick=2, wood=1)

class Settlement(Card, ABC):
    def __init__(self, name: str, player: Optional[Player]):
        super().__init__(name, player)

class Village(Settlement):
    def __init__(self, player: Optional[Player] = None):
        super().__init__('village', player)
        self.cost: Cost = Cost(wood=1, sheep=1, brick=1, grain=1)

class Town(Settlement):
    def __init__(self, player: Optional[Player] = None):
        super().__init__('town', player)
        self.cost: Cost = Cost(rock=3, grain=2)

class Event(Card):
    def __init__(self, name: str, eventType: EventCardType):
        super().__init__(name, None)
        self.eventType: EventCardType = eventType

class Playable(Card, ABC):
    def __init__(self, name: str, player: Optional[Player]):
        super().__init__(name, player)

class Action(Playable):
    def __init__(self, name: str, actionType: ActionCardType, player: Optional[Player] = None):
        super().__init__(name, player)
        self.actionType = actionType

class Building(Playable):
    def __init__(self, name: str, buildingType: BuildingType, cost: Cost, townOnly: bool, victoryPoints: int, tradePoints: int, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost = cost
        self.townOnly = townOnly
        self.victoryPoints = victoryPoints
        self.tradePoints = tradePoints
        self.buildingType: BuildingType = buildingType

class Knight(Playable):
    def __init__(self, name: str, cost: Cost, tournamentStrength: int, battleStrength: int, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost = cost
        self.tournamentStrength = tournamentStrength
        self.battleStrength = battleStrength

class Fleet(Playable):
    def __init__(self, name: str, cost: Cost, affectedResource: Resource, tradePoints, player: Optional[Player] = None):
        super().__init__(name, player)
        self.cost = cost
        self.affectedResource: affectedResource
        self.tradePoints = tradePoints
