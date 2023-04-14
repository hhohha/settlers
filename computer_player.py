from __future__ import annotations
from typing import TYPE_CHECKING, Set, Optional, Type

from card import Town, Path, Village, Playable, Action, Landscape
from enums import Resource
from player import Player

if TYPE_CHECKING:
    from game import Game
    from util import Pile, Pos, Cost
    from board import Board

class ComputerPlayer(Player):
    def __init__(self, game: Game, handBoard: Board, number: int, midPos: Pos):
        super().__init__(game, handBoard, number, False, midPos)

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
        # TODO - setup card priority
        pile = self.selectPile()
        while len(self.cardsInHand) < self.cardsInHandCnt:
            self.add_card(pile.pop())
        self.refresh_hand_board()

    def throw_dice(self) -> None:
        print('opponent throwing dice')
        event = self.game.throw_event_dice()
        print(f'event: {event}')
        self.game.handle_dice_events(event)
        diceNumber = self.game.throw_yield_dice()
        print(f'yield: {diceNumber}')
        self.game.land_yield(diceNumber)

    def get_new_village_position(self) -> Optional[Pos]:
        pass

    def pay(self, cost: Cost | int) -> None:
        pass

    def do_actions(self) -> None:
        pass

    def refill_hand(self) -> None:
        # TODO - improve, obviously
        pile = self.selectPile()
        while len(self.cardsInHand) < self.cardsInHandCnt:
            self.add_card(pile.pop())
        self.refresh_hand_board()

    def get_new_infra_position(self, infraType: Type[Village | Town | Path]) -> Optional[Pos]:
        pass

    def grab_any_resource(self) -> None:
        # TODO - improve, currently it gets anything available
        for opponentLand in self.opponent.landscapeCards:
            if opponentLand.resourcesHeld > 0:
                for myLand in self.landscapeCards:
                    if myLand.resource == opponentLand.resource and myLand.resourcesHeld < 3:
                        opponentLand -= 1
                        myLand += 1
                        self.game.mainBoard.refresh_square(self.landscapeCards[myLand])
                        self.game.mainBoard.refresh_square(self.opponent.landscapeCards[opponentLand])
                        return

    def pick_any_resource(self) -> None:
        # TODO - improve
        for land in self.landscapeCards:
            if land.resourcesHeld < 3:
                land.resourcesHeld += 1
                self.game.mainBoard.refresh_square(self.landscapeCards[land])
                return

    def decide_browse_pile(self) -> bool:
        return False

    def get_new_card_position(self, infraType: Type[Village | Path | Town | Playable], townOnly=False) -> Optional[Pos]:
        return None

    def play_action_card(self, card: Action) -> None:
        pass

    def select_card_to_pay(self, resource: Optional[Resource]) -> Landscape:
        pass

    def select_pile(self) -> Pile:
        return self.game.cardPiles[0]

    def swap_one_card(self) -> bool:
        return False

    def select_card_to_throw_away(self) -> int:
        return 0