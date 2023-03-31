import pygame as pg
import random
import time
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

    cardSize = Pos(*CARD_IMG_SIZE_SMALL)
    bigCardSize = Pos(*CARD_IMG_SIZE_BIG)
    mainBoardSquares = Pos(*MAIN_BOARD_SQUARES)
    handBoardSquares = Pos(*HAND_BOARD_SQUARES)
    choiceBoardSquares = Pos(*CHOICE_BOARD_SQUARES)
    buttonSize = Pos(*BUTTON_SIZE)
    buttonBoardSquares = Pos(*BUTTON_BOARD_SQUARES)

    mainBoardTopLeft = Pos(0, 0)
    mainBoardBottomRight = mainBoardTopLeft + (cardSize + space) * mainBoardSquares + space

    handBoardTopLeft = Pos(mainBoardSquares.x * (cardSize.x + 2*space) + RIGHT_BOARDS_SPACE,
                           (mainBoardSquares.y - handBoardSquares.y) * (cardSize.y + 2*space))
    handBoardBottomRight = handBoardTopLeft + (cardSize + space) * (handBoardSquares + space)

    choiceBoardTopLeft = Pos(mainBoardSquares.x * (cardSize.x + 2*space) + space + RIGHT_BOARDS_SPACE, 0)
    choiceBoardBottomRight = choiceBoardTopLeft + (cardSize + space) * choiceBoardSquares + space

    bigCardTopLeft = Pos(mainBoardSquares.x * (cardSize.x + 2*space) + space + RIGHT_BOARDS_SPACE,
                         (cardSize.y + 2*space) * choiceBoardSquares.y + 2*space)
    bigCardBottomRight = bigCardTopLeft + bigCardSize + space

    buttonBoardTopLeft = Pos(bigCardBottomRight.x + space, bigCardTopLeft.y)
    buttonBoardBottomRight = buttonBoardTopLeft + (buttonSize + space) * buttonBoardSquares + space


    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                game.event_mouse_click(pg.mouse.get_pos())

        for square in game.board.get_edited_squares():
            imgIdx = square.x + mainBoardSquares.x * square.y
            img = pg.transform.scale(IMAGES[game.board.squares[imgIdx].name], cardSize.tuple())
            screen.blit(img, (square * (cardSize + 2*space) + space).tuple())

        for square in game.handBoard.get_edited_squares():
            imgIdx = square.x + handBoardSquares.x * square.y
            img = pg.transform.scale(IMAGES[game.handBoard.squares[imgIdx].name], cardSize.tuple())
            screen.blit(img, (square * (cardSize + 2*space) + space + handBoardTopLeft).tuple())

        for square in game.choiceBoard.get_edited_squares():
            imgIdx = square.x + choiceBoardSquares.x * square.y
            img = pg.transform.scale(IMAGES[game.choiceBoard.squares[imgIdx].name], cardSize.tuple())
            screen.blit(img, (square * (cardSize + 2*space) + space + choiceBoardTopLeft).tuple())

        for square in game.bigCard.get_edited_squares():
            img = pg.transform.scale(IMAGES[game.bigCard.squares[0].name], bigCardSize.tuple())
            screen.blit(img, (bigCardTopLeft + space).tuple())

        for square in game.buttons.get_edited_squares():
            imgIdx = square.x + buttonBoardSquares.x * square.y
            img = pg.transform.scale(IMAGES[game.buttons.squares[imgIdx].name], buttonSize.tuple())
            screen.blit(img, (square * (buttonSize + 2*space) + space + buttonBoardTopLeft).tuple())

        clock.tick(30)
        pg.display.flip()


if __name__ == '__main__':
    main()
