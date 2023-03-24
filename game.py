import random
from typing import List, Optional

from board import Board
from card import Card, Fleet, Knight, Building, Action, Event, Landscape
from enums import ActionType, DiceEvent, EventCardType
from card_data import KNIGHT_LIST, ACTION_CARD_LIST, BUILDING_LIST, FLEET_LIST, EVENT_CARD_LIST, LANDSCAPE_CARD_LIST
from player import Player
import config
from util import DiceEvents


class Game:
    def __init__(self):
        self.eventCards = []
        self.activePlayer = Player(1)
        self.nonactivePlayer = Player(2)
        self.board: Board = Board()
        self.cardPiles: List[List[Card]] = [[] * config.PILE_COUNT]
        self.eventCards: List[Event] = []
        self.landscapeCards: List[Landscape] = []
        self.paths: int = config.PATHS_COUNT
        self.villages: int = config.VILLAGES_COUNT
        self.towns: int = config.TOWNS_COUNT

    def create_landscape_cards(self):
        cards: List[Landscape] = []

        for landscapeCard in LANDSCAPE_CARD_LIST:
            for _ in range(landscapeCard['count']):
                card = Landscape(
                    landscapeCard['resource'],
                    landscapeCard['dice']
                )

                if landscapeCard['player'] is None:
                    cards.append(card)
                if landscapeCard['player'] == 1:
                    card.player = self.activePlayer
                    self.activePlayer.landscapeCards.append(card)
                elif landscapeCard['player'] == 2:
                    card.player = self.nonactivePlayer
                    self.nonactivePlayer.landscapeCards.append(card)
                else:
                    raise ValueError(f"invalid player: {landscapeCard['player']}")

        while cards:
            idx = random.randint(len(cards))
            self.landscapeCards.append(cards.pop(idx))


    def create_event_cards(self):
        cards: List[Event] = []
        for eventCard in EVENT_CARD_LIST:
            for _ in range(eventCard['count']):
                cards.append(Event(eventCard['type']))

        idx = random.randint(len(cards))
        self.eventCards.append(cards.pop(idx))

    def create_playable_cards(self) -> None:
        cards: List[Card] = []
        for fleetData in FLEET_LIST:
            cards.append(Fleet(
                fleetData['cost'],
                fleetData['resource'],
                fleetData['trade_points'],
                None
            ))

        for knightData in KNIGHT_LIST:
            cards.append(Knight(
                knightData['name'],
                knightData['cost'],
                knightData['tournament_strength'],
                knightData['battle_strength'],
                None
            ))

        for buildingData in BUILDING_LIST:
            for _ in range(buildingData['count']):
                cards.append(Building(
                    buildingData['type'],
                    buildingData['cost'],
                    buildingData['town_only'],
                    buildingData['victory_points'],
                    buildingData['trade_points'],
                    None
                ))

        for actionCardData in ACTION_CARD_LIST:
            for _ in range(actionCardData['count']):
                cards.append(Action(actionCardData['type']))

        i = 0
        while cards:
            idx = random.randint(len(cards))
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

