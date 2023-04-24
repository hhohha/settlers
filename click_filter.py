from typing import Optional, Type, List, Callable
from dataclasses import dataclass

from board import Board
from card import Card, Settlement, Path, Playable, Landscape
from player import Player
from util import MouseClick


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

        assert isinstance(square, Card)
        if self.cardNamesNeg:
            if self.cardNames is not None and square.name in self.cardNames:
                return False
        else:
            if self.cardNames is not None and square.name not in self.cardNames:
                return False

        if self.player is not None:
            if not hasattr(square, 'player'):
                return False
            assert isinstance(square, Settlement | Path | Playable | Landscape)
            if self.player is not square.player:
                return False

        if self.check is not None and not self.check():
            return False

        return True