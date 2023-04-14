from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Type
from enums import Button, DiceEvent, Resource
from player import Player
from util import Pos, MouseClick, ClickFilter, RESOURCE_LIST, Cost
from card import Landscape, Playable, Path, Card, Town, Village, Settlement, Action, Building

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

    def select_card_to_pay(self, cost: Optional[Cost]=None) -> Card:
        while True:
            click = self.game.get_filtered_click(
                [ClickFilter(board=self.game.mainBoard, cardNames=RESOURCE_LIST, player=self)]
            )
            card: Card = click.board.get_square(click.pos)
            if not isinstance(card, Landscape):
                continue

            if card.resourcesHeld > 0 and (cost is None or cost.get(card.resource) > 0):
                return card

    def get_new_card_position(self, infraType: Type[Village | Path | Town | Playable], townOnly=False) -> Optional[Pos]:
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
            elif infraType == Playable:
                if card.name == 'empty' and hasattr(card, 'settlement') and card.settlement.player is self:
                    if townOnly and isinstance(card.settlement, Village):
                        print('this card needs to be placed in a town')
                        continue
                    return click.pos
            else:
                raise ValueError(f'unknown infra type: {infraType}')


    def play_action_card(self, card: Action) -> None:
        pass

    def decide_browse_pile(self) -> bool:
        print('will you brose a pile?')
        while True:
            click = self.game.get_filtered_click()
            if self.button_clicked(click) == Button.OK.value:
                return True
            if self.button_clicked(click) == Button.CANCEL.value:
                return False

    def refill_hand(self) -> None:
        maxCardsInHand = self.get_hand_cards_cnt()
        if len(self.cardsInHand) < maxCardsInHand:
            while len(self.cardsInHand) < maxCardsInHand:
                pile = self.select_pile()
                payToBrowse = 1 if self.has_browse_discount() else 2
                if self.can_cover_cost(payToBrowse) and self.decide_browse_pile():
                    self.pay(payToBrowse)
                else:
                    self.cardsInHand.append(pile.pop())
                    self.refresh_hand_board()
        else:
            if len(self.cardsInHand) > maxCardsInHand:
                while len(self.cardsInHand) > maxCardsInHand:
                    idx = self.select_card_to_throw_away()
                    self.cardsInHand.pop(idx)
                    self.refresh_hand_board()
            if self.swap_one_card():
                idx = self.select_card_to_throw_away()
                self.cardsInHand.pop(idx)
                self.refresh_hand_board()
                self.refill_hand()

    def do_actions(self) -> None:
        while True:
            self.game.display.print_msg('do something')
            click = self.game.get_filtered_click()
            card = click.board.get_square(click.pos)

            if self.button_clicked(click) == Button.END_TURN.value:
                return
            elif click.board is self.game.mainBoard and card.name == 'back_path':
                self.build_infrastructure(Path)
            elif click.board is self.game.mainBoard and card.name == 'back_town':
                self.build_infrastructure(Town)
            elif click.board is self.game.mainBoard and card.name == 'back_village':
                self.build_infrastructure(Village)
            elif click.board is self.handBoard and isinstance(card, Playable):
                self.play_card_from_hand(card)
            elif click.board is self.game.mainBoard and isinstance(card, Landscape) and card.player is self:
                pass # exchange goods
            elif click.board is self.game.mainBoard and isinstance(card, Playable):
                pass  # take card back