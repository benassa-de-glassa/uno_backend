import csv

""" 
Creates a csv file listing all cards and their IDs for future reference 
Not needed by the API!
"""

allcards = []
N = 0
for color in ["red", "green", "blue", "yellow"]:
    # add a single zero per color
    allcards.append({"id": N, "color": color, "number":0, "name":"number"})
    N += 1
    # add two of each kind
    for i in range(9):
        allcards.append({"id": N, "color": color, "number":i+1, "name":"number"})
        allcards.append({"id": N+1, "color": color, "number":i+1, "name":"number"})
        N += 2
    
    for specialname in ["reverse", "skip", "+2"]:
        allcards.append({"id": N, "color": color, "number": i+1, "name": specialname})
        allcards.append({"id": N+1, "color": color, "number": i+1, "name": specialname})
        N += 2

# creates the black cards
for i in range(4):
        allcards.append({"id": N, "color": "black", "number":0, "name": "wish"}) # choose color
        N += 1

for i in range(4):
        allcards.append({"id": N, "color": "black", "number":1, "name": "+4"}) # +4 card
        N += 1

with open("cards.csv", "w") as output_file:
    dict_writer = csv.DictWriter(output_file, allcards[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(allcards)
