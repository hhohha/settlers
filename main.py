import pygame as pg
import random
import time
import config
from card_data import CARD_NAMES
from game import Game


def main():
    random.seed(time.time())
    game = Game()
    pg.init()
    boardSizeX, boardSizeY = config.MAIN_BOARD_SIZE
    space = config.CARD_IMG_SPACING
    screenSizeX = (config.CARD_IMG_SIZE_SMALL[0] + space * 2) * boardSizeX
    screenSizeY = (config.CARD_IMG_SIZE_SMALL[1] + space * 2) * boardSizeY
    screen = pg.display.set_mode((screenSizeX, screenSizeY))
    clock = pg.time.Clock()
    pg.display.set_caption('Settlers')
    IMAGES = {}

    for name in CARD_NAMES:
        IMAGES[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    screen.fill(config.BACKGROUND_IMAGE)
    cardSizeX, cardSizeY = config.CARD_IMG_SIZE_SMALL

    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                game.event_mouse_click(pg.mouse.get_pos())
        for square in game.board.editedSquares:
            img = pg.transform.scale(IMAGES[game.board.squares[square.x + config.MAIN_BOARD_SIZE[0] * square.y].name], config.CARD_IMG_SIZE_SMALL)
            screen.blit(img, (square.x * (cardSizeX + space*2) + space, square.y * (cardSizeY + space*2) + space))
        game.board.editedSquares.clear()
        clock.tick(30)
        pg.display.flip()


if __name__ == '__main__':
    main()
