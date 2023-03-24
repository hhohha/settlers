import pygame as pg


IMAGE_NAMES = ['village', 'town', 'path', 'gold', 'rocks', 'sheep', 'grain', 'tree', 'bricks']

edited_squares = []
board = [None] * 15*11

def place_card(name, x, y):
    global edited_squares
    board[x*15 + y] = name
    edited_squares.append((x, y))


def main():
    global edited_squares
    # setup
    #random.seed(time.time())
    #game = Game()
    #game.play()



    pg.init()
    boardSizeX, boardSizeY = 15, 11
    screen = pg.display.set_mode((130 * boardSizeX, 130 * boardSizeY))
    clock = pg.time.Clock()
    pg.display.set_caption('Settlers')
    IMAGES = {}

    for name in IMAGE_NAMES:
        IMAGES[name] = pg.image.load('imgs/' + name + '.png').convert_alpha()

    place_card('path', 5, 8)
    place_card('village', 4, 8)
    place_card('village', 6, 8)

    place_card('tree', 5, 9)
    place_card('gold', 5, 7)
    place_card('rocks', 3, 9)
    place_card('bricks', 3, 7)
    place_card('sheep', 7, 9)
    place_card('grain', 7, 7)


    place_card('path', 5, 2)
    place_card('village', 4, 2)
    place_card('village', 6, 2)


    screen.fill((240, 220, 200))
    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return

        for square in edited_squares:
            x, y = square
            screen.blit(IMAGES[board[x*15 + y]], (x * 125 + 5, y * 125 + 4))  # TODO - blits instead of blit
        edited_squares = []
        clock.tick(3)
        pg.display.flip()

if __name__ == '__main__':
    main()
