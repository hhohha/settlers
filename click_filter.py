from typing import Optional, Type, Tuple
from dataclasses import dataclass

from board import Board
from card import Card, Settlement, Path, Playable, Landscape
from player import Player
from util import MouseClick


@dataclass
class ClickFilter:
    board: Optional[Board] = None
    cardType: None | Type | Tuple[Type, ...] = None
    cardName: Optional[str] = None
    player: Optional[Player] = None

    def accepts(self, click: MouseClick) -> bool:
        if self.board is not None and self.board is not click.board:
            return False

        square: Optional[Card] = click.board.get_square(click.pos)
        if square is None:
            return False

        if self.cardType is not None and not isinstance(square, self.cardType):
            return False

        assert isinstance(square, Card)
        if self.cardName is not None and square.name != self.cardName:
            return False

        if self.player is not None:
            if not hasattr(square, 'player'):
                return False
            assert isinstance(square, Settlement | Path | Playable | Landscape)
            if self.player is not square.player:
                return False

        return True