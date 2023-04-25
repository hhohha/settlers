import random
import time
from game import Game
from config import *
from util import Pos

# BUGS
#  - grab does not subtract
#  - mills don't work in the second position

def main():
    random.seed(time.time())
    game = Game()

    space = CARD_IMG_SPACING

    cardSize = game.mainBoard.squareSize

    game.mainBoard.set_top_left(Pos(0, 0))
    game.player1Board.set_top_left(Pos(game.mainBoard.size.x * (cardSize.x + 2 * space) + BIG_SPACE,
                                       (game.mainBoard.size.y - game.player1Board.size.y) * (cardSize.y + 2 * space)))

    game.player2Board.set_top_left(Pos(game.mainBoard.size.x * (cardSize.x + 2 * space) + space + BIG_SPACE, 0))

    game.choiceBoard.set_top_left(Pos(game.mainBoard.size.x * (cardSize.x + 2 * space) + space + BIG_SPACE,
                                      game.player2Board.bottomRight.y + 2*BIG_SPACE))

    game.bigCard.set_top_left(Pos(game.mainBoard.size.x * (cardSize.x + 2 * space) + space + BIG_SPACE,
                                  (game.player1Board.topLeft.y + game.choiceBoard.bottomRight.y) // 2 - game.bigCard.squareSize.y // 2))
    game.buttons.set_top_left(Pos(game.bigCard.bottomRight.x + BIG_SPACE, game.bigCard.topLeft.y))
    game.display.textTopLeft = Pos(game.choiceBoard.topLeft.x, game.choiceBoard.bottomRight.y + 2*space)
    game.play()


if __name__ == '__main__':
    main()
