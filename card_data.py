import random
from typing import List, TypedDict, Optional, Set
import config
from card import Landscape, Event, Playable, Fleet, Knight, Building, Action
from enums import BuildingType, Resource, ActionCardType, EventCardType
from player import Player
from util import Cost
from custom_types import Pile

class KnightData(TypedDict):
    name: str
    cost: Cost
    battle_strength: int
    tournament_strength: int

class FleetData(TypedDict):
    name: str
    resource: Resource
    cost: Cost
    trade_points: int

class BuildingData(TypedDict):
    name: str
    type: BuildingType
    count: int
    cost: Cost
    victory_points: int
    trade_points: int
    town_only: bool

class ActionCardData(TypedDict):
    name: str
    type: ActionCardType
    count: int


class EventCardData(TypedDict):
    name: str
    type: EventCardType
    count: int

class LandscapeData(TypedDict):
    name: str
    resource: Resource
    dice: int
    count: int
    player: Optional[int]

class InfraCardData(TypedDict):
    name: str

class NamedData(TypedDict):
    name: str

class CardData:
    @staticmethod
    def create_landscape_cards(player1: Player, player2: Player) -> List[Landscape]:
        cards: List[Landscape] = []

        for landscapeCard in CardData.LANDSCAPE_CARD_LIST:
            for _ in range(landscapeCard['count']):
                card = Landscape(
                    landscapeCard['name'],
                    landscapeCard['resource'],
                    landscapeCard['dice']
                )

                if landscapeCard['player'] is None:
                    pass
                elif landscapeCard['player'] == 1:
                    card.player = player1
                elif landscapeCard['player'] == 2:
                    card.player = player2
                else:
                    raise ValueError(f"invalid player: {landscapeCard['player']}")

                cards.append(card)
        random.shuffle(cards)
        return cards

    @staticmethod
    def create_event_cards() -> List[Event]:
        cards: List[Event] = []
        for eventCard in CardData.EVENT_CARD_LIST:
            for _ in range(eventCard['count']):
                cards.append(Event(eventCard['name'], eventCard['type']))
        random.shuffle(cards)
        return cards

    @staticmethod
    def prepare_piles() -> List[Pile]:
        cardPiles: List[Pile] = [[] for _ in range(config.PILE_COUNT)]
        cards: List[Playable] = CardData.create_playable_cards()
        pileSize = len(cards) // len(cardPiles)
        extraCards = len(cards) % len(cardPiles)
        startIdx, endIdx = 0, pileSize

        for idx, _ in enumerate(cardPiles):
            if extraCards > 0:
                extraCards -= 1
                endIdx += 1
            cardPiles[idx] = cards[startIdx:endIdx]
            startIdx = endIdx
            endIdx += pileSize
        return cardPiles

    @staticmethod
    def create_playable_cards() -> List[Playable]:
        cards: List[Playable] = []
        for fleetData in CardData.FLEET_LIST:
            cards.append(Fleet(
                fleetData['name'],
                fleetData['cost'],
                fleetData['resource'],
                fleetData['trade_points']
            ))

        for knightData in CardData.KNIGHT_LIST:
            cards.append(Knight(
                knightData['name'],
                knightData['cost'],
                knightData['tournament_strength'],
                knightData['battle_strength']
            ))

        for buildingData in CardData.BUILDING_LIST:
            for _ in range(buildingData['count']):
                cards.append(Building(
                    buildingData['name'],
                    buildingData['type'],
                    buildingData['cost'],
                    buildingData['town_only'],
                    buildingData['victory_points'],
                    buildingData['trade_points']
                ))

        for actionCardData in CardData.ACTION_CARD_LIST:
            for _ in range(actionCardData['count']):
                cards.append(Action(actionCardData['name'], actionCardData['type']))

        random.shuffle(cards)
        return cards

    KNIGHT_LIST: List[KnightData] = [
        {'name': 'konrad', 'cost': Cost(grain=1, rock=1), 'battle_strength': 2, 'tournament_strength': 1},
        {'name': 'gustav', 'cost': Cost(grain=2, sheep=2, rock=2), 'battle_strength': 5, 'tournament_strength': 2},
        {'name': 'otto', 'cost': Cost(rock=2, grain=1, sheep=1), 'battle_strength': 3, 'tournament_strength': 2},
        {'name': 'siegfried', 'cost': Cost(rock=1), 'battle_strength': 1, 'tournament_strength': 1},
        {'name': 'walter', 'cost': Cost(grain=1, sheep=1, rock=1), 'battle_strength': 3, 'tournament_strength': 1},
        {'name': 'karel', 'cost': Cost(sheep=3, grain=2, rock=2), 'battle_strength': 7, 'tournament_strength': 1},
        {'name': 'franz', 'cost': Cost(grain=2, rock=2, sheep=1), 'battle_strength': 1, 'tournament_strength': 5},
        {'name': 'pipin', 'cost': Cost(grain=1, sheep=1, rock=1), 'battle_strength': 1, 'tournament_strength': 3},
        {'name': 'hubert', 'cost': Cost(grain=1, rock=1), 'battle_strength': 1, 'tournament_strength': 2},
    ]

    FLEET_LIST: List[FleetData] = [
        {'name': 'fleet_gold', 'resource': Resource.GOLD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
        {'name': 'fleet_sheep', 'resource': Resource.SHEEP, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
        {'name': 'fleet_wood', 'resource': Resource.WOOD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
        {'name': 'fleet_rock', 'resource': Resource.ROCK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
        {'name': 'fleet_brick', 'resource': Resource.BRICK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
        {'name': 'fleet_grain', 'resource': Resource.GRAIN, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1}
    ]

    BUILDING_LIST: List[BuildingData] = [
        {'name': 'warehouse', 'type': BuildingType.WAREHOUSE, 'count': 3, 'cost': Cost(brick=1, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'mill', 'type': BuildingType.MILL, 'count': 1, 'cost': Cost(brick=1, grain=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'sawmill', 'type': BuildingType.SAWMILL, 'count': 1, 'cost': Cost(wood=2), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'brickyard', 'type': BuildingType.BRICKYARD, 'count': 1, 'cost': Cost(brick=1, rock=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'spinning_mill', 'type': BuildingType.SPINNING_MILL, 'count': 1, 'cost': Cost(brick=1, sheep=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'cloister', 'type': BuildingType.CLOISTER, 'count': 2, 'cost': Cost(rock=1, brick=1, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'smithy', 'type': BuildingType.SMITHY, 'count': 1, 'cost': Cost(rock=2, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
        {'name': 'spa', 'type': BuildingType.SPA, 'count': 2, 'cost': Cost(brick=2, rock=1, sheep=1), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
        {'name': 'library', 'type': BuildingType.LIBRARY, 'count': 2, 'cost': Cost(rock=2, brick=1, wood=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
        {'name': 'colossus', 'type': BuildingType.COLOSSUS, 'count': 1, 'cost': Cost(rock=3, brick=3, grain=3), 'victory_points': 2, 'trade_points': 0, 'town_only': True},
        {'name': 'port', 'type': BuildingType.PORT, 'count': 1, 'cost': Cost(rock=1, brick=1, sheep=1), 'victory_points': 0, 'trade_points': 1, 'town_only': True},
        {'name': 'church', 'type': BuildingType.CHURCH, 'count': 2, 'cost': Cost(rock=2, brick=1, grain=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
        {'name': 'market', 'type': BuildingType.MARKET, 'count': 1, 'cost': Cost(sheep=1, grain=1), 'victory_points': 0, 'trade_points': 2, 'town_only': True},
        {'name': 'trade_office', 'type': BuildingType.TRADE_OFFICE, 'count': 1, 'cost': Cost(sheep=2, grain=1, brick=1), 'victory_points': 0, 'trade_points': 3, 'town_only': True},
        {'name': 'trade_guild', 'type': BuildingType.TRADE_GUILD, 'count': 1, 'cost': Cost(sheep=3, brick=2, grain=1), 'victory_points': 0, 'trade_points': 4, 'town_only': True},
        {'name': 'mint', 'type': BuildingType.MINT, 'count': 1, 'cost': Cost(wood=2, brick=2, rock=2), 'victory_points': 0, 'trade_points': 1, 'town_only': True},
        {'name': 'town_hall', 'type': BuildingType.TOWN_HALL, 'count': 2, 'cost': Cost(sheep=2, rock=2, brick=1), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
        {'name': 'aquaduct', 'type': BuildingType.AQUADUCT, 'count': 2, 'cost': Cost(rock=2, brick=2, wood=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True}
    ]

    ACTION_CARD_LIST: List[ActionCardData] = [
        {'name': 'alchemist', 'type': ActionCardType.ALCHEMIST, 'count': 2},
        {'name': 'bishop', 'type': ActionCardType.BISHOP, 'count': 2},
        {'name': 'arson', 'type': ActionCardType.ARSON, 'count': 2},
        {'name': 'trader', 'type': ActionCardType.TRADER, 'count': 2},
        {'name': 'caravan', 'type': ActionCardType.CARAVAN, 'count': 1},
        {'name': 'witch', 'type': ActionCardType.WITCH, 'count': 2},
        {'name': 'scout', 'type': ActionCardType.SCOUT, 'count': 2},
        {'name': 'ambush', 'type': ActionCardType.AMBUSH, 'count': 1},
        {'name': 'black_knight', 'type': ActionCardType.BLACK_KNIGHT, 'count': 3},
        {'name': 'spy', 'type': ActionCardType.SPY, 'count': 3}
    ]

    EVENT_CARD_LIST: List[EventCardData] = [
        {'name': 'builder', 'type': EventCardType.BUILDER, 'count': 1},
        {'name': 'civil_war', 'type': EventCardType.CIVIL_WAR, 'count': 1},
        {'name': 'rich_year', 'type': EventCardType.RICH_YEAR, 'count': 2},
        {'name': 'advance', 'type': EventCardType.ADVANCE, 'count': 2},
        {'name': 'new_year', 'type': EventCardType.NEW_YEAR, 'count': 1},
        {'name': 'conflict', 'type': EventCardType.CONFLICT, 'count': 1},
        {'name': 'plaque', 'type': EventCardType.PLAQUE, 'count': 2}
    ]

    LANDSCAPE_CARD_LIST: List[LandscapeData] = [
        {'name': 'gold', 'resource': Resource.GOLD, 'dice': 1, 'count': 1, 'player': 2},
        {'name': 'gold', 'resource': Resource.GOLD, 'dice': 3, 'count': 1, 'player': None},
        {'name': 'gold', 'resource': Resource.GOLD, 'dice': 6, 'count': 1, 'player': 1},
        {'name': 'rock', 'resource': Resource.ROCK, 'dice': 2, 'count': 1, 'player': 1},
        {'name': 'rock', 'resource': Resource.ROCK, 'dice': 3, 'count': 1, 'player': 2},
        {'name': 'rock', 'resource': Resource.ROCK, 'dice': 4, 'count': 1, 'player': None},
        {'name': 'rock', 'resource': Resource.ROCK, 'dice': 5, 'count': 1, 'player': None},
        {'name': 'sheep', 'resource': Resource.SHEEP, 'dice': 3, 'count': 1, 'player': 1},
        {'name': 'sheep', 'resource': Resource.SHEEP, 'dice': 4, 'count': 1, 'player': 2},
        {'name': 'sheep', 'resource': Resource.SHEEP, 'dice': 5, 'count': 1, 'player': None},
        {'name': 'sheep', 'resource': Resource.SHEEP, 'dice': 6, 'count': 1, 'player': None},
        {'name': 'wood', 'resource': Resource.WOOD, 'dice': 1, 'count': 1, 'player': None},
        {'name': 'wood', 'resource': Resource.WOOD, 'dice': 4, 'count': 1, 'player': 1},
        {'name': 'wood', 'resource': Resource.WOOD, 'dice': 5, 'count': 1, 'player': 2},
        {'name': 'wood', 'resource': Resource.WOOD, 'dice': 6, 'count': 1, 'player': None},
        {'name': 'brick', 'resource': Resource.BRICK, 'dice': 1, 'count': 1, 'player': None},
        {'name': 'brick', 'resource': Resource.BRICK, 'dice': 2, 'count': 1, 'player': None},
        {'name': 'brick', 'resource': Resource.BRICK, 'dice': 5, 'count': 1, 'player': 1},
        {'name': 'brick', 'resource': Resource.BRICK, 'dice': 6, 'count': 1, 'player': 2},
        {'name': 'grain', 'resource': Resource.GRAIN, 'dice': 1, 'count': 1, 'player': 1},
        {'name': 'grain', 'resource': Resource.GRAIN, 'dice': 2, 'count': 1, 'player': 2},
        {'name': 'grain', 'resource': Resource.GRAIN, 'dice': 3, 'count': 1, 'player': None},
        {'name': 'grain', 'resource': Resource.GRAIN, 'dice': 4, 'count': 1, 'player': None}
    ]

    INFRA_CARD_LIST: List[NamedData] = [
        {'name': 'path'},
        {'name': 'village'},
        {'name': 'town'}
    ]

    META_CARD_LIST: List[NamedData] = [
        {'name': 'back_land'},
        {'name': 'back_event'},
        {'name': 'back_town'},
        {'name': 'back_path'},
        {'name': 'back_village'},
        {'name': 'back'},
        {'name': 'empty'},
        {'name': 'highlighted'}
    ]

    CARD_NAMES: Set[str] = {card['name'] for card in KNIGHT_LIST}
    CARD_NAMES.update({card['name'] for card in FLEET_LIST})
    CARD_NAMES.update({card['name'] for card in BUILDING_LIST})
    CARD_NAMES.update({card['name'] for card in ACTION_CARD_LIST})
    CARD_NAMES.update({card['name'] for card in EVENT_CARD_LIST})
    CARD_NAMES.update({card['name'] for card in LANDSCAPE_CARD_LIST})
    CARD_NAMES.update({card['name'] for card in INFRA_CARD_LIST})
    CARD_NAMES.update({card['name'] for card in META_CARD_LIST})