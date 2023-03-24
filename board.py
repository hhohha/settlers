from typing import List, Optional
import config
from card import Card
from util import Pos


class Board:
    def __init__(self):
        self.size: Pos = Pos(config.BOARD_SIZE)
        self.squares: List[Optional[Card]] = [None] * self.size.x * self.size.y
        self.editedSquares: List[Pos] = []

    def get_square(self, pos: Pos) -> Optional[Card]:
        return self.squares[pos.x * self.size.x + pos.y]

    def set_square(self, pos: Pos, card: Card) -> None:
        self.squares[pos.x * self.size.x + pos.y] = card
        self.editedSquares.append(pos)
