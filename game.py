import random
from typing import List, Optional, Tuple
from board import Board
from click_filter import ClickFilter
from computer_player import ComputerPlayer
from display_handler import DisplayHandler
from enums import DiceEvent, EventCardType
from card_data import CardData
from human_player import HumanPlayer
import config
from player import Player
from util import DiceEvents, Pos, MouseClick, MILLS_EFFECTS
from card import Card, Event, Landscape, Village, Town, Path, MetaCard, Playable, Building, Buildable, SettlementSlot

Pile = List[Playable]

class Game:
    def __init__(self):
        self.eventCards: List[EventCardType] = []

        self.mainBoard: Board = Board(Pos(*config.MAIN_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player1Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.player2Board = Board(Pos(*config.PLAYER_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SQUARES), Pos(*config.CARD_IMG_SIZE_SMALL))
        self.bigCard = Board(Pos(1, 1), Pos(*config.CARD_IMG_SIZE_BIG))
        self.buttons = Board(Pos(*config.BUTTON_BOARD_SQUARES), Pos(*config.BUTTON_SIZE))

        self.player1: Player = HumanPlayer(self, self.player1Board, 1, Pos(6, 8))
        self.player2: Player = ComputerPlayer(self, self.player2Board, 2, Pos(6, 2))
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

        self.setup_playable_cards()
        self.init_main_board()
        self.setup_landscape_cards()

        self.player1Board.fill_board(MetaCard('empty'))
        self.player2Board.fill_board(MetaCard('empty'))
        self.choiceBoard.fill_board(MetaCard('empty'))
        self.bigCard.fill_board(MetaCard('empty'))
        self.buttons.fill_board(MetaCard('empty'))

    def get_filtered_click(self, clickFilters: Tuple[ClickFilter, ...]=()) -> MouseClick:
        while True:
            click = self.display.get_mouse_click()
            if click.board.get_square(click.pos) is None:
                continue
            if not clickFilters:
                return click
            for clickFilter in clickFilters:
                if clickFilter.accepts(click):
                    return click

    def init_main_board(self):
        for pos in (Pos(x, y) for x in range(self.mainBoard.size.x) for y in range(self.mainBoard.size.y)):
            self.mainBoard.set_square(pos, MetaCard('empty'))

        for player in [self.player1, self.player2]:
            self.mainBoard.set_square(player.midPos, Path(player.midPos, player))

            FIX IT HERE
            self.mainBoard.set_square(player.midPos.right(), Village(player.midPos.right(), player))
            self.mainBoard.set_square(player.midPos.right().up(), SettlementSlot(player.midPos.right().up()))
            self.mainBoard.set_square(player.midPos.right().down(), SettlementSlot(player.midPos.right().down()))

            self.mainBoard.set_square(player.midPos.left(), Village(player.midPos.left(), player))
            self.mainBoard.set_square(player.midPos.left().up(), SettlementSlot(player.midPos.left().up()))
            self.mainBoard.set_square(player.midPos.left().down(), SettlementSlot(player.midPos.left().down()))

        self.mainBoard.set_square(Pos(0, 5), MetaCard('back_event'))
        self.mainBoard.set_square(Pos(1, 5), MetaCard('back_land'))
        self.mainBoard.set_square(Pos(2, 5), MetaCard('back_path'))
        self.mainBoard.set_square(Pos(3, 5), MetaCard('back_village'))
        self.mainBoard.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(self.mainBoard.size.x - len(self.cardPiles), self.mainBoard.size.x):
            self.mainBoard.set_square(Pos(x, 5), MetaCard('back'))

    def setup_landscape_cards(self):
        for card in CardData.create_landscape_cards(self.player1, self.player2):
            if card.player is not None:
                card.player.setup_land_card(card)
            else:
                self.landscapeCards.append(card)

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
            print('tournament winner is player1')
            self.player1.pick_any_resource()
        elif player1Strength < player2Strength:
            print('tournament winner is player2')
            self.player2.pick_any_resource()
        else:
            print('tournament has no winner')

    def event_trade_profit(self) -> None:
        player1Profit = self.player1.get_trade_strength()
        player2Profit = self.player1.get_trade_strength()

        if player1Profit > player2Profit:
            print('trade profit for player 1')
            self.player1.grab_any_resource()
        elif player1Profit < player2Profit:
            print('trade profit for player 2')
            self.player2.grab_any_resource()
        else:
            print('no trade profit')

    def event_good_harvest(self) -> None:
        self.player1.pick_any_resource()
        self.player2.pick_any_resource()

    def event_ambush(self) -> None:
        for player in [self.player1, self.player2]:
            if player.get_unprotected_resources_cnt() > config.AMBUSH_MAX_RESOURCES:
                player.lose_ambush_resources()

    def handle_dice_events(self, event: DiceEvent):
        if event == DiceEvent.TOURNAMENT:
            self.event_tournament()
        elif event == DiceEvent.TRADE_PROFIT:
            self.event_trade_profit()
        elif event == DiceEvent.AMBUSH:
            self.event_ambush()
        elif event == DiceEvent.GOOD_HARVEST:
            self.event_good_harvest()
        elif event == DiceEvent.CARD_EVENT:
            self.card_event()
        else:
            raise ValueError(f'unknown dice event: {event}')


    def card_event_builder(self) -> None:
        pass

    def card_event_civil_war(self) -> None:
        pass

    def card_event_rich_year(self) -> None:
        pass

    def card_event_advance(self) -> None:
        pass

    def card_event_new_year(self) -> None:
        random.shuffle(self.eventCards)

    def card_event_conflict(self) -> None:
        pass

    def card_event_plaque(self) -> None:
        pass


    def card_event(self):
        event: Event = self.eventCards.pop(0)
        self.eventCards.append(event)
        if event.eventType == EventCardType.BUILDER:
            self.card_event_builder()
        elif event.eventType == EventCardType.CIVIL_WAR:
            self.card_event_civil_war()
        elif event.eventType == EventCardType.RICH_YEAR:
            self.card_event_rich_year()
        elif event.eventType == EventCardType.ADVANCE:
            self.card_event_advance()
        elif event.eventType == EventCardType.NEW_YEAR:
            self.card_event_new_year()
        elif event.eventType == EventCardType.CONFLICT:
            self.card_event_conflict()
        elif event.eventType == EventCardType.PLAQUE:
            self.card_event_plaque()
        else:
            raise ValueError(f'unknown card event: {event}')

    def select_card(self, card: Card):
        self.bigCard.set_square(Pos(0, 0), card)

    def display_cards_for_choice(self, pile: Pile) -> None:
        self.choiceBoard.clear()
        for card in pile:
            self.choiceBoard.set_next_square(card)

    def throw_yield_dice(self) -> int:
        return random.randint(1, 6)

    def get_land_neighbors(self, card: Landscape) -> List[Buildable]:
        assert card.pos is not None and card.player is not None
        posLst: List[Pos] = []
        if card.pos.x > 0:
            posLst.append(card.pos.left())
            posLst.append(card.pos.left().up() if card.pos.y > card.player.midPos.y else card.pos.left().down())
        if card.pos.x < self.mainBoard.size.x - 1:
            posLst.append(card.pos.right())
            posLst.append(card.pos.right().up() if card.pos.y > card.player.midPos.y else card.pos.right().down())

        retLst: List[Buildable] = []
        for pos in posLst:
            square = self.mainBoard.get_square(pos)
            if isinstance(square, Buildable):
                retLst.append(square)
        return retLst

    def get_land_yield(self, card: Landscape) -> int:
        buildingNeeded = MILLS_EFFECTS[card.resource]
        # TODO this double isinstance is ugly - improve it somehow
        buildingsAvailable = filter (lambda b: isinstance(b, Building), self.get_land_neighbors(card))
        return 2 if buildingNeeded in map(lambda b: isinstance(b, Building) and b.buildingType, buildingsAvailable) else 1

    def land_yield(self, number: int):
        for player in [self.player1, self.player2]:
            for land in player.landscapeCards:
                if land.diceNumber == number and land.resourcesHeld < config.MAX_LAND_RESOURCES:
                    land.resourcesHeld = min(land.resourcesHeld + self.get_land_yield(land), config.MAX_LAND_RESOURCES)
                    assert land.pos is not None
                    self.mainBoard.refresh_square(land.pos)

    def throw_event_dice(self) -> DiceEvent:
        return DiceEvents[random.randint(1, 6)]

    def play(self):
        for player in [self.player1, self.player2]:
            player.initial_land_setup()

        for player in [self.player1, self.player2]:
            player.pick_starting_cards()

        player: Player = self.player1
        while not self.is_victory():
            player.throw_dice()
            player.do_actions()
            player.refill_hand(True)
            player.opponent.refill_hand(False)
            player = player.opponent

