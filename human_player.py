from __future__ import annotations

import copy
from typing import Optional, TYPE_CHECKING
from enums import Button, DiceEvent
from player import Player
from util import Pos, MouseClick, Pile, ClickFilter, RESOURCE_LIST, Cost
from card import Landscape, Playable, Path, Card

if TYPE_CHECKING:
    from game import Game
    from board import Board


class HumanPlayer(Player):
    def __init__(self, game: Game, handBoard: Board, number: int, midPos: Pos):
        super().__init__(game, handBoard, number, True, midPos)

    def button_clicked(self, click: MouseClick) -> int:
        board, square = click.tuple()
        if board is not self.game.buttons:
            return Button.NO_BUTTON.value

        return square.x + square.y * self.game.buttons.size.x

    def initial_land_setup(self) -> None:
        landSelected: Optional[Pos] = None
        self.game.display.print_msg('setup land cards')

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
        board, pos = self.game.get_filtered_click([ClickFilter(board=self.game.mainBoard, cardTypes=['back'])]).tuple()
        pileIdx = pos.x - board.size.x + len(self.game.cardPiles)
        return self.game.cardPiles[pileIdx]

    def get_card_from_choice(self, pile: Pile) -> None:
        selectedCardIdx: Optional[int] = None
        self.game.choiceBoard.clear()
        for idx, card in enumerate(pile):
            self.game.choiceBoard.set_next_square(card)

        while True:
            click: MouseClick = self.game.display.get_mouse_click()
            if selectedCardIdx is not None and self.button_clicked(click) == Button.OK.value:
                card = pile.pop(selectedCardIdx)
                self.add_card(card)
                self.refresh_hand_board()
                return

            if click.board is not self.game.choiceBoard or self.game.choiceBoard.get_square(click.pos) is None:
                continue

            cardIdx = click.board.to_int(click.pos)
            card = pile[cardIdx]
            self.game.select_card(card)
            selectedCardIdx = cardIdx

    def pick_starting_cards(self) -> None:
        self.game.display.print_msg('select pile')
        pile = self.select_pile()
        self.game.display.print_msg('select cards')
        while len(self.cardsInHand) < self.cardsInHandCnt:
            self.get_card_from_choice(pile)
        self.game.choiceBoard.clear()

    def grab_any_resource(self) -> None:
        opponentLandSelected: Optional[Landscape] = None
        selectedPos: Optional[Pos] = None

        while True:
            click = self.game.display.get_mouse_click(
                ClickFilter(board=self.game.mainBoard, cardTypes=RESOURCE_LIST),
                ClickFilter(board=self.game.buttons)
            )

            if self.button_clicked(click) == Button.OK.value:
                return
            if click.board is not self.game.mainBoard:
                continue
            square = click.board.get_square(click.pos)
            if not isinstance(square, Landscape):
                continue

            if square.player is self.opponent and square.resourcesHeld >= 1:
                opponentLandSelected = square
                selectedPos = click.pos

            if opponentLandSelected is not None and square.player is self and square.resourcesHeld < 3 and square.resource == opponentLandSelected.resource:
                opponentLandSelected.resourcesHeld -= 1
                square.resourcesHeld += 1
                self.game.mainBoard.refresh_square(selectedPos)
                self.game.mainBoard.refresh_square(click.pos)
                return


    def pick_any_resource(self) -> None:
        self.game.display.print_msg('pick a resource')
        while True:
            click = self.game.get_filtered_click(
                [ClickFilter(board=self.game.mainBoard, cardTypes=RESOURCE_LIST, player=self),
                ClickFilter(board=self.game.buttons)]
            )

            if self.button_clicked(click) == Button.CANCEL.value:
                return

            if click.board is not self.game.mainBoard:
                continue

            square = click.board.get_square(click.pos)
            if not isinstance(square, Landscape):
                continue

            if square.resourcesHeld >= 3:
                continue

            square.resourcesHeld += 1
            click.board.refresh_square(click.pos)
            return

    def wait_for_ok(self):
        while True:
            click = self.game.get_filtered_click()
            if self.button_clicked(click) == Button.OK.value:
                return


    def refill_hand(self) -> None:
        pass

    def throw_dice(self) -> None:
        self.game.display.print_msg('click to toss event dice')
        self.wait_for_ok()

        event: DiceEvent = self.game.throw_event_dice()
        print(f'event: {event}')
        self.game.handle_dice_events(event)

        self.game.display.print_msg('click to toss yield dice or use alchemist')
        self.wait_for_ok()
        diceNumber: int = self.game.throw_yield_dice()
        print(f'yield: {diceNumber}')

        self.game.land_yield(diceNumber)

    def clicked_card_equals(self, click: MouseClick, name: str) -> bool:
        square = click.board.get_square(click.pos)
        if square is None:
            return False
        return square.name == name

    def pay(self, cost: Cost) -> None:
        costToPay = copy.copy(cost)

        while not costToPay.is_zero():
            click = self.game.get_filtered_click(
                [ClickFilter(board=self.game.mainBoard, cardTypes=RESOURCE_LIST, player=self)]
            )

            card: Card = click.board.get_square(click.pos)
            if not isinstance(card, Landscape):
                continue
            if card.resourcesHeld > 0 and costToPay.get(card.resource) > 0:
                costToPay.take(card.resource)
                card.resourcesHeld -= 1
                self.game.mainBoard.refresh_square(click.pos)

    def buildPath(self) -> None:
        path = Path()
        if not self.can_cover_cost(path.cost):
            print('you cannot affort a path')
            return

        while True:
            click = self.game.get_filtered_click()
            card = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.CANCEL.value:
                return

            if card.name != 'empty' or not self.is_next_to_settlement(click.pos):
                continue

            self.game.mainBoard.set_square(click.pos, path)
            self.pay(path.cost)
            return



    def do_actions(self) -> None:
        while True:
            self.game.display.print_msg('do something')
            click = self.game.get_filtered_click()
            card = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.END_TURN.value:
                return

            elif click.board is self.game.mainBoard and card.name == 'back_path':
                self.buildPath()

            elif click.board is self.game.mainBoard and card.name == 'back_town':
                # build town
                pass

            elif click.board is self.game.mainBoard and card.name == 'back_village':
                # build village
                pass

            elif click.board is self.handBoard and isinstance(card, Playable):
                # use card from hand
                pass

            elif click.board is self.game.mainBoard and isinstance(card, Landscape) and card.player is self:
                # exchange goods
                pass

            elif click.board is self.game.mainBoard and isinstance(card, Playable):
                # take card back
                pass