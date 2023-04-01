import pygame as pg
import random
import time

from board import BoardsController
from config import *
from card_data import CardData
from game import Game
from util import Pos


def main():
    random.seed(time.time())
    game = Game()
    pg.init()
    boardSizeX, boardSizeY = MAIN_BOARD_SQUARES
    space = CARD_IMG_SPACING
    screenSizeX = (CARD_IMG_SIZE_SMALL[0] + space * 2) * (boardSizeX + max(HAND_BOARD_SQUARES[0], CHOICE_BOARD_SQUARES[
        0])) + RIGHT_BOARDS_SPACE + space
    screenSizeY = (CARD_IMG_SIZE_SMALL[1] + space * 2) * boardSizeY
    screen = pg.display.set_mode((screenSizeX, screenSizeY))
    clock = pg.time.Clock()
    pg.display.set_caption('Settlers')
    IMAGES = {}

    for name in CardData.CARD_NAMES:
        IMAGES[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    screen.fill(BACKGROUND_IMAGE)

    controller = BoardsController()
    controller.add(game.board)
    controller.add(game.handBoard)
    controller.add(game.choiceBoard)
    controller.add(game.bigCard)
    controller.add(game.buttons)

    cardSize = game.board.squareSize

    game.board.set_top_left(Pos(0, 0))
    game.handBoard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + RIGHT_BOARDS_SPACE,
                                    (game.board.size.y - game.handBoard.size.y) * (cardSize.y + 2 * space)))
    game.choiceBoard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + space + RIGHT_BOARDS_SPACE, 0))
    game.buttons.set_top_left(Pos(game.handBoard.topLeft.x,
                                  game.handBoard.topLeft.y - game.buttons.size.y * (game.buttons.squareSize.y + 2*space)))

    game.bigCard.set_top_left(Pos(game.board.size.x * (cardSize.x + 2 * space) + space + RIGHT_BOARDS_SPACE,
                                  (game.buttons.topLeft.y + game.choiceBoard.bottomRight.y) // 2 - game.bigCard.squareSize.y // 2))

    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                mousePos = Pos(*pg.mouse.get_pos())
                click = controller.get_click_square(mousePos)
                if click is not None:
                    game.mouseClicks.append(click)
                    game.respond_to_player_action()

        for board in controller.boards:
            for square in board.get_edited_squares():
                img = pg.transform.scale(IMAGES[board.get_square(square).name], board.squareSize.tuple())
                screen.blit(img, (square * (board.squareSize + 2 * space) + space + board.topLeft).tuple())

        clock.tick(30)
        pg.display.flip()


if __name__ == '__main__':
    main()
