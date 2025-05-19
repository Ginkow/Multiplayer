from flask import Flask, request, jsonify

app = Flask(__name__)

resultat = []

@app.route('/', methods=['POST'])
def save_game():
    """Enregistre le résultat de la partie dans le serveur de sauvegarde"""
    data = request.get_json()
    id_game = data.get('id_game')
    winner = data.get('winner')
    opponent = data.get('opponent')
    player = data.get('player')
    
    resultat.append({'id_game': id_game, 'winner': winner, 'opponent': opponent, 'player': player})
    print(f"Game saved: {id_game} - Winner: {winner}")
    return jsonify({'status': 'saved'}), 200

@app.route('/games', methods=['GET'])
def games_liste():
    """Récupère tous les résultats des parties"""
    return jsonify(resultat)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070, debug=True)
