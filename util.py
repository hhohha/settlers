from __future__ import annotations
from typing import Union, Tuple, TYPE_CHECKING, List, Optional, Type, Callable, Dict
from dataclasses import dataclass
from config import RESOURCE_LIST
from enums import DiceEvent, Resource, BuildingType

if TYPE_CHECKING:
    from player import Player
    from board import Board
    from card import Playable, Card

    Pile = List[Playable]


MILLS_EFFECTS: Dict[Resource, BuildingType] = {
    Resource.GRAIN: BuildingType.MILL,
    Resource.BRICK: BuildingType.BRICKYARD,
    Resource.ROCK: BuildingType.STEEL_MILL,
    Resource.SHEEP: BuildingType.SPINNING_MILL,
    Resource.WOOD: BuildingType.SAWMILL
}

@dataclass
class ClickFilter:
    board: Optional[Board] = None
    cardType: Optional[Type] = None
    cardNames: Optional[List[str]] = None
    cardNamesNeg: bool = False
    player: Optional[Player] = None
    check: Optional[Callable] = None

    def accepts(self, click: MouseClick) -> bool:
        if self.board is not None and self.board is not click.board:
            return False

        square: Optional[Card] = click.board.get_square(click.pos)
        if square is None:
            return False

        if self.cardType is not None and not isinstance(square, self.cardType):
            return False

        if self.cardNamesNeg:
            if self.cardNames is not None and square.name in self.cardNames:
                return False
        else:
            if self.cardNames is not None and square.name not in self.cardNames:
                return False

        if self.player is not None and self.player is not square.player:
            return False

        if self.check is not None and not self.check():
            return False

        return True

@dataclass(frozen=False)
class Cost:
    grain: int = 0
    sheep: int = 0
    rock: int = 0
    brick: int = 0
    wood: int = 0
    gold: int = 0

    def get(self, resource: Resource) -> int:
        return getattr(self, resource.value)

    def take(self, resource: Resource) -> None:
        setattr(self, resource.value, self.get(resource) - 1)

    def __ge__ (self, other) -> bool:
        return all([getattr(self, resource) >= getattr(other, resource) for resource in RESOURCE_LIST])

    def is_zero(self) -> bool:
        return all([getattr(self, resource) == 0 for resource in RESOURCE_LIST])

    def total(self) -> int:
        return self.gold + self.sheep + self.grain + self.brick + self.rock + self.wood

@dataclass(frozen=True)
class Pos:
    x: int
    y: int

    def __add__(self, other: Union['Pos', int]) -> 'Pos':
        if isinstance(other, Pos):
            return Pos(self.x + other.x, self.y + other.y)
        else:
            return Pos(self.x + other, self.y + other)

    def __sub__(self, other: Union['Pos', int]) -> 'Pos':
        if isinstance(other, Pos):
            return Pos(self.x - other.x, self.y - other.y)
        else:
            return Pos(self.x - other, self.y - other)

    def __mul__(self, other: Union['Pos', int]) -> 'Pos':
        if isinstance(other, Pos):
            return Pos(self.x * other.x, self.y * other.y)
        else:
            return Pos(self.x * other, self.y * other)

    def __floordiv__(self, other: Union['Pos', int]) -> 'Pos':
        if isinstance(other, Pos):
            return Pos(self.x // other.x, self.y // other.y)
        else:
            return Pos(self.x // other, self.y // other)

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def up(self, n: int = 1) -> 'Pos':
        return Pos(self.x, self.y - n)

    def down(self, n: int = 1) -> 'Pos':
        return Pos(self.x, self.y + n)

    def right(self, n: int = 1) -> 'Pos':
        return Pos(self.x + n, self.y)

    def left(self, n: int = 1) -> 'Pos':
        return Pos(self.x - n, self.y)

    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y

@dataclass(frozen=True)
class MouseClick:
    board: Board
    pos: Pos

    def tuple(self) -> Tuple[Board, Pos]:
        return self.board, self.pos

DiceEvents = {
    1: DiceEvent.TOURNAMENT,
    2: DiceEvent.TRADE_PROFIT,
    3: DiceEvent.AMBUSH,
    4: DiceEvent.GOOD_HARVEST,
    5: DiceEvent.CARD_EVENT,
    6: DiceEvent.CARD_EVENT
}

