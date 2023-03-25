from enums import BuildingType, Resource, ActionCardType, EventCardType
from util import Cost

KNIGHT_LIST = [
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

FLEET_LIST = [
    {'name': 'fleet_gold', 'resource': Resource.GOLD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'name': 'fleet_sheep', 'resource': Resource.SHEEP, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'name': 'fleet_wood', 'resource': Resource.WOOD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'name': 'fleet_rock', 'resource': Resource.ROCK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'name': 'fleet_brick', 'resource': Resource.BRICK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'name': 'fleet_grain', 'resource': Resource.GRAIN, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1}
]

BUILDING_LIST = [
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

ACTION_CARD_LIST = [
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

EVENT_CARD_LIST = [
    {'name': 'builder', 'type': EventCardType.BUILDER, 'count': 1},
    {'name': 'civil_war', 'type': EventCardType.CIVIL_WAR, 'count': 1},
    {'name': 'rich_year', 'type': EventCardType.RICH_YEAR, 'count': 2},
    {'name': 'advance', 'type': EventCardType.ADVANCE, 'count': 2},
    {'name': 'new_year', 'type': EventCardType.NEW_YEAR, 'count': 1},
    {'name': 'conflict', 'type': EventCardType.CONFLICT, 'count': 1},
    {'name': 'plaque', 'type': EventCardType.PLAQUE, 'count': 2}
]

LANDSCAPE_CARD_LIST = [
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

INFRA_CARD_LIST = [
    {'name': 'path'},
    {'name': 'village'},
    {'name': 'town'},
]

META_CARD_LIST = [
    {'name': 'back_land'},
    {'name': 'back_event'},
    {'name': 'back_town'},
    {'name': 'back_path'},
    {'name': 'back_village'},
    {'name': 'back'},
    {'name': 'empty'}
]

CARD_NAMES = {card['name'] for card in KNIGHT_LIST + FLEET_LIST + BUILDING_LIST + ACTION_CARD_LIST + EVENT_CARD_LIST +
              LANDSCAPE_CARD_LIST + INFRA_CARD_LIST + META_CARD_LIST}
