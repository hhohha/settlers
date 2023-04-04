from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from enums import Button
from player import Player
from util import Pos, MouseClick, Pile

if TYPE_CHECKING:
    from game import Game
    from card import Landscape


class HumanPlayer(Player):
    def __init__(self, game: Game, number: int):
        super().__init__(game, number)

    def button_clicked(self, click: MouseClick) -> int:
        board, square = click.tuple()
        if board is not self.game.buttons:
            return Button.NO_BUTTON.value

        return square.x + square.y * self.game.buttons.size.x

    def initial_land_setup(self) -> None:
        landSelected: Optional[Pos] = None

        while True:
            click = self.game.display.get_mouse_click()

            if self.button_clicked(click) == Button.OK.value:
                return

            board, pos = click.tuple()
            card = board.get_square(pos)
            if board is self.game.mainBoard and isinstance(card, Landscape) and card.player is self:
                if landSelected is None:
                    landSelected = pos
                else:
                    board.set_square(pos, board.get_square(landSelected))
                    board.set_square(landSelected, card)
                    landSelected = None
            else:
                landSelected = None

    def select_pile(self) -> Pile:
        board, pos = self.game.display.get_mouse_click(self.game.mainBoard, ['back']).tuple()
        pileIdx = pos.x - board.size.x + len(self.game.cardPiles)
        return self.game.cardPiles[pileIdx]

    def get_card_from_choice(self, pile: Pile) -> None:
        self.game.display_cards_for_choice(pile)
        while True:
            board, pos = self.game.display.get_mouse_click(self.game.choiceBoard).tuple()
            if self.game.choiceBoard.get_square(pos).name != 'empty':
                break

        cardIdx = pos.x + self.game.choiceBoard.size.x * pos.y
        card = pile[cardIdx]
        self.game.select_card(card)

        click = self.game.display.get_mouse_click()
        if self.button_clicked(click) == Button.OK:
            self.add_card(card)
            self.game.handBoard.set_next_square(card)
            pile.pop(cardIdx)

    def pick_starting_cards(self) -> None:
        pile = self.select_pile()
        for _ in range(self.cardsInHandCnt):
            self.get_card_from_choice(pile)