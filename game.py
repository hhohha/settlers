import random
from typing import List, Optional, Type, Tuple, TYPE_CHECKING
from board import Board
from computer_player import ComputerPlayer
from display_handler import DisplayHandler
from enums import ActionType, DiceEvent, EventCardType, GameStage, Button
from card_data import CardData
from human_player import HumanPlayer
import config
from util import DiceEvents, Pos, MouseClick, Pile
from card import Card, Event, Landscape, Village, Town, Path, MetaCard, Playable

class Game:
    def __init__(self):
        self.eventCards = []

        self.mainBoard: Board = Board(Pos(*config.MAIN_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player1Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player2Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.bigCard = Board(Pos(1, 1), Pos(*config.CARD_IMG_SIZE_BIG))
        self.buttons = Board(Pos(*config.BUTTON_BOARD_SQUARES), Pos(*config.BUTTON_SIZE))

        self.player1 = HumanPlayer(self, self.player1Board, 1)
        self.player2 = ComputerPlayer(self, self.player2Board, 2)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

        self.yieldDice: Optional[int] = None

        self.display = DisplayHandler()
        self.display.add_board(self.mainBoard)
        self.display.add_board(self.player1Board)
        self.display.add_board(self.player2Board)
        self.display.add_board(self.choiceBoard)
        self.display.add_board(self.bigCard)
        self.display.add_board(self.buttons)

        self.cardPiles: List[Pile] = [[] for _ in range(config.PILE_COUNT)]
        self.pileSelected: Optional[List[Card]] = None
        self.cardSelected: Optional[Card] = None

        self.eventCards: List[Event] = CardData.create_event_cards()
        self.landscapeCards: List[Landscape] = []
        self.infraCardsLeft = {
            Village: config.VILLAGES_COUNT,
            Path: config.PATHS_COUNT,
            Town: config.TOWNS_COUNT
        }

        self.paths: int = config.PATHS_COUNT
        self.villages: int = config.VILLAGES_COUNT
        self.towns: int = config.TOWNS_COUNT

        self.setup_landscape_cards()
        self.setup_playable_cards()
        self.init_main_board()

        self.player1Board.fill_board(MetaCard('empty'))
        self.player2Board.fill_board(MetaCard('empty'))
        self.choiceBoard.fill_board(MetaCard('empty'))
        self.bigCard.fill_board(MetaCard('empty'))
        self.buttons.fill_board(MetaCard('empty'))

    def create_infra_card(self, cardType: Type[Village | Path | Town]):
        if self.infraCardsLeft[cardType] > 0:
            self.infraCardsLeft[cardType] -= 1
            return cardType()
        else:
            raise ValueError(f'cannot create more infra cards of type: {cardType}')

    def init_main_board(self):
        for pos in (Pos(x, y) for x in range(self.mainBoard.size.x) for y in range(self.mainBoard.size.y)):
            self.mainBoard.set_square(pos, MetaCard('empty'))

        self.mainBoard.set_square(Pos(6, 8), self.create_infra_card(Path))
        self.mainBoard.set_square(Pos(7, 8), self.create_infra_card(Village))
        self.mainBoard.set_square(Pos(5, 8), self.create_infra_card(Village))

        for lCard, pos in zip(self.player1.landscapeCards,
                              [Pos(4, 9), Pos(6, 9), Pos(8, 9), Pos(4, 7), Pos(6, 7), Pos(8, 7)]):
            self.mainBoard.set_square(pos, lCard)

        self.mainBoard.set_square(Pos(0, 5), MetaCard('back_event'))
        self.mainBoard.set_square(Pos(1, 5), MetaCard('back_land'))
        self.mainBoard.set_square(Pos(2, 5), MetaCard('back_path'))
        self.mainBoard.set_square(Pos(3, 5), MetaCard('back_village'))
        self.mainBoard.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(8, 13):
            self.mainBoard.set_square(Pos(x, 5), MetaCard('back'))  # TODO - set this up relative to right side

    def setup_landscape_cards(self):
        for card in CardData.create_landscape_cards(self.player1, self.player2):
            if card.player is None:
                self.landscapeCards.append(card)
            else:
                #card.player.landscapeCards.append(card)
                card.player.landscapeCards[card] = None

    def setup_playable_cards(self) -> None:
        cards: List[Playable] = CardData.create_playable_cards()
        pileSize = len(cards) // len(self.cardPiles)
        extraCards = len(cards) % len(self.cardPiles)
        startIdx, endIdx = 0, pileSize

        for idx, _ in enumerate(self.cardPiles):
            if extraCards > 0:
                extraCards -= 1
                endIdx += 1
            self.cardPiles[idx] = cards[startIdx:endIdx]
            startIdx = endIdx
            endIdx += pileSize

    def is_victory(self) -> bool:
        return self.player1.victoryPoints >= config.VICTORY_POINTS or self.player2.victoryPoints >= config.VICTORY_POINTS

    def event_tournament(self) -> None:
        player1Strength = self.player1.get_tournament_strength()
        player2Strength = self.player1.get_tournament_strength()

        if player1Strength > player2Strength:
            self.player1.pick_any_resource()
        elif player1Strength < player2Strength:
            self.player2.pick_any_resource()

    def event_trade_profit(self) -> None:
        player1Profit = self.player1.get_trade_strength()
        player2Profit = self.player1.get_trade_strength()

        if player1Profit > player2Profit:
            self.player1.grab_any_resource()
        elif player1Profit < player2Profit:
            self.player2.grab_any_resource()

    def event_good_harvest(self) -> None:
        self.player1.pick_any_resource()
        self.player2.pick_any_resource()

    def handle_dice_events(self, event: DiceEvent):
        if event == DiceEvent.TOURNAMENT:
            self.event_tournament()
        elif event == DiceEvent.TRADE_PROFIT:
            self.event_trade_profit()
        elif event == DiceEvent.AMBUSH:
            pass
        elif event == DiceEvent.GOOD_HARVEST:
            self.event_good_harvest()
        elif event == DiceEvent.CARD_EVENT:
            pass
        else:
            raise ValueError(f'unknown dice event: {event}')

    def handle_card_event(self, event: EventCardType):
        if event == EventCardType.BUILDER:
            pass
        elif event == EventCardType.CIVIL_WAR:
            pass
        elif event == EventCardType.RICH_YEAR:
            pass
        elif event == EventCardType.ADVANCE:
            pass
        elif event == EventCardType.NEW_YEAR:
            pass
        elif event == EventCardType.CONFLICT:
            pass
        elif event == EventCardType.PLAQUE:
            pass
        else:
            raise ValueError(f'unknown card event: {event}')

    def initial_land_setup_computer(self):
        pass

    def select_card(self, card: Card):
        self.bigCard.set_square(Pos(0, 0), card)

    def display_cards_for_choice(self, pile: Pile) -> None:
        self.choiceBoard.clear()
        for card in pile:
            self.choiceBoard.set_next_square(card)

    def throw_yield_dice(self) -> None:
        self.yieldDice = random.randint(1, 6)

    def throw_event_dice(self) -> DiceEvent:
        return DiceEvents[random.randint(1, 6)]

    def play(self):
        for player in [self.player1, self.player2]:
            player.initial_land_setup()

        for player in [self.player1, self.player2]:
            player.pick_starting_cards()

        while not self.is_victory():
            for player in [self.player1, self.player2]:
                player.throw_dice()
                player.do_actions()
                for p in [self.player1, self.player2]:
                    p.refill_hand()

        self.display.get_mouse_click()

