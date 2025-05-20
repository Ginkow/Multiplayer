from flask import Flask, request, jsonify
from datetime import datetime

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
    
    for r in resultat:
        if r['id_game'] == id_game and r['winner'] == winner:
            return jsonify({'status': 'already_saved'}), 200
        
    resultat.append({'id_game': id_game, 'winner': winner, 'opponent': opponent, 'player': player, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    print(f"Game saved: {id_game} - Winner: {winner}")
    return jsonify({'status': 'saved'}), 200

@app.route('/save', methods=['GET'])
def games_liste():
    """Affiche tous les résultats des parties sous forme HTML lisible"""
    html = "<h2>Historique des parties</h2><ul style='font-family:Arial;'>"
    for game in resultat:
        if game['winner'] == game['player']:
            gagnant = game['player']
            perdant = game['opponent']
        else:
            gagnant = game['opponent']
            perdant = game['player']
        date = game.get('date', 'Inconnue')
        html += f"<li>victoire {gagnant} 1 - 0 {perdant} défaite — {date}</li>"
    html += "</ul>"
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070, debug=True)
