from __future__ import annotations
from typing import TYPE_CHECKING
from player import Player

if TYPE_CHECKING:
    from game import Game
    from util import Pile

class ComputerPlayer(Player):
    def __init__(self, game: Game, number: int):
        super().__init__(game, number)

    def initial_land_setup(self) -> None:
        # TODO - move gold to the middle
        pass

    def selectPile(self) -> Pile:
        # TODO
        # always selects the pile with most cards, that is suitable for first select but needs to improve
        # for subsequent selections - at least pick those that haven't been picked (longest), or those we know/think
        # have card(s) we want
        resIdx, maxLen = 0, 0
        for idx, pile in enumerate(self.game.cardPiles):
            if len(pile) > maxLen:
                maxLen, resIdx = len(pile), idx
        return self.game.cardPiles[resIdx]

    def pick_starting_cards(self) -> None:
        pass