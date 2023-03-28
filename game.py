import random
from typing import List, Optional, Type, Tuple

from board import Board
from card import Card, Fleet, Knight, Building, Action, Event, Landscape, Village, Town, Path, MetaCard
from enums import ActionType, DiceEvent, EventCardType, GameStage
from card_data import CardData
from player import Player
import config
from util import DiceEvents, Pos


class Game:
    def __init__(self):
        self.eventCards = []
        self.activePlayer = Player(1)
        self.nonactivePlayer = Player(2)

        self.board: Board = Board(Pos(*config.MAIN_BOARD_SIZE))
        self.handBoard = Board(Pos(*config.HAND_BOARD_SIZE))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SIZE))
        self.bigCard = Board(Pos(1, 1))
        self.buttons = Board(Pos(2, 3))

        self.cardPiles: List[List[Card]] = [[] for _ in range(config.PILE_COUNT)]
        self.eventCards: List[Event] = CardData.create_event_cards()
        self.landscapeCards: List[Landscape] = []
        self.infraCardsLeft = {
            Village: config.VILLAGES_COUNT,
            Path: config.PATHS_COUNT,
            Town: config.TOWNS_COUNT
        }
        self.mouseClicks: List[Pos] = []
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
        self.stage = GameStage.LANDSCAPE_SETUP   # the first action of the game

    def player_action_choose_starting_cards(self):
        if self.mouseClicks and self.board.get_square(self.mouseClicks[-1]).name == 'back':
            pileNo = self.mouseClicks[-1].x - self.board.size.x + len(self.cardPiles)
            for pile in self.cardPiles:
                print(len(pile))
            #for card in self.cardPiles[pileNo]:
            #    pass


    def player_action_land_setup(self):
        if self.mouseClicks and self.mouseClicks[-1] == Pos(0, 0):
            self.stage = GameStage.CHOOSE_CARDS
        if len(self.mouseClicks) >= 2:
            pos1, pos2 = self.mouseClicks[0], self.mouseClicks[1]
            card1, card2 = self.board.get_square(pos1), self.board.get_square(pos2)
            if isinstance(card1, Landscape) and isinstance(card2, Landscape) and card1.player is self.activePlayer and card2.player is self.activePlayer:
                self.board.set_square(pos1, card2)
                self.board.set_square(pos2, card1)
            self.mouseClicks.clear()

    def event_mouse_click(self, pos: Tuple[int, int]):
        cardSizeX, cardSizeY = config.CARD_IMG_SIZE_SMALL
        x, y = pos
        x = x // (cardSizeX + config.CARD_IMG_SPACING * 2)
        y = y // (cardSizeY + config.CARD_IMG_SPACING * 2)
        self.mouseClicks.append(Pos(x, y))

        if self.stage == GameStage.LANDSCAPE_SETUP:
            self.player_action_land_setup()
        elif self.stage == GameStage.CHOOSE_CARDS:
            self.player_action_choose_starting_cards()

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
        for lCard, pos in zip(self.activePlayer.landscapeCards, [Pos(4, 9), Pos(6, 9), Pos(8, 9), Pos(4, 7), Pos(6, 7), Pos(8, 7)]):
            self.board.set_square(pos, lCard)

        self.board.set_square(Pos(0, 5), MetaCard('back_event'))
        self.board.set_square(Pos(1, 5), MetaCard('back_land'))
        self.board.set_square(Pos(2, 5), MetaCard('back_path'))
        self.board.set_square(Pos(3, 5), MetaCard('back_village'))
        self.board.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(8, 13):
            self.board.set_square(Pos(x, 5), MetaCard('back')) # TODO - set this up relative to right side

    def setup_landscape_cards(self):
        for card in CardData.create_landscape_cards(self.activePlayer, self.nonactivePlayer):
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
        return self.activePlayer.victoryPoints >= config.VICTORY_POINTS or self.nonactivePlayer.victoryPoints >= config.VICTORY_POINTS

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
            action = self.activePlayer.get_action()
            if action.actionType == ActionType.END_TURN:
                break

        self.settle_card_counts(self.activePlayer)
        self.settle_card_counts(self.nonactivePlayer)




    def play(self):
        while not self.is_victory():
            self.activePlayer, self.nonactivePlayer = self.nonactivePlayer, self.activePlayer
            self.turn()

