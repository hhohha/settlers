import random
from typing import List, Optional, Type, Tuple

from board import Board
from card import Card, Fleet, Knight, Building, Action, Event, Landscape, Village, Town, Path, MetaCard
from enums import ActionType, DiceEvent, EventCardType, GameStage
from card_data import KNIGHT_LIST, ACTION_CARD_LIST, BUILDING_LIST, FLEET_LIST, EVENT_CARD_LIST, LANDSCAPE_CARD_LIST
from player import Player
import config
from util import DiceEvents, Pos


class Game:
    def __init__(self):
        self.eventCards = []
        self.activePlayer = Player(1)
        self.nonactivePlayer = Player(2)
        self.board: Board = Board(Pos(*config.MAIN_BOARD_SIZE))
        self.myCardBoard = Board(Pos(*config.PLAYER_CARDS_BOARD_SIZE))
        self.choiceBoard = Board(Pos(*config.CHOICE_BOARD_SIZE))
        self.cardPiles: List[List[Card]] = [[] for _ in range(config.PILE_COUNT)]
        self.eventCards: List[Event] = []
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

        self.create_cards()
        self.init_board()

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

    def init_board(self):
        for pos in (Pos(x, y) for x in range(self.board.size.x) for y in range(self.board.size.y)):
            self.board.set_square(pos, MetaCard('empty'))

        self.board.set_square(Pos(6, 8), self.create_infra_card(Path))
        self.board.set_square(Pos(7, 8), self.create_infra_card(Village))
        self.board.set_square(Pos(5, 8), self.create_infra_card(Village))
        for lCard, pos in zip(self.activePlayer.landscapeCards, [Pos(4, 9), Pos(6, 9), Pos(8, 9), Pos(4, 7), Pos(6, 7), Pos(8, 7)]):
            self.board.set_square(pos, lCard)
            self.stage = GameStage.LANDSCAPE_SETUP

        self.board.set_square(Pos(0, 5), MetaCard('back_event'))
        self.board.set_square(Pos(1, 5), MetaCard('back_land'))
        self.board.set_square(Pos(2, 5), MetaCard('back_path'))
        self.board.set_square(Pos(3, 5), MetaCard('back_village'))
        self.board.set_square(Pos(4, 5), MetaCard('back_town'))

        for x in range(8, 13):
            self.board.set_square(Pos(x, 5), MetaCard('back')) # TODO - set this up relative to right side


    def create_cards(self):
        self.create_landscape_cards()
        self.create_event_cards()
        self.create_playable_cards()

    def create_landscape_cards(self):
        cards: List[Landscape] = []

        for landscapeCard in LANDSCAPE_CARD_LIST:
            for _ in range(landscapeCard['count']):
                card = Landscape(
                    landscapeCard['name'],
                    landscapeCard['resource'],
                    landscapeCard['dice']
                )

                if landscapeCard['player'] is None:
                    cards.append(card)
                elif landscapeCard['player'] == 1:
                    card.player = self.activePlayer
                    self.activePlayer.landscapeCards.append(card)
                elif landscapeCard['player'] == 2:
                    card.player = self.nonactivePlayer
                    self.nonactivePlayer.landscapeCards.append(card)
                else:
                    raise ValueError(f"invalid player: {landscapeCard['player']}")

        while cards:
            idx = random.randint(0, len(cards) - 1)
            self.landscapeCards.append(cards.pop(idx))


    def create_event_cards(self):
        cards: List[Event] = []
        for eventCard in EVENT_CARD_LIST:
            for _ in range(eventCard['count']):
                cards.append(Event(eventCard['name'], eventCard['type']))

        idx = random.randint(0, len(cards) - 1)
        self.eventCards.append(cards.pop(idx))

    def create_playable_cards(self) -> None:
        cards: List[Card] = []
        for fleetData in FLEET_LIST:
            cards.append(Fleet(
                fleetData['name'],
                fleetData['cost'],
                fleetData['resource'],
                fleetData['trade_points']
            ))

        for knightData in KNIGHT_LIST:
            cards.append(Knight(
                knightData['name'],
                knightData['cost'],
                knightData['tournament_strength'],
                knightData['battle_strength']
            ))

        for buildingData in BUILDING_LIST:
            for _ in range(buildingData['count']):
                cards.append(Building(
                    buildingData['name'],
                    buildingData['type'],
                    buildingData['cost'],
                    buildingData['town_only'],
                    buildingData['victory_points'],
                    buildingData['trade_points']
                ))

        for actionCardData in ACTION_CARD_LIST:
            for _ in range(actionCardData['count']):
                cards.append(Action(actionCardData['name'], actionCardData['type']))

        i = 0
        while cards:
            idx = random.randint(0, len(cards) - 1)
            self.cardPiles[i].append(cards.pop(idx))
            i = 0 if i == len(self.cardPiles) - 1 else i + 1

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

