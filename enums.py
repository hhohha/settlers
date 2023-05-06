from enum import Enum

class Button(Enum):
    NO_BUTTON = -1
    OK = 0
    CANCEL = 1
    END_TURN = 2
    TRADE = 3
    UNKNOWN1 = 4
    UNKNOWN2 = 5

class GameStage(Enum):
    NONE = 0
    LANDSCAPE_SETUP = 1
    CHOOSE_STARING_CARDS = 2

class BuildingType(Enum):
    WAREHOUSE = 0
    MILL = 1
    SAWMILL = 2
    BRICKYARD = 3
    SPINNING_MILL = 4
    STEEL_MILL = 5
    CLOISTER = 6
    SMITHY = 7
    SPA = 8
    LIBRARY = 9
    COLOSSUS = 10
    PORT = 11
    CHURCH = 12
    MARKET = 13
    TRADE_OFFICE = 14
    TRADE_GUILD = 15
    MINT = 16
    TOWN_HALL = 17
    AQUADUCT = 18

class ActionCardType(Enum):
    ALCHEMIST = 'alchemist'
    BISHOP = 'bishop'
    ARSON = 'arson'
    TRADER = 'trader'
    CARAVAN = 'caravan'
    WITCH = 'witch'
    SCOUT = 'scout'
    AMBUSH = 'ambush'
    BLACK_KNIGHT = 'black_knight'
    SPY = 'spy'

class Resource(Enum):
    GRAIN = 'grain'
    SHEEP = 'sheep'
    ROCK = 'rock'
    BRICK = 'brick'
    WOOD = 'wood'
    GOLD = 'gold'

class ActionType(Enum):
    BUILD_FROM_HAND = 0
    BUILD_VILLAGE = 1
    BUILD_TOWN = 2
    BUILD_PATH = 3
    PROPOSE_TRADE = 4
    BANK_TRADE = 5
    ACTION_CARD = 6
    END_TURN = 7

class DiceEvent(Enum):
    TOURNAMENT = 0
    TRADE_PROFIT = 1
    AMBUSH = 2
    GOOD_HARVEST = 3
    CARD_EVENT = 4

class EventCardType(Enum):
    BUILDER = 'builder'
    CIVIL_WAR = 'civil_war'
    RICH_YEAR = 'rich_year'
    ADVANCE = 'advance'
    NEW_YEAR = 'new_year'
    CONFLICT = 'conflict'
    PLAQUE = 'plaque'
