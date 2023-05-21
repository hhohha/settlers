from __future__ import annotations
from typing import Union, Tuple, TYPE_CHECKING, Dict, Type
from dataclasses import dataclass

import config
from config import RESOURCE_LIST
from enums import DiceEvent, Resource
if TYPE_CHECKING:
    from board import Board
    from card import Knight, Fleet

MILLS_EFFECTS: Dict[Resource, str] = {
    Resource.GRAIN: 'mill',
    Resource.BRICK: 'brickyard',
    Resource.ROCK: 'steel_mill',
    Resource.SHEEP: 'spinning_mill',
    Resource.WOOD: 'sawmill'
}

def is_next_to(board: Board, pos: Pos, cardType: Type) -> bool:
    if pos.x + 1 < board.size.x and isinstance(board.get_square(pos.right()), cardType):
        return True

    return pos.x - 1 >= 0 and isinstance(board.get_square(pos.left()), cardType)

def is_protected_from_civil_war(card: Knight | Fleet) -> bool:
    for protection in config.CIVIL_WAR_PROTECTION:
        assert card.settlement is not None
        if protection in map(lambda c: c.name, card.settlement.cards):
            return True
    return False

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

    def set(self, resource: Resource, n: int) -> None:
        setattr(self, resource.value, n)

    def take(self, resource: Resource, n: int=1) -> None:
        assert self.get(resource) >= n, f'cannot take {n} of resource {resource}'
        self.set(resource, self.get(resource) - n)

    def __ge__ (self, other) -> bool:
        return all([getattr(self, resource) >= getattr(other, resource) for resource in RESOURCE_LIST])

    def is_zero(self) -> bool:
        return self.total() == 0

    def total(self) -> int:
        return self.gold + self.sheep + self.grain + self.brick + self.rock + self.wood

@dataclass(frozen=True)
class Pos:
    x: int
    y: int

    def __add__(self, other: Union[Pos, int]) -> Pos:
        if isinstance(other, Pos):
            return Pos(self.x + other.x, self.y + other.y)
        else:
            return Pos(self.x + other, self.y + other)

    def __sub__(self, other: Union[Pos, int]) -> Pos:
        if isinstance(other, Pos):
            return Pos(self.x - other.x, self.y - other.y)
        else:
            return Pos(self.x - other, self.y - other)

    def __mul__(self, other: Union[Pos, int]) -> Pos:
        if isinstance(other, Pos):
            return Pos(self.x * other.x, self.y * other.y)
        else:
            return Pos(self.x * other, self.y * other)

    def __floordiv__(self, other: Union[Pos, int]) -> Pos:
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

    def up(self, n: int = 1) -> Pos:
        return Pos(self.x, self.y - n)

    def down(self, n: int = 1) -> Pos:
        return Pos(self.x, self.y + n)

    def right(self, n: int = 1) -> Pos:
        return Pos(self.x + n, self.y)

    def left(self, n: int = 1) -> Pos:
        return Pos(self.x - n, self.y)

    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y

@dataclass(frozen=True)
class MouseClick:
    board: Board
    pos: Pos

    def tuple(self) -> Tuple[Board, Pos]:
        return self.board, self.pos

DiceEvents: Dict[int, DiceEvent] = {
    1: DiceEvent.TOURNAMENT,
    2: DiceEvent.TRADE_PROFIT,
    3: DiceEvent.AMBUSH,
    4: DiceEvent.GOOD_HARVEST,
    5: DiceEvent.CARD_EVENT,
    6: DiceEvent.CARD_EVENT
}

DEFENCE_CARDS: Dict[str, str] = {
    'arson': 'bishop',
    'black_knight': 'witch',
    'ambush' : 'bishop'
}