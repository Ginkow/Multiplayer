from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

wait_player = []
game = {}
names = {}

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
    join_room(id_game)
    print(f"{request.sid} a rejoint la partie {id_game}")
    
    if id_game not in game:
        print(f"Erreur : partie {id_game} inconnue dans 'game'")
        return
        
    if request.sid not in game[id_game]:
        game[id_game].append(request.sid)

    # Premier joueur reçoit le tour
    if len(game[id_game]) == 2:
        socket.emit('your_turn', room=game[id_game][0])

@socket.on('play')
def handle_play(data):
    id_game = data['id_game']
    index = data['index']
    symbol = data['symbol']

    # Envoyer le coup à l'adversaire
    for player in game[id_game]:
        if player != request.sid:
            socket.emit('opponent_move', {'index': index, 'symbol': symbol}, room=player)
        else:
            socket.emit('your_turn', room=player)  # Redonne la main après réception du coup

    
if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=6969, debug=True, allow_unsafe_werkzeug=True)
