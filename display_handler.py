import sys

import pygame as pg

from board import Board
from card import Landscape
from util import Pos, MouseClick
from config import *
from card_data import CardData
from typing import Dict, List, Optional

class DisplayHandler:
    def __init__(self):
        self.boards: List[Board] = []
        self.images: Dict[str, pg.Surface] = {}
        cardSize = Pos(*CARD_IMG_SIZE_SMALL)

        pg.init()
        space = CARD_IMG_SPACING
        boardSize: Pos = Pos(*MAIN_BOARD_SQUARES)
        screenSize: Pos = Pos((cardSize.x + space * 2) * (
                    boardSize.x + max(PLAYER_BOARD_SQUARES[0], CHOICE_BOARD_SQUARES[0])) + BIG_SPACE + space,
                              (cardSize.y + space * 2) * boardSize.y)

        self.screen = pg.display.set_mode(screenSize.tuple())
        self.screen.fill(BACKGROUND_IMAGE)
        pg.display.set_caption('Settlers')
        self.clock = pg.time.Clock()
        self.font = pg.font.Font('freesansbold.ttf', 32)
        self.textTopLeft: Pos = Pos(0, 0)

        for name in CardData.CARD_NAMES:
            self.images[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    def print_msg(self, msg: str) -> None:
        text = self.font.render(msg + ' '*50, True, (40, 40, 40), BACKGROUND_IMAGE)
        self.screen.blit(text, self.textTopLeft.tuple())

    def refresh_screen(self):
        space = CARD_IMG_SPACING
        for board in self.boards:
            for pos in board.get_edited_squares():
                square = board.get_square(pos)
                if square is None:
                    x1, y1, = (pos * (board.squareSize + 2 * space) + space + board.topLeft).tuple()
                    self.screen.fill(BACKGROUND_IMAGE, (x1, y1, *CARD_IMG_SIZE_SMALL))
                else:
                    img = pg.transform.scale(self.images[board.get_square(pos).name], board.squareSize.tuple())
                    self.screen.blit(img, (pos * (board.squareSize + 2 * space) + space + board.topLeft).tuple())
                    if isinstance(square, Landscape):
                        text = self.font.render(str(square.resourcesHeld), True, (40, 40, 40), BACKGROUND_IMAGE)
                        p = pos * (board.squareSize + 2 * space) + space + board.topLeft
                        self.screen.blit(text, p.tuple())

                        text = self.font.render(str(square.diceNumber), True, (40, 40, 40), BACKGROUND_IMAGE)
                        p = (pos * (board.squareSize + 2 * space) + space + board.topLeft) + Pos(*CARD_IMG_SIZE_SMALL) // 2
                        self.screen.blit(text, p.tuple())
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

    def get_mouse_click(self, board: Optional[Board]=None, squareTypes: Optional[List[str]]=None) -> MouseClick:
        while True:
            for event in pg.event.get():
                if event.type is pg.QUIT:
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mousePos = Pos(*pg.mouse.get_pos())
                    click = self.get_click_square(mousePos)
                    if click is None:
                        continue

                    clickedBoard, clickedPos = click.tuple()
                    if board is None:
                        return click

                    if board is not clickedBoard:
                        continue

                    if squareTypes is None:
                        return click

                    square = clickedBoard.get_square(clickedPos)
                    if square is None:
                        continue

                    if square.name in squareTypes:
                        return click

            self.refresh_screen()
            self.clock.tick(20)