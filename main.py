import random
import time
from game import Game

# TODOS
#  - implement AI
#  - voluntarily remove card from board

# TEST CASES
#  - builder - select pile collision
#  - grabbing resource - is there something which can be grabbed?

def main():
    random.seed(time.time())
    game = Game()
    game.play()

if __name__ == '__main__':
    main()
