import pygame as pg
import random
import time
import config
from card_data import CardData
from game import Game
from util import Pos


def main():
    random.seed(time.time())
    game = Game()
    pg.init()
    boardSizeX, boardSizeY = config.MAIN_BOARD_SIZE
    space = config.CARD_IMG_SPACING
    screenSizeX = (config.CARD_IMG_SIZE_SMALL[0] + space * 2) * (boardSizeX + max(config.HAND_BOARD_SIZE[0],
                                                                                  config.CHOICE_BOARD_SIZE[
                                                                                      0])) + config.RIGHT_BOARDS_SPACE + space
    screenSizeY = (config.CARD_IMG_SIZE_SMALL[1] + space * 2) * boardSizeY
    screen = pg.display.set_mode((screenSizeX, screenSizeY))
    clock = pg.time.Clock()
    pg.display.set_caption('Settlers')
    IMAGES = {}

    for name in CardData.CARD_NAMES:
        IMAGES[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    screen.fill(config.BACKGROUND_IMAGE)

    cardSizeX, cardSizeY = config.CARD_IMG_SIZE_SMALL

    mainBoardTopLeft = Pos(0, 0)
    mainBoardBottomRight = Pos((cardSizeX + space) * config.MAIN_BOARD_SIZE[0] + space,
                               (cardSizeY + space) * config.MAIN_BOARD_SIZE[1] + space)


    handBoardOffsetX = config.MAIN_BOARD_SIZE[0] * (
            config.CARD_IMG_SIZE_SMALL[0] + 2 * space) + space + config.RIGHT_BOARDS_SPACE
    handBoardOffsetY = (config.MAIN_BOARD_SIZE[1] - config.HAND_BOARD_SIZE[1]) * (
            config.CARD_IMG_SIZE_SMALL[1] + 2 * space) + space
    handBoardSurface = Pos(handBoardOffsetX, handBoardOffsetY),

    choiceBoardOffsetX = handBoardOffsetX
    choiceBoardOffsetY = 0

    bigCardOffsetX = handBoardOffsetX
    bigCardOffsetY = config.CHOICE_BOARD_SIZE[1] * (config.CARD_IMG_SIZE_SMALL[1] + 2 * space)

    buttonBoardOffsetX = handBoardOffsetX + config.CARD_IMG_SIZE_BIG[1] + space
    buttonBoardOffsetY = bigCardOffsetY

    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                game.event_mouse_click(pg.mouse.get_pos())
        for square in game.board.get_edited_squares():
            img = pg.transform.scale(IMAGES[game.board.squares[square.x + config.MAIN_BOARD_SIZE[0] * square.y].name],
                                     config.CARD_IMG_SIZE_SMALL)
            screen.blit(img, (square.x * (cardSizeX + space * 2) + space, square.y * (cardSizeY + space * 2) + space))
        for square in game.handBoard.get_edited_squares():
            img = pg.transform.scale(
                IMAGES[game.handBoard.squares[square.x + config.HAND_BOARD_SIZE[0] * square.y].name],
                config.CARD_IMG_SIZE_SMALL)
            screen.blit(img, (square.x * (cardSizeX + space * 2) + space + handBoardOffsetX,
                              square.y * (cardSizeY + space * 2) + space + handBoardOffsetY))
        for square in game.choiceBoard.get_edited_squares():
            img = pg.transform.scale(
                IMAGES[game.choiceBoard.squares[square.x + config.CHOICE_BOARD_SIZE[0] * square.y].name],
                config.CARD_IMG_SIZE_SMALL)
            screen.blit(img, (square.x * (cardSizeX + space * 2) + space + choiceBoardOffsetX,
                              square.y * (cardSizeY + space * 2) + space + choiceBoardOffsetY))
        for square in game.bigCard.get_edited_squares():
            img = pg.transform.scale(IMAGES[game.bigCard.squares[0].name], config.CARD_IMG_SIZE_BIG)
            screen.blit(img, (space + bigCardOffsetX, space + bigCardOffsetY))
        for square in game.buttons.get_edited_squares():
            img = pg.transform.scale(
                IMAGES[game.buttons.squares[square.x + config.BUTTON_BOARD_SIZE[0] * square.y].name],
                config.BUTTON_SIZE)
            screen.blit(img, (square.x * (config.BUTTON_SIZE[0] + space * 2) + space + buttonBoardOffsetX,
                              square.y * (config.BUTTON_SIZE[1] + space * 2) + space + buttonBoardOffsetY))
        clock.tick(30)
        pg.display.flip()


if __name__ == '__main__':
    main()
