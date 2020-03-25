# uno_backend
online uno backend

# Routes @'/game/'

## POST 'game/add_player'
Description:
 - Adds a player with the given name to the current game instance
 
Query parameter: 
 - player_name: str

Returns:
 - JSON {"name": player_name, "uid": unique_player_id}

## GET 'game/start_game' //should be POST
Description:
 - Starts a new game instance
 
Query parameter: 
 - None
 
Returns:
 - None
 
## POST 'game/deal_cards'
Query parameter: 
 - player_id: str 
 
## GET 'game/turn'
Description:
 - Returns whose turn it is
 
Query parameter:
 - None
 
Returns: 
 - player_id: int // should return  - JSON {"name": player_name, "uid": unique_player_id}
 
## GET 'game/cards'
Description:
 - Returns a list of card dictionaries belonging to player
 
Query parameter:
 - player_id: int
 
Returns:
 - JSON [{ "id": id, "color": color,"number": number } ... ] 
