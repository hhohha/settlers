import random
import time
from game import Game
from config import *
from util import Pos


def main():
    random.seed(time.time())
    game = Game()

    space = CARD_IMG_SPACING

    cardSize = game.board.squareSize

    game.board.set_top_left(Pos(0, 0))
    game.handBoard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + RIGHT_BOARDS_SPACE,
                                    (game.board.size.y - game.handBoard.size.y) * (cardSize.y + 2 * space)))
    game.choiceBoard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + space + RIGHT_BOARDS_SPACE, 0))
    game.buttons.set_top_left(Pos(game.handBoard.topLeft.x,
                                  game.handBoard.topLeft.y - game.buttons.size.y * (game.buttons.squareSize.y + 2*space)))

    game.bigCard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + space + RIGHT_BOARDS_SPACE,
                                  (game.buttons.topLeft.y + game.choiceBoard.bottomRight.y) // 2 - game.bigCard.squareSize.y // 2))

    game.play()


if __name__ == '__main__':
    main()
