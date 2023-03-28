from typing import List, Optional
from card import Card, MetaCard
from util import Pos


class Board:
    def __init__(self, size: Pos):
        self.size: Pos = size
        self.squares: List[Optional[Card]] = [None] * self.size.x * self.size.y
        self.editedSquares: List[Pos] = []

    def get_square(self, pos: Pos) -> Optional[Card]:
        return self.squares[pos.x + self.size.x * pos.y]

    def set_square(self, pos: Pos, card: Card) -> None:
        self.squares[pos.x + self.size.x * pos.y] = card
        self.editedSquares.append(pos)

    def get_edited_squares(self):
        while self.editedSquares:
            yield self.editedSquares.pop()
