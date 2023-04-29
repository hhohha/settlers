import random
import time
from game import Game

# TODOS
#  - exchange own resources 3:1
#  - use fleets
#  - use mint
#  - implement card events
#  - implement action cards
#  - implement protective cards
#  - implement AI

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
