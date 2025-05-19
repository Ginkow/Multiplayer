import tkinter as tk
import socketio
import sys
import requests as request
import subprocess
import os

# --- Récupération des arguments ---
if len(sys.argv) >= 6:
    id_game = sys.argv[1]
    opponent = sys.argv[2]
    player_symbol = sys.argv[3]
    server_url = sys.argv[4]
    id_player = sys.argv[5]
else:
    id_game = "test"
    opponent = "unknown"
    player_symbol = "X"
    server_url = "http://localhost:6969"

# --- Connexion SocketIO ---
sio = socketio.Client()
sio.connect(server_url)


# --- Variables de jeu ---
root = tk.Tk()
root.title(f"Morpion - Partie {id_game} contre {opponent}")
board = [" " for _ in range(9)]
your_turn = True
turn_ennemies = False
game_over = False

canvas_size = 300
cell_size = canvas_size // 3

canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
canvas.pack()

status_label = tk.Label(root)
status_label.pack(pady=10)

# --- Fonctions de dessin ---
def draw_board():
    for i in range(1, 3):
        # Lignes verticales
        canvas.create_line(i * cell_size, 0, i * cell_size, canvas_size, width=3)
        # Lignes horizontales
        canvas.create_line(0, i * cell_size, canvas_size, i * cell_size, width=3)

def draw_symbol(index, symbol):
    x0 = (index % 3) * cell_size + 20
    y0 = (index // 3) * cell_size + 20
    x1 = (index % 3 + 1) * cell_size - 20
    y1 = (index // 3 + 1) * cell_size - 20

    if symbol == "X":
        canvas.create_line(x0, y0, x1, y1, width=4)
        canvas.create_line(x0, y1, x1, y0, width=4)
    elif symbol == "O":
        canvas.create_oval(x0, y0, x1, y1, width=4)

# --- Logique de jeu ---
def click(event):
    global your_turn
    global turn_ennemies
    
    if not your_turn:
        status_label.config(text="C'est le tour de l'adversaire !")
        return

    col = event.x // cell_size
    row = event.y // cell_size
    index = row * 3 + col

    if board[index] == " ":
        board[index] = player_symbol
        draw_symbol(index, player_symbol)
        sio.emit('play', {
            'id_game': id_game,
            'index': index,
            'symbol': player_symbol,
            'id_player': id_player
        })
        check_winner()
        your_turn = False
        turn_ennemies = True
        status_label.config(text="En attente de l'adversaire...")
    
    if game_over:
        return

def check_winner():
    global game_over
    win_conditions = [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != " ":
            winner = board[a]
            status_label.config(text=f"Le joueur {winner} a gagné !")
            save_game(winner)
            game_over = True
            back_btn = tk.Button(root, text="Retour au menu", command=back)
            back_btn.pack(pady=10)


def save_game(winner):
    try:
        request.post(f"{server_url}/save", json={
            'id_game': id_game,
            'winner': winner,
            'opponent': opponent,
            'player': player_symbol
        })
        print(f"Partie {id_game} enregistrée avec le gagnant : {winner}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la partie : {e}")

# --- Réseau : événements SocketIO ---
@sio.event
def connect():
    print("Connecté au serveur")
    sio.emit('join_game', {'id_game': id_game, 'id_player': id_player})

@sio.on('your_turn')
def on_your_turn(data):
    global your_turn
    your_turn = True
    print("C’est ton tour !")
    status_label.config(text="À toi de jouer !")

@sio.on('opponent_move')
def on_opponent_move(data):
    index = data['index']
    symbol = data['symbol']
    board[index] = symbol
    draw_symbol(index, symbol)
    canvas.update()
    check_winner()
    
    global your_turn
    # global turn_ennemies
    # turn_ennemies = True
    your_turn = True
    status_label.config(text="À toi de jouer !")


# --- Lancement du jeu ---
draw_board()
canvas.bind("<Button-1>", click)

# Message initial pour le joueur O
if player_symbol == "O":
    status_label.config(text="Attendez que l'adversaire joue...")
else:
    status_label.config(text="À toi de jouer !")
    
def back():
    subprocess.Popen([
        sys.executable,
        os.path.join("Matchmaking", "salon_matchmaking.py")
    ])
    root.destroy()



root.mainloop()
