const API_URL = 'http://' + document.location.hostname + ':8000/'

function addPlayer(playerName) {
  var url = new URL(API_URL)
  url.pathname += 'player'
  url.searchParams.append('player_name', playerName)
  console.log(url,'url')
  fetch(url)
    .then(res=>console.log(res))
}