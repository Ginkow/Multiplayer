from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# resultat = []

@app.route('/', methods=['POST'])
def save_game():
    data = request.get_json()
    id_game = data.get('id_game')
    winner = data.get('winner')
    opponent = data.get('opponent')
    player = data.get('player')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    victoire = 0
    if winner == player:
        victoire = 1
    defaite = 0
    
    try:
        conn = sqlite3.connect("Data/DB.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT 1 FROM morpion WHERE id_game = ? AND player = ?''', (id_game, player))
        cursor.execute('''INSERT INTO morpion (id_game, player, opponent, victoire, defaite, timestamp) VALUES (?, ?, ?, ?, ?, ?)''', (id_game, player, opponent, victoire, defaite, timestamp))
        conn.commit()
        conn.close()
        print(f"Game saved: {id_game} - Winner: {winner}")
        return jsonify({'status': 'saved'}), 200
    except Exception as e:
        print(f'[ERREUR DB] {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500
        

@app.route('/save', methods=['GET'])
def games_liste():
    pseudo_local = request.args.get('pseudo', '')
    """Affiche tous les résultats des parties depuis la base de données"""
    html = "<h2>Historique des parties</h2><ul style='font-family:Arial;'>"
    try:
        conn = sqlite3.connect("Data/DB.db")
        cursor = conn.cursor()
        if cursor.fetchone():
            return jsonify({'status': 'already_saved'}), 200
        cursor.execute('SELECT player, opponent, victoire, timestamp FROM morpion ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()

        for player, opponent, victoire, timestamp in results:
            if player == pseudo_local:
                player_display = f"{player} 👤"
            else:
                player_display = player

            if opponent == pseudo_local:
                opponent_display = f"{opponent} 👤"
            else:
                opponent_display = opponent
            
            if victoire == 1:
                if player == pseudo_local:
                    html += f"<li>victoire {player_display} 1 - 0 {opponent_display} — {timestamp}</li>"
                else:
                    html += f"<li>défaite {opponent_display} 0 - 1 {player_display} — {timestamp}</li>"
            elif victoire == 0:
                html += f"<li>match nul entre {player_display} et {opponent_display} — {timestamp}</li>"

        html += "</ul>"
        return html
    except Exception as e:
        return f"<p>Erreur lors de la récupération des parties : {e}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070, debug=True)
