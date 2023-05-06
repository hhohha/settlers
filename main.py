import random
import time
from game import Game

# TODOS
#  - implement action cards
#      - alchemist
#      - scout
#  - implement AI
#  - voluntarily remove card from board

# BUGS
#  - victory doesn't work

# TEST CASES
#  - builder - select pile collision
#  - grabbing resource - is there something which can be grabbed?

def main():
    random.seed(time.time())
    game = Game()
    game.play()

if __name__ == '__main__':
    main()
