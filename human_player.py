from __future__ import annotations
import copy
from typing import Optional, TYPE_CHECKING, Type
from enums import Button, DiceEvent
from player import Player
from util import Pos, MouseClick, ClickFilter, RESOURCE_LIST, Cost
from card import Landscape, Playable, Path, Card, Town, Village, Settlement, Action

if TYPE_CHECKING:
    from game import Game
    from board import Board
    from util import Pile


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
        self.game.display.print_msg('now you need to pay')
        costToPay = copy.copy(cost)

        while not costToPay.is_zero():
            click = self.game.get_filtered_click(
                [ClickFilter(board=self.game.mainBoard, cardNames=RESOURCE_LIST, player=self)]
            )

            card: Card = click.board.get_square(click.pos)
            if not isinstance(card, Landscape):
                continue
            if card.resourcesHeld > 0 and costToPay.get(card.resource) > 0:
                costToPay.take(card.resource)
                card.resourcesHeld -= 1
                self.game.mainBoard.refresh_square(click.pos)

    def get_new_infra_position(self, infraType: Type[Village | Path | Town]) -> Optional[Pos]:
        while True:
            click = self.game.get_filtered_click()
            card = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.CANCEL.value:
                return None

            if infraType == Village:
                if card.name == 'empty' and click.pos.y == self.midPos.y and self.is_next_to(click.pos, Path):
                    return click.pos
            elif infraType == Town:
                if card.name == 'village' and card.player is self:
                    return click.pos
            elif infraType == Path:
                if card.name == 'empty' and click.pos.y == self.midPos.y and self.is_next_to(click.pos, Settlement):
                    return click.pos
            else:
                raise ValueError(f'unknown infra type: {infraType}')


    def play_action_card(self, card: Action) -> None:
        pass

    def play_card_from_hand(self, card: Playable) -> None:
        if isinstance(card, Action):
            self.play_action_card(card)
            return

        if not self.can_cover_cost(card.cost):
            return

        while True:
            click = self.game.get_filtered_click()
            emptyCard = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.CANCEL.value:
                return

            if emptyCard.name != 'empty' or not hasattr(emptyCard, 'settlement') or emptyCard.settlement.player is not self:
                continue

            self.game.mainBoard.set_square(click.pos, card)
            self.cardsInHand.remove(card)
            self.refresh_hand_board()
            self.pay(card.cost)
            return

    def refill_hand(self) -> None:
        maxCardsInHand = self.get_hand_cards_cnt()
        while len(self.cardsInHand) != maxCardsInHand:
            if len(self.cardsInHand) > maxCardsInHand:
                click = self.game.get_filtered_click(ClickFilter(board=self.handBoard))
            else:
                self.select_pile()

                # pick a pile or pay resources


    def do_actions(self) -> None:
        while True:
            self.game.display.print_msg('do something')
            click = self.game.get_filtered_click()
            card = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.END_TURN.value:
                return
            elif click.board is self.game.mainBoard and card.name == 'back_path':
                self.build_path()
            elif click.board is self.game.mainBoard and card.name == 'back_town':
                self.build_town()
            elif click.board is self.game.mainBoard and card.name == 'back_village':
                self.build_village()
            elif click.board is self.handBoard and isinstance(card, Playable):
                self.play_card_from_hand(card)
            elif click.board is self.game.mainBoard and isinstance(card, Landscape) and card.player is self:
                pass # exchange goods
            elif click.board is self.game.mainBoard and isinstance(card, Playable):
                pass  # take card back