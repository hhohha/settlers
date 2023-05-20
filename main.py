import random
import time
from game import Game

# TODOS
#  - implement AI
#  - voluntarily remove card from board
#  - remove print_msg from module player

# COVERED BY UNIT TESTS
#  - board.py                 OK
#  - card_data.py
#  - card.py                  OK
#  - click_filter.py
#  - computer_player.py
#  - config.py
#  - custom_types.py
#  - display_handler.py
#  - enums.py
#  - game.py
#  - human_player.py
#  - main.py
#  - player.py                DONE
#  - util.py                  PART

def main():
    random.seed(time.time())
    game = Game()
    game.play()

if __name__ == '__main__':
    main()
