from typing import Union, Tuple

from dataclasses import dataclass
from enums import DiceEvent


@dataclass(frozen=True)
class Cost:
    grain: int = 0
    sheep: int = 0
    rock: int = 0
    brick: int = 0
    wood: int = 0


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

    def up(self, n: int) -> 'Pos':
        return Pos(self.x, self.y - n)

    def down(self, n: int) -> 'Pos':
        return Pos(self.x, self.y + n)

    def right(self, n: int) -> 'Pos':
        return Pos(self.x + n, self.y)

    def left(self, n: int) -> 'Pos':
        return Pos(self.x - n, self.y)

    def tuple(self) -> Tuple[int, int]:
        return self.x, self.y

DiceEvents = {
    1: DiceEvent.TOURNAMENT,
    2: DiceEvent.TRADE_PROFIT,
    3: DiceEvent.AMBUSH,
    4: DiceEvent.GOOD_HARVEST,
    5: DiceEvent.CARD_EVENT,
    6: DiceEvent.CARD_EVENT
}

