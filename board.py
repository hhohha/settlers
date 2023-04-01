from typing import List, Optional, Tuple

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
        self.bottomRight = self.topLeft + (self.squareSize + 2*self.spacing) * self.size

    def get_edited_squares(self):
        while self.editedSquares:
            yield self.editedSquares.pop()


class BoardsController:
    def __init__(self):
        self.boards: List[Board] = []

    def add(self, board: Board) -> None:
        self.boards.append(board)

    def get_click_square(self, pos: Pos) -> Optional[Tuple[Board, Pos]]:
        for board in self.boards:
            if board.topLeft is None or board.bottomRight is None:
                continue
            if board.bottomRight > pos > board.topLeft:
                retPos = (pos - board.topLeft) // (board.squareSize + Pos(board.spacing, board.spacing))
                return board, retPos
        return None

