from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type
from card import Town, Path, Village, Playable, Action, Landscape
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

    def get_new_infra_position(self, infraType: Type[Village | Town | Path]) -> Optional[Pos]:
        pass

    def grab_any_resource(self) -> None:
        # TODO - improve, currently it gets anything available
        assert self.opponent is not None
        for opponentLand in self.opponent.landscapeCards:
            if opponentLand.resourcesHeld > 0:
                for myLand in self.landscapeCards:
                    if myLand.resource == opponentLand.resource and myLand.resourcesHeld < 3:
                        opponentLand.resourcesHeld -= 1
                        myLand.resourcesHeld += 1
                        assert myLand.pos is not None and opponentLand.pos is not None
                        self.game.mainBoard.refresh_square(myLand.pos)
                        self.game.mainBoard.refresh_square(opponentLand.pos)
                        return

    def pick_any_resource(self) -> None:
        # TODO - improve
        for land in self.landscapeCards:
            if land.resourcesHeld < 3:
                land.resourcesHeld += 1
                assert land.pos is not None
                self.game.mainBoard.refresh_square(land.pos)
                return

    def decide_browse_pile(self) -> bool:
        return False

    def get_new_card_position(self, infraType: Type[Village | Path | Town | Playable], townOnly=False) -> Optional[Pos]:
        return None

    def play_action_card(self, card: Action) -> None:
        pass

    def select_card_to_pay(self, resource: Optional[Cost]) -> Landscape:
        pass

    def select_pile(self) -> Pile:
        return self.game.cardPiles[0]

    def swap_one_card(self) -> bool:
        return False

    def select_card_to_throw_away(self) -> int:
        return 0

    def get_card_from_choice(self, pile: Pile) -> None:
        pass