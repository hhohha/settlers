from typing import List, Optional
import config
from card import Card
from util import Pos


class Board:
    def __init__(self, size: Pos, squareSize: Pos):
        self.size: Pos = size
        self.squareSize: Pos = squareSize
        self.squares: List[Optional[Card]] = [None] * self.size.x * self.size.y
        self.editedSquares: List[Pos] = []
        self.topLeft: Optional[Pos] = None
        self.bottomRight: Optional[Pos] = None
        self.spacing: int = config.CARD_IMG_SPACING

    def get_square(self, pos: Pos) -> Optional[Card]:
        return self.squares[pos.x + self.size.x * pos.y]

    def set_square(self, pos: Pos, card: Card) -> None:
        self.squares[pos.x + self.size.x * pos.y] = card
        self.editedSquares.append(pos)

    def set_top_left(self, pos: Pos):
        self.topLeft = pos
        self.bottomRight = self.topLeft + (self.squareSize + 2 * self.spacing) * self.size

    def set_next_square(self, card: Card) -> None:
        for idx, square in enumerate(self.squares):
            if square is None or square.name == 'empty':
                self.set_square(Pos(idx % self.size.x, idx // self.size.x), card)
                return
        raise ValueError('no empty square')

    def get_edited_squares(self):
        while self.editedSquares:
            yield self.editedSquares.pop()
