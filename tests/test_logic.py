import sys

sys.path.append('./assets')

from game import Inegleit

test = Inegleit(seed=1)

id1 = test.add_player('Bene')
id2 = test.add_player('Lara')
id3 = test.add_player('Thilo')

test.start_game()

ids = [id1, id2, id3]

for uid in ids:
    test.deal_cards(uid, 7) 
    print(test.get_cards(uid))

test.get_active_player()
print("top card", test.get_top_card())

# top card is red 8
test.event_play_card(0, 8) # [0] plays red 4
test.event_play_black_card(1, 104) # [1] plays black +4
test.event_choose_color(1, "red")



