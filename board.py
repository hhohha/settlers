from typing import List, Optional
import config
from card import Card
from util import Pos


class Board:
    def __init__(self, size: Pos, squareSize: Pos):
        self.size: Pos = size
        self.squareSize: Pos = squareSize
        self.squares: List[Optional[Card]] = [None for _ in range (self.size.x * self.size.y)]
        self.editedSquares: List[Pos] = []
        self.topLeft: Optional[Pos] = None
        self.bottomRight: Optional[Pos] = None
        self.spacing: int = config.CARD_IMG_SPACING

    def to_int(self, pos: Pos) -> int:
        return pos.x + self.size.x * pos.y

    def to_pos(self, n: int) -> Pos:
        return Pos(n % self.size.x, n // self.size.x)

    def get_square(self, pos: Pos) -> Optional[Card]:
        return self.squares[self.to_int(pos)]

    def set_square(self, pos: Pos, card: Card) -> None:
        self.squares[self.to_int(pos)] = card
        self.editedSquares.append(pos)

    def refresh_square(self, pos: Pos) -> None:
        self.editedSquares.append(pos)

    def clear_square(self, pos: Pos) -> None:
        self.squares[self.to_int(pos)] = None
        self.editedSquares.append(pos)

    def set_top_left(self, pos: Pos):
        self.topLeft = pos
        self.bottomRight = self.topLeft + (self.squareSize + 2 * self.spacing) * self.size

    def set_next_square(self, card: Card) -> None:
        for idx, square in enumerate(self.squares):
            if square is None or square.name == 'empty':
                self.set_square(self.to_pos(idx), card)
                return
        raise ValueError('no empty square')

    def get_edited_squares(self):
        while self.editedSquares:
            yield self.editedSquares.pop()

    def clear(self):
        for idx, _ in enumerate(self.squares):
            self.clear_square(self.to_pos(idx))

    def fill_board(self, card: Card):
        for idx, _ in enumerate(self.squares):
            self.set_square(self.to_pos(idx), card)