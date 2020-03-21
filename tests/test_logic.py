import sys

sys.path.append('./assets')
from game import Inegleit

test = Inegleit()

test.add_player('Bene', 0)
test.add_player('Lara', 1)
test.add_player('Thilo', 2)

test.start_game()

c1 = test.players[0].hand

# print the hand of player 1
for c in c1:
    print(c)


