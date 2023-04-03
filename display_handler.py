import sys

import pygame as pg

from board import Board
from util import Pos, MouseClick
from config import *
from card_data import CardData
from typing import Dict, List, Optional, Tuple


class DisplayHandler:
    def __init__(self):
        self.boards: List[Board] = []
        self.images: Dict[str, pg.Surface] = {}
        cardSize = Pos(*CARD_IMG_SIZE_SMALL)

        pg.init()
        space = CARD_IMG_SPACING
        boardSize: Pos = Pos(*MAIN_BOARD_SQUARES)
        screenSize: Pos = Pos((cardSize.x + space * 2) * (
                    boardSize.x + max(HAND_BOARD_SQUARES[0], CHOICE_BOARD_SQUARES[0])) + RIGHT_BOARDS_SPACE + space,
                              (cardSize.y + space * 2) * boardSize.y)

        self.screen = pg.display.set_mode(screenSize.tuple())
        self.screen.fill(BACKGROUND_IMAGE)
        pg.display.set_caption('Settlers')
        self.clock = pg.time.Clock()

        for name in CardData.CARD_NAMES:
            self.images[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    def refresh_screen(self):
        space = CARD_IMG_SPACING
        for board in self.boards:
            for square in board.get_edited_squares():
                img = pg.transform.scale(self.images[board.get_square(square).name], board.squareSize.tuple())
                self.screen.blit(img, (square * (board.squareSize + 2 * space) + space + board.topLeft).tuple())
        pg.display.flip()

    def add_board(self, board: Board) -> None:
        self.boards.append(board)

    def get_click_square(self, pos: Pos) -> Optional[MouseClick]:
        for board in self.boards:
            if board.topLeft is None or board.bottomRight is None:
                continue
            if board.bottomRight > pos > board.topLeft:
                retPos = (pos - board.topLeft) // (board.squareSize + Pos(board.spacing, board.spacing))
                return MouseClick(board, retPos)
        return None

    def get_mouse_click(self) -> MouseClick:
        while True:
            for event in pg.event.get():
                if event.type is pg.QUIT:
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mousePos = Pos(*pg.mouse.get_pos())
                    click = self.get_click_square(mousePos)
                    if click is not None:
                        return click
            self.refresh_screen()
            self.clock.tick(20)
