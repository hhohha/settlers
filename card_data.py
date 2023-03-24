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
    {'resource': Resource.GOLD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'resource': Resource.SHEEP, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'resource': Resource.WOOD, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'resource': Resource.ROCK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'resource': Resource.BRICK, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1},
    {'resource': Resource.GRAIN, 'cost': Cost(wood=1, sheep=1), 'trade_points': 1}
]

BUILDING_LIST = [
    {'type': BuildingType.WAREHOUSE, 'count': 3, 'cost': Cost(brick=1, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.MILL, 'count': 1, 'cost': Cost(brick=1, grain=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.SAWMILL, 'count': 1, 'cost': Cost(wood=2), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.BRICKYARD, 'count': 1, 'cost': Cost(brick=1, rock=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.SPINNING_MILL, 'count': 1, 'cost': Cost(brick=1, sheep=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.CLOISTER, 'count': 2, 'cost': Cost(rock=1, brick=1, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.SMITHY, 'count': 1, 'cost': Cost(rock=2, wood=1), 'victory_points': 0, 'trade_points': 0, 'town_only': False},
    {'type': BuildingType.SPA, 'count': 2, 'cost': Cost(brick=2, rock=1, sheep=1), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
    {'type': BuildingType.LIBRARY, 'count': 2, 'cost': Cost(rock=2, brick=1, wood=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
    {'type': BuildingType.COLOSSUS, 'count': 1, 'cost': Cost(rock=3, brick=3, grain=3), 'victory_points': 2, 'trade_points': 0, 'town_only': True},
    {'type': BuildingType.PORT, 'count': 1, 'cost': Cost(rock=1, brick=1, sheep=1), 'victory_points': 0, 'trade_points': 1, 'town_only': True},
    {'type': BuildingType.CHURCH, 'count': 2, 'cost': Cost(rock=2, brick=1, grain=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
    {'type': BuildingType.MARKET, 'count': 1, 'cost': Cost(sheep=1, grain=1), 'victory_points': 0, 'trade_points': 2, 'town_only': True},
    {'type': BuildingType.TRADE_OFFICE, 'count': 1, 'cost': Cost(sheep=2, grain=1, brick=1), 'victory_points': 0, 'trade_points': 3, 'town_only': True},
    {'type': BuildingType.TRADE_GUILD, 'count': 1, 'cost': Cost(sheep=3, brick=2, grain=1), 'victory_points': 0, 'trade_points': 4, 'town_only': True},
    {'type': BuildingType.MINT, 'count': 1, 'cost': Cost(wood=2, brick=2, rock=2), 'victory_points': 0, 'trade_points': 1, 'town_only': True},
    {'type': BuildingType.TOWN_HALL, 'count': 2, 'cost': Cost(sheep=2, rock=2, brick=1), 'victory_points': 1, 'trade_points': 0, 'town_only': True},
    {'type': BuildingType.AQUADUCT, 'count': 2, 'cost': Cost(rock=2, brick=2, wood=2), 'victory_points': 1, 'trade_points': 0, 'town_only': True}
]

ACTION_CARD_LIST = [
    {'type': ActionCardType.ALCHYMIST, 'count': 2},
    {'type': ActionCardType.BISHOP, 'count': 2},
    {'type': ActionCardType.ARSON, 'count': 2},
    {'type': ActionCardType.TRADER, 'count': 2},
    {'type': ActionCardType.CARAVAN, 'count': 1},
    {'type': ActionCardType.WITCH, 'count': 2},
    {'type': ActionCardType.SCOUT, 'count': 2},
    {'type': ActionCardType.AMBUSH, 'count': 1},
    {'type': ActionCardType.BLACK_KNIGHT, 'count': 3},
    {'type': ActionCardType.SPY, 'count': 3}
]

EVENT_CARD_LIST = [
    {'type': EventCardType.BUILDER, 'count': 1},
    {'type': EventCardType.CIVIL_WAR, 'count': 1},
    {'type': EventCardType.RICH_YEAR, 'count': 2},
    {'type': EventCardType.ADVANCE, 'count': 2},
    {'type': EventCardType.NEW_YEAR, 'count': 1},
    {'type': EventCardType.CONFLICT, 'count': 1},
    {'type': EventCardType.PLAQUE, 'count': 2}
]

LANDSCAPE_CARD_LIST = [
    {'resource': Resource.GOLD, 'dice': 1, 'count': 1, 'player': 2},
    {'resource': Resource.GOLD, 'dice': 3, 'count': 1, 'player': None},
    {'resource': Resource.GOLD, 'dice': 6, 'count': 1, 'player': 1},
    {'resource': Resource.ROCK, 'dice': 2, 'count': 1, 'player': 1},
    {'resource': Resource.ROCK, 'dice': 3, 'count': 1, 'player': 2},
    {'resource': Resource.ROCK, 'dice': 4, 'count': 1, 'player': None},
    {'resource': Resource.ROCK, 'dice': 5, 'count': 1, 'player': None},
    {'resource': Resource.SHEEP, 'dice': 3, 'count': 1, 'player': 1},
    {'resource': Resource.SHEEP, 'dice': 4, 'count': 1, 'player': 2},
    {'resource': Resource.SHEEP, 'dice': 5, 'count': 1, 'player': None},
    {'resource': Resource.SHEEP, 'dice': 6, 'count': 1, 'player': None},
    {'resource': Resource.WOOD, 'dice': 1, 'count': 1, 'player': None},
    {'resource': Resource.WOOD, 'dice': 4, 'count': 1, 'player': 1},
    {'resource': Resource.WOOD, 'dice': 5, 'count': 1, 'player': 2},
    {'resource': Resource.WOOD, 'dice': 6, 'count': 1, 'player': None},
    {'resource': Resource.BRICK, 'dice': 1, 'count': 1, 'player': None},
    {'resource': Resource.BRICK, 'dice': 2, 'count': 1, 'player': None},
    {'resource': Resource.BRICK, 'dice': 5, 'count': 1, 'player': 1},
    {'resource': Resource.BRICK, 'dice': 6, 'count': 1, 'player': 2},
    {'resource': Resource.GRAIN, 'dice': 1, 'count': 1, 'player': 1},
    {'resource': Resource.GRAIN, 'dice': 2, 'count': 1, 'player': 2},
    {'resource': Resource.GRAIN, 'dice': 3, 'count': 1, 'player': None},
    {'resource': Resource.GRAIN, 'dice': 4, 'count': 1, 'player': None}
]
