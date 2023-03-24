from abc import ABC
from typing import Optional

from enums import Resource, BuildingType, ActionCardType, EventCardType
from player import Player
from util import Cost


class Card(ABC):
    def __init__(self, player: Optional[Player]):
        self.player = player


class Landscape(Card):
    def __init__(self, resource: Resource, diceNumber: int, player: Player = None):
        super().__init__(player)
        self.resource: Resource = resource
        self.diceNumber = diceNumber


class Path(Card):
    def __init__(self, player: Player):
        super().__init__(player)


class Settlement(Card, ABC):
    def __init__(self, player: Player):
        super().__init__(player)


class Village(Settlement):
    def __init__(self, player: Player):
        super().__init__(player)


class Town(Settlement):
    def __init__(self, player: Player):
        super().__init__(player)


class Event(Card):
    def __init__(self, eventType: EventCardType):
        super().__init__(None)
        self.eventType: EventCardType = eventType

class Playable(Card, ABC):
    def __init__(self, player: Player, name: str):
        super().__init__(player)
        self.name = name


class Action(Playable):
    def __init__(self, actionType: ActionCardType, player: Optional[Player] = None):
        super().__init__(player, '')
        self.actionType = actionType


class Building(Playable):
    def __init__(self, buildingType: BuildingType, cost: Cost, townOnly: bool, victoryPoints: int, tradePoints: int, image, player: Optional[Player] = None):
        super().__init__(player, '')
        self.cost = cost
        self.townOnly = townOnly
        self.victoryPoints = victoryPoints
        self.tradePoints = tradePoints
        self.buildingType: BuildingType = buildingType


class Knight(Playable):
    def __init__(self, name: str, cost: Cost, tournamentStrength: int, battleStrength: int, player: Optional[Player] = None):
        super().__init__(player, name)
        self.cost = cost
        self.tournamentStrength = tournamentStrength
        self.battleStrength = battleStrength


class Fleet(Playable):
    def __init__(self, cost: Cost, affectedResource: Resource, tradePoints, image, player: Optional[Player] = None):
        super().__init__(player, '')
        self.cost = cost
        self.affectedResource: affectedResource
        self.tradePoints = tradePoints
        self.image = image
