from typing import TYPE_CHECKING, List
#from game import Game
if TYPE_CHECKING:
    from card import Playable, Landscape

class Player:
    #def __init__(self, game: Game, number: int):
    #    self.game: Game = game
    def __init__(self, game, number: int):
        self.game = game
        self.number: int = number
        self.victoryPoints = 0
        self.tradePoints = 0
        self.tournamentPoints = 0
        self.battlePoints = 0
        self.cardsInHandCnt: int = 3
        self.cardsInHand: List[Playable] = []
        self.landscapeCards: List[Landscape] = []

    def take_card(self, card: 'Playable') -> None:
        self.cardsInHand.append(card)
        self.game.handBoard.set_next_square(card)

    def add_card(self, card: 'Playable'):
        if len(self.cardsInHand) >= self.cardsInHandCnt:
            raise ValueError(f'cannot take a card, already at max')
        self.cardsInHand.append(card)