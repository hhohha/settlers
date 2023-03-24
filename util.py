from dataclasses import dataclass
from enums import DiceEvent

@dataclass(frozen=True)
class Cost:
    grain: int = 0
    sheep: int = 0
    rock: int = 0
    brick: int = 0
    wood: int = 0

@dataclass(frozen=True)
class Pos:
    x: int
    y: int

DiceEvents = {
    1: DiceEvent.TOURNAMENT,
    2: DiceEvent.TRADE_PROFIT,
    3: DiceEvent.AMBUSH,
    4: DiceEvent.GOOD_HARVEST,
    5: DiceEvent.CARD_EVENT,
    6: DiceEvent.CARD_EVENT
}

