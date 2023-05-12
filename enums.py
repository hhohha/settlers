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
