import random
from typing import List, Optional, Type, Tuple, TYPE_CHECKING
from board import Board
from display_handler import DisplayHandler
from enums import ActionType, DiceEvent, EventCardType, GameStage, Button
from card_data import CardData
from player import Player
import config
from util import DiceEvents, Pos, MouseClick
from card import Card, Event, Landscape, Village, Town, Path, MetaCard, Playable

Pile = List[Playable]

class Game:
    def __init__(self):
        self.eventCards = []
        self.humanPlayer = Player(self, 1)
        self.computerPlayer = Player(self, 2)

        self.board: Board = Board(Pos(*config.MAIN_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.handBoard = Board(Pos(*config.HAND_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.bigCard = Board(Pos(1, 1), Pos(*config.CARD_IMG_SIZE_BIG))
        self.buttons = Board(Pos(*config.BUTTON_BOARD_SQUARES), Pos(*config.BUTTON_SIZE))

        self.display = DisplayHandler()
        self.display.add_board(self.board)
        self.display.add_board(self.handBoard)
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
        self.mouseClicks: List[MouseClick] = []
        self.stage: GameStage = GameStage.NONE

        self.paths: int = config.PATHS_COUNT
        self.villages: int = config.VILLAGES_COUNT
        self.towns: int = config.TOWNS_COUNT

        self.setup_landscape_cards()
        self.setup_playable_cards()
        self.init_main_board()
        self.init_hand_board()
        self.init_choice_board()
        self.init_big_card()
        self.init_buttons()

    def button_clicked(self, click: MouseClick) -> int:
        board, square = click.tuple()
        if board is not self.buttons:
            return Button.NO_BUTTON.value

        return square.x + square.y * self.buttons.size.x

    def create_infra_card(self, cardType: Type[Village | Path | Town]):
        if self.infraCardsLeft[cardType] > 0:
            self.infraCardsLeft[cardType] -= 1
            return cardType()
        else:
            raise ValueError(f'cannot create more infra cards of type: {cardType}')

    def init_big_card(self):
        self.bigCard.set_square(Pos(0, 0), MetaCard('empty'))

    def init_buttons(self):
        for pos in (Pos(x, y) for x in range(self.buttons.size.x) for y in range(self.buttons.size.y)):
            self.buttons.set_square(pos, MetaCard('empty'))

    def init_hand_board(self):
        for pos in (Pos(x, y) for x in range(self.handBoard.size.x) for y in range(self.handBoard.size.y)):
            self.handBoard.set_square(pos, MetaCard('empty'))

    def init_choice_board(self):
        for pos in (Pos(x, y) for x in range(self.choiceBoard.size.x) for y in range(self.choiceBoard.size.y)):
            self.choiceBoard.set_square(pos, MetaCard('empty'))

    def init_main_board(self):
        for pos in (Pos(x, y) for x in range(self.board.size.x) for y in range(self.board.size.y)):
            self.board.set_square(pos, MetaCard('empty'))

        self.board.set_square(Pos(6, 8), self.create_infra_card(Path))
        self.board.set_square(Pos(7, 8), self.create_infra_card(Village))
        self.board.set_square(Pos(5, 8), self.create_infra_card(Village))
        for lCard, pos in zip(self.humanPlayer.landscapeCards, [Pos(4, 9), Pos(6, 9), Pos(8, 9), Pos(4, 7), Pos(6, 7), Pos(8, 7)]):
            self.board.set_square(pos, lCard)

        self.board.set_square(Pos(0, 5), MetaCard('back_event'))
        self.board.set_square(Pos(1, 5), MetaCard('back_land'))
        self.board.set_square(Pos(2, 5), MetaCard('back_path'))
        self.board.set_square(Pos(3, 5), MetaCard('back_village'))
        self.board.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(8, 13):
            self.board.set_square(Pos(x, 5), MetaCard('back')) # TODO - set this up relative to right side

    def setup_landscape_cards(self):
        for card in CardData.create_landscape_cards(self.humanPlayer, self.computerPlayer):
            if card.player is None:
                self.landscapeCards.append(card)
            else:
                card.player.landscapeCards.append(card)

    def setup_playable_cards(self) -> None:
        cards: List[Card] = CardData.create_playable_cards()
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
        return self.humanPlayer.victoryPoints >= config.VICTORY_POINTS or self.computerPlayer.victoryPoints >= config.VICTORY_POINTS

    def handle_dice_events(self, event: DiceEvents):
        if event == DiceEvent.TOURNAMENT:
            pass
        elif event == DiceEvent.TRADE_PROFIT:
            pass
        elif event == DiceEvent.AMBUSH:
            pass
        elif event == DiceEvent.GOOD_HARVEST:
            pass
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

    def turn(self):
        diceNumber = random.randint(1, 6)
        event = DiceEvents[random.randint(1, 6)]

        self.handle_dice_events(event)
        self.add_resources(diceNumber)

        while True:
            action = self.humanPlayer.get_action()
            if action.actionType == ActionType.END_TURN:
                break

        self.settle_card_counts(self.humanPlayer)
        self.settle_card_counts(self.computerPlayer)

    def initial_land_setup_computer(self):
        pass

    def initial_land_setup_player(self) -> None:
        while True:
            self.mouseClicks.append(self.display.get_mouse_click())

            if self.button_clicked(self.mouseClicks[-1]) == Button.OK.value:
                self.mouseClicks.clear()
                return

            if len(self.mouseClicks) < 2:
                continue

            board1, pos1 = self.mouseClicks[-1].tuple()
            board2, pos2 = self.mouseClicks[-2].tuple()

            if board1 is not self.board or board2 is not self.board:
                continue

            card1, card2 = self.board.get_square(pos1), self.board.get_square(pos2)
            if isinstance(card1, Landscape) and isinstance(card2, Landscape) and card1.player is self.humanPlayer and card2.player is self.humanPlayer:
                self.board.set_square(pos1, card2)
                self.board.set_square(pos2, card1)
                self.mouseClicks.clear()

    def select_card(self, card: Card):
        self.bigCard.set_square(Pos(0, 0), card)


    def display_cards_for_choice(self, pile: Pile) -> None:
        self.init_choice_board()
        for card in pile:
           self.choiceBoard.set_next_square(card)

    def display_hand_cards(self):
        self.init_hand_board()
        for card in self.humanPlayer.cardsInHand:
            self.handBoard.set_next_square(card)

    def get_card_from_choice(self, pile: Pile) -> None:
        self.display_cards_for_choice(pile)
        while True:
            board, pos = self.display.get_mouse_click().tuple()
            if board is self.choiceBoard and self.choiceBoard.get_square(pos).name != 'empty':
                self.mouseClicks.clear()
                break

        cardIdx = pos.x + self.choiceBoard.size.x * pos.y
        card = pile[cardIdx]
        self.select_card(card)

        click = self.display.get_mouse_click()
        if self.button_clicked(click) == Button.OK:
            self.humanPlayer.add_card(card)
            self.handBoard.set_next_square(card)
            pile.pop(cardIdx)

    def pick_starting_cards_player(self) -> None:
        pile = self.select_pile()
        for _ in range(self.humanPlayer.cardsInHandCnt):
            self.get_card_from_choice(pile)

    def pick_starting_cards_computer(self) -> None:
        pass

    def select_pile(self) -> Pile:
        while True:
            self.mouseClicks.append(self.display.get_mouse_click())

            if not self.mouseClicks:
                continue

            board, pos = self.mouseClicks[-1].tuple()
            if board is not self.board or self.board.get_square(pos).name != 'back':
                continue

            pileIdx = pos.x - board.size.x + len(self.cardPiles)
            return self.cardPiles[pileIdx]

    def play(self):
        self.initial_land_setup_player()
        self.initial_land_setup_computer()

        self.pick_starting_cards_player()
        self.pick_starting_cards_computer()

        print('game ended successfully')
