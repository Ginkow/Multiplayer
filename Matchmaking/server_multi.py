from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

wait_player = []
game = {}
names = {}
sid_to_player = {}
player_to_sid = {}

@app.route('/')
def index():
    return "Matchmaking en ligne"

@socket.on('connect')
def handle_connect():
    print(f"{request.sid} connecté")


@socket.on('disconnect')
def handle_disconnect():
    print(f"{request.sid} disconnecté")
    if request.sid in wait_player:
        wait_player.remove(request.sid)
        names.pop(request.sid)
    
@socket.on('waiting_room')
def handle_waiting_room(data):
    """Permet de rejoindre la salle d'attente et lorsqu'il y a 2 joueurs, de les faire jouer ensemble"""
    pseudo = data.get('pseudo', '???')
    names[request.sid] = pseudo
    wait_player.append(request.sid)
    print(f"Waiting room: {request.sid}")
    
    if len(wait_player) >= 2:
        player1, player2 = wait_player.pop(0), wait_player.pop(0)
        players = [player1, player2]
        random.shuffle(players)
        
        id_game = f"game_{random.randint(1000, 9999)}"
        game[id_game] = players
        
        symbol_player = {players[0]: "X", players[1]: "O"}
        for player in players:
            join_room(id_game, sid=player)	
            oppenent_id = players[1] if player == players[0] else players[0]
            emit('match_found', {'id_game': id_game, 'opponent': names[oppenent_id], 'symbol': symbol_player[player]}, room=player)
        
        print(f"Match found: {players[0]} vs {players[1]} in game {id_game}")
    else:
        emit('waiting_room', {'status': 'waiting'}, room=request.sid)
        
@socket.on('game_over')
def handle_game_over(data):
    """Enregistre le result de la partie dans le serveur de sauvegarde"""
    id_game = data.get['id_game']
    winner = data.get['winner']
    
    print(f"Game over: {id_game} - Winner: {winner}")
    
@socket.on('join_game')
def handle_join_game(data):
    id_game = data['id_game']
    id_player = data['id_player']

    if id_game not in game:
        game[id_game] = []

    if id_player not in game[id_game] and len(game[id_game]) < 2:
        game[id_game].append(id_player)
        print(f"[JOIN] Player {id_player} joined {id_game}")

    if len(game[id_game]) == 2:
        socket.emit('your_turn', room=request.sid)


@socket.on('play')
def handle_play(data):

    id_game = data['id_game']
    index = data['index']
    symbol = data['symbol']
    id_player = data['id_player']
    
    print(f"[DEBUG] {id_player} joue {symbol} à la case {index} (game {id_game})")

    # Envoyer le coup à l'adversaire
    for player in game[id_game]:
        sid = player_to_sid.get(player)
        if player != request.sid:
            print(f"Reçu coup adverse : {symbol} sur case {index}")
            socket.emit('opponent_move', {'index': index, 'symbol': symbol}, room=sid)
        else:
            print(f"Reçu coup player : {symbol} sur case {index}")
            socket.emit('your_turn', room=sid)  # Redonne la main après réception du coup

    
if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=6969, debug=True, allow_unsafe_werkzeug=True)