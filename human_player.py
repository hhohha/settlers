from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Type, Tuple

from click_filter import ClickFilter
from config import MAX_LAND_RESOURCES
from custom_types import Pile
from enums import Button, DiceEvent, Resource
from player import Player
from util import Pos, MouseClick, Cost, is_next_to, display_cards_on_board
from card import Landscape, Playable, Path, Town, Village, Settlement, Action, SettlementSlot, Buildable, Knight, Fleet, \
    Building

if TYPE_CHECKING:
    from game import Game
    from board import Board


class HumanPlayer(Player):
    def __init__(self, game: Game, handBoard: Board, number: int, midPos: Pos):
        super().__init__(game, handBoard, number, True, midPos)

    def __str__(self) -> str:
        return 'human'

    __repr__ = __str__

    def _get_filtered_click(self, clickFilter: Tuple[ClickFilter, ...] | ClickFilter) -> MouseClick:
        while True:
            click: MouseClick = self.game.display.get_mouse_click()
            if isinstance(clickFilter, ClickFilter) and clickFilter.accepts(click):
                    return click
            else:
                for f in clickFilter:
                    if f.accepts(click):
                        return click

    def _button_clicked(self, click: MouseClick) -> int:
        board, square = click.tuple()
        if board is not self.game.buttons:
            return Button.NO_BUTTON.value

        return square.x + square.y * self.game.buttons.size.x

    def initial_land_setup(self) -> None:
        landSelected: Optional[Landscape] = None
        self.game.display.print_msg('setup land cards')

        while True:
            click = self._get_filtered_click((
                ClickFilter(board=self.game.mainBoard, cardType=Landscape, player=self),
                ClickFilter(board=self.game.buttons)
            ))

            if self._button_clicked(click) == Button.OK.value:
                # ok button - we're done
                return
            elif self._button_clicked(click) == Button.CANCEL.value:
                # cancel button - clears previous selection
                landSelected = None
                continue
            elif self._button_clicked(click) != Button.NO_BUTTON.value:
                # different button was clicked - that does nothing
                continue

            # now it's clear that button has not been clicked, so it must have been landscape
            land = click.board.get_square(click.pos)
            assert isinstance(land, Landscape) and land.pos is not None

            if landSelected is None:
                landSelected = land
            else:
                click.board.set_square(land.pos, landSelected)
                click.board.set_square(landSelected.pos, land)
                landSelected = None

    def select_pile(self, unavailablePile: Optional[Pile]=None) -> Pile:
        self.game.display.print_msg('select a pile')

        while True:
            board, pos = self._get_filtered_click(ClickFilter(
                board=self.game.mainBoard,
                cardName='back'
            )).tuple()

            pileIdx = pos.x - board.size.x + len(self.game.cardPiles)
            if self.game.cardPiles[pileIdx] is unavailablePile:
                print('this pile is already chosen, select another')
                continue
            return self.game.cardPiles[pileIdx]

    def select_card_from_choice(self, pile: Pile) -> Playable:
        if self.cardsVisible:
            display_cards_on_board(pile, self.game.choiceBoard)

        click: MouseClick = self._get_filtered_click(ClickFilter(
            board=self.game.choiceBoard,
            cardType=Playable
        ))

        card = click.board.get_square(click.pos)
        assert isinstance(card, Playable), 'invalid card in choice'
        return card

    def select_resource_to_trade_for(self) -> Optional[Resource]:
        while True:
            click = self._get_filtered_click((
                ClickFilter(player=self, cardType=Landscape),
                ClickFilter(board=self.game.buttons)
            ))

            if click.board is self.game.buttons:
                if self._button_clicked(click) == Button.CANCEL.value:
                    return None
                else:
                    continue

        card = click.board.get_square(click.pos)
        assert isinstance(card, Landscape), f'expected Landscape'

        return card.resource

    def select_resource_to_purchase(self) -> Landscape:
        while True:
            click = self._get_filtered_click(ClickFilter(
                player=self,
                cardType=Landscape
            ))

            card = click.board.get_square(click.pos)
            assert isinstance(card, Landscape), f'expected Landscape'

            if card.resourcesHeld >= MAX_LAND_RESOURCES:
                continue

        return card

    def pick_starting_cards(self) -> None:
        pile = self.select_pile()
        self.game.display.print_msg('select cards')
        while len(self.cardsInHand) < self.cardsInHandDefaultCnt:
            self.get_card_from_choice(pile)
        self.game.choiceBoard.clear()

    def give_any_resource(self) -> None:
        # used only as second step by trader action card and thus should always be possible
        # TODO - maybe add a check anyway
        self.game.display.print_msg('give a resource')
        ownLandSelected: Optional[Landscape] = None

        while True:
            click = self._get_filtered_click(ClickFilter(
                board=self.game.mainBoard,
                cardType=Landscape
            ))

            square = click.board.get_square(click.pos)
            assert isinstance(square, Landscape), f'expected to select a resource'

            if square.player is self and square.resourcesHeld >= 1:
                ownLandSelected = square

            if ownLandSelected is not None and square.player is self.opponent and square.resourcesHeld < MAX_LAND_RESOURCES and square.resource == ownLandSelected.resource:
                ownLandSelected.resourcesHeld -= 1
                square.resourcesHeld += 1
                assert ownLandSelected.pos is not None
                self.game.mainBoard.refresh_square(ownLandSelected.pos)
                self.game.mainBoard.refresh_square(click.pos)
                return

    def grab_any_resource_if_possible(self) -> None:
        if not self.can_grab_resource_from_opponent():
            print('sadly, no resource can be grabbed')
            return

        self.game.display.print_msg('grab a resource')
        opponentLandSelected: Optional[Landscape] = None

        while True:
            click = self._get_filtered_click(ClickFilter(
                board=self.game.mainBoard,
                cardType=Landscape
            ))

            square = click.board.get_square(click.pos)
            assert isinstance(square, Landscape), f'unexpected card grabbed'

            if square.player is self.opponent and square.resourcesHeld >= 1:
                opponentLandSelected = square

            if opponentLandSelected is not None and square.player is self and square.resourcesHeld < MAX_LAND_RESOURCES and square.resource == opponentLandSelected.resource:
                opponentLandSelected.resourcesHeld -= 1
                square.resourcesHeld += 1
                assert opponentLandSelected.pos is not None
                self.game.mainBoard.refresh_square(opponentLandSelected.pos)
                self.game.mainBoard.refresh_square(click.pos)
                return


    def pick_any_resource(self) -> None:
        self.game.display.print_msg('pick a resource')
        while True:
            click = self._get_filtered_click((
                ClickFilter(board=self.game.mainBoard, cardType=Landscape, player=self),
                ClickFilter(board=self.game.buttons)
            ))

            if self._button_clicked(click) == Button.CANCEL.value:
                return

            if click.board is not self.game.mainBoard:
                continue

            square = click.board.get_square(click.pos)
            if not isinstance(square, Landscape):
                continue

            if square.resourcesHeld >= MAX_LAND_RESOURCES:
                continue

            square.resourcesHeld += 1
            click.board.refresh_square(click.pos)
            return

    def wait_for_ok(self):
        while True:
            click = self._get_filtered_click(ClickFilter(board=self.game.buttons))
            if self._button_clicked(click) == Button.OK.value:
                return

    def decide_use_defence(self, againstCard: str) -> bool:
        self.game.display.print_msg(f'will you defend against {againstCard}?')
        return self.ok_or_cancel()

    def select_card_to_steal_by_spy(self) -> Knight | Fleet | Action:
        click = self._get_filtered_click(ClickFilter(
            board=self.game.choiceBoard,
            cardType=(Fleet, Knight, Action)
        ))
        unit = click.board.get_square(click.pos)
        assert isinstance(unit, (Knight, Fleet)), f'spy attempted to steel a card of type {type(unit)}'
        return unit

    def decide_dice_or_alchemist(self) -> bool:
        return self.ok_or_cancel()

    def use_alchemist(self) -> int:
        self.game.display.print_msg('choose yield')
        click = self._get_filtered_click(ClickFilter(board=self.game.buttons))

        self.remove_action_card('alchemist')
        return self.game.buttons.to_int(click.pos) + 1

    def decide_use_scout(self) -> bool:
        self.game.display.print_msg('will you use scout?')
        return self.ok_or_cancel()

    def select_new_land(self) -> Landscape:
        display_cards_on_board(self.game.landscapeCards, self.game.choiceBoard)

        click = self._get_filtered_click(ClickFilter(
            board=self.game.choiceBoard,
            cardType=Landscape
        ))

        land = click.board.get_square(click.pos)
        assert isinstance(land, Landscape), f'expected landscape'

        return land

    def throw_dice(self) -> None:
        self.game.display.print_msg('click to toss event dice')
        self.wait_for_ok()

        event: DiceEvent = self.game.throw_event_dice()
        print(f'event: {event}')
        self.game.handle_dice_events(event)

        diceNumber: int
        if 'alchemist' in map(lambda x: x.name, self.cardsInHand):
            self.game.display.print_msg('click to toss yield dice or use alchemist')
            tossDice = self.decide_dice_or_alchemist()
            if not tossDice:
                self.wait_for_ok()
                diceNumber = self.game.throw_yield_dice()
            else:
                diceNumber = self.use_alchemist()
        else:
            self.game.display.print_msg('click to toss yield dice')
            self.wait_for_ok()
            diceNumber = self.game.throw_yield_dice()

        print(f'yield: {diceNumber}')

        self.game.land_yield(diceNumber)

    def select_card_to_pay(self, cost: Optional[Cost]=None) -> Landscape:
        self.game.display.print_msg('select card to pay')
        while True:
            click = self._get_filtered_click(ClickFilter(
                board=self.game.mainBoard,
                cardType=Landscape,
                player=self
            ))
            card = click.board.get_square(click.pos)
            if not isinstance(card, Landscape):
                continue

            if card.resourcesHeld > 0 and (cost is None or cost.get(card.resource) > 0):
                return card

    def select_new_card_position(self, infraType: Type[Village | Path | Town | Buildable], townOnly=False) -> Optional[Pos]:
        self.game.display.print_msg('choose card location')
        while True:
            click = self._get_filtered_click((
              ClickFilter(board=self.game.mainBoard),
              ClickFilter(board=self.game.buttons)
            ))
            card = click.board.get_square(click.pos)
            if card is None:
                continue

            if self._button_clicked(click) == Button.CANCEL.value:
                return None

            if infraType == Village:
                if card.name == 'empty' and click.pos.y == self.midPos.y and is_next_to(self.game.mainBoard, click.pos, Path):
                    return click.pos
            elif infraType == Town:
                if isinstance(card, Village) and card.player is self:
                    return click.pos
            elif infraType == Path:
                if card.name == 'empty' and click.pos.y == self.midPos.y and is_next_to(self.game.mainBoard, click.pos, Settlement):
                    return click.pos
            elif infraType == Buildable:
                if isinstance(card, SettlementSlot) and card.settlement is not None and card.settlement.player is self:
                    if townOnly and isinstance(card.settlement, Village):
                        print('this card needs to be placed in a town')
                        continue
                    return click.pos
            else:
                raise ValueError(f'unknown infra type: {infraType}')

    def select_opponents_unit_to_remove(self) -> Knight | Fleet:
        self.game.display.print_msg('select opponents knight or fleet to remove')
        while True:
            card = self._get_filtered_click((
                ClickFilter(board=self.game.mainBoard, player=self.opponent, cardType=Knight),
                ClickFilter(board=self.game.mainBoard, player=self.opponent, cardType=Fleet)
            ))
            assert isinstance(card, (Knight, Fleet))
            if not self.game.is_protected_from_civil_war(card):
                return card

    def decide_swap_one_card(self) -> bool:
        self.game.display.print_msg('will you swap one card?')
        return self.ok_or_cancel()

    def decide_browse_pile(self) -> bool:
        self.game.display.print_msg('will you browse a pile?')
        return self.ok_or_cancel()

    def select_card_to_throw_away(self) -> Playable:
        self.game.display.print_msg('select card to throw away')
        click = self._get_filtered_click(ClickFilter(board=self.handBoard))
        card = click.board.get_square(click.pos)
        assert isinstance(card, Playable), 'wrong card type in hand'
        return card

    def select_building_to_burn(self) -> Building:
        click = self._get_filtered_click(ClickFilter(
            board=self.game.mainBoard,
            player=self.opponent,
            cardType=Building
        ))

        card = click.board.get_square(click.pos)
        assert isinstance(card, Building), f'selected card cannot be burnt: {card}'
        return card

    def select_knight_to_kill(self) -> Knight:
        click = self._get_filtered_click(ClickFilter(
            board=self.game.mainBoard,
            player=self.opponent,
            cardType=Knight
        ))

        card = click.board.get_square(click.pos)
        assert isinstance(card, Knight), f'selected card cannot be killed: {card}'
        return card

    def select_opponents_card_to_discard(self) -> Playable:
        click = self._get_filtered_click(ClickFilter(
            board=self.game.choiceBoard,
            cardType=Playable
        ))
        card = click.board.get_square(click.pos)
        assert isinstance(card, Playable), f'choice board has invalid content'
        return card

    def trade_with_caravan(self) -> None:
        while True:
            self.game.display.print_msg('select a resource to get')
            click = self._get_filtered_click(ClickFilter(
                player=self,
                cardType=Landscape
            ))

            landToGet = click.board.get_square(click.pos)
            assert isinstance(landToGet, Landscape), f'expected Landscape'
            if landToGet.resourcesHeld >= MAX_LAND_RESOURCES:
                continue

            self.game.display.print_msg('select a resource to pay with')
            click = self._get_filtered_click(ClickFilter(
                player=self,
                cardType=Landscape
            ))

            landToPay = click.board.get_square(click.pos)
            assert isinstance(landToPay, Landscape), f'expected Landscape'
            if landToPay.resourcesHeld < 1:
                continue

            landToGet.resourcesHeld += 1
            landToPay.resourcesHeld -= 1

            assert landToPay.pos is not None and landToGet.pos is not None
            self.game.mainBoard.refresh_square(landToPay.pos)
            self.game.mainBoard.refresh_square(landToGet.pos)

    def ok_or_cancel(self) -> bool:
        while True:
            click = self._get_filtered_click(ClickFilter(board=self.game.buttons))
            if self._button_clicked(click) == Button.OK.value:
                return True
            if self._button_clicked(click) == Button.CANCEL.value:
                return False

    def do_actions(self) -> None:
        while True:
            self.game.display.print_msg('do something')
            click = self._get_filtered_click((
                ClickFilter(board=self.game.mainBoard),
                ClickFilter(board=self.game.buttons),
                ClickFilter(board=self.handBoard)
            ))
            card = click.board.get_square(click.pos)
            if card is None:
                continue

            if self._button_clicked(click) == Button.END_TURN.value:
                return
            elif click.board is self.game.mainBoard and card.name == 'back_path':
                self.build_infrastructure(Path)
            elif click.board is self.game.mainBoard and card.name == 'back_town':
                self.build_infrastructure(Town)
            elif click.board is self.game.mainBoard and card.name == 'back_village':
                self.build_infrastructure(Village)
            elif click.board is self.handBoard and isinstance(card, Playable):
                self.play_card_from_hand(card)
            elif self._button_clicked(click) == Button.TRADE.value:
                self.trade()
            elif click.board is self.game.mainBoard and isinstance(card, Playable):
                pass  # take card back
