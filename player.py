class Player:
    def __init__(self, number: int):
        self.number = number
        self.victoryPoints = 0
        self.tradePoints = 0
        self.tournamentPoints = 0
        self.battlePoints = 0
        self.cardsInHand = []
        self.landscapeCards = []