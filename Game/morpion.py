import tkinter as tk
import socketio
import sys
import requests as request
import subprocess
import os
import socket
import webbrowser

def get_local_ip():
    """Récupère automatiquement l'adresse IP locale de la machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connexion factice pour récupérer l'IP de la machine
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# --- Récupération des arguments ---
if len(sys.argv) >= 7:
    id_game = sys.argv[1]
    opponent = sys.argv[2]
    player_symbol = sys.argv[3]
    server_url = sys.argv[4]
    id_player = sys.argv[5]
    pseudo = sys.argv[6]
else:
    id_game = "test"
    opponent = "unknown"
    player_symbol = "X"
    server_url = "http://localhost:6969"
    pseudo = " "

# --- Connexion SocketIO ---
sio = socketio.Client()
sio.connect(server_url)
save_url = f"http://{get_local_ip()}:7070"


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
        if not game_over:
            your_turn = False
            turn_ennemies = True
            status_label.config(text="En attente de l'adversaire...")
    
    if game_over:
        return

def disable_click():
    canvas.unbind("<Button-1>")
    
def clear_action_buttons():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] in ["Retour au menu", "Rejouer"]:
            widget.destroy()


def check_winner():
    global game_over
    if game_over:
        return
    
    win_conditions = [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != " ":
            winner = board[a]
            game_over = True
            clear_action_buttons()
            if winner == player_symbol:
                status_label.config(text="Victoire !")
            else:
                status_label.config(text="Défaite !")
            if winner == player_symbol:
                save_game(pseudo)
            disable_click()
            
            # Bouton Historique de partie
            history_btn = tk.Button(root, text="Voir historique", command=lambda: webbrowser.open(f"{save_url}/save?pseudo={pseudo}"))
            history_btn.pack(pady=5)
            
            # Bouton Rejouer
            replay_btn = tk.Button(root, text="Rejouer", command=replay)
            replay_btn.pack(pady=5)

            # Bouton Retour
            back_btn = tk.Button(root, text="Retour au menu", command=back)
            back_btn.pack(pady=5)
            return

    if " " not in board:
        game_over = True
        clear_action_buttons()
        status_label.config(text="Match nul ! Voulez-vous rejouer ?")
        save_game(pseudo)
        
        # Bouton Historique de partie
        history_btn = tk.Button(root, text="Voir historique", command=lambda: webbrowser.open(f"{save_url}/save?pseudo={pseudo}"))
        history_btn.pack(pady=5)

        # Bouton Rejouer
        replay_btn = tk.Button(root, text="Rejouer", command=replay)
        replay_btn.pack(pady=5)

        # Bouton Retour
        back_btn = tk.Button(root, text="Retour au menu", command=back)
        back_btn.pack(pady=5)
        return


def save_game(winner_pseudo):
    try:
        request.post(f"{save_url}", json= {
            'id_game': id_game,
            'winner': winner_pseudo,
            'opponent': opponent,
            'player': pseudo
        })
        print(f"Partie {id_game} enregistrée avec le gagnant : {winner_pseudo}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la partie : {e}")
        
def reset():
    global board, your_turn, game_over
    canvas.delete('all')
    board = [" " for _ in range(9)]
    your_turn = (player_symbol == "X")
    game_over = False
    draw_board()
    clear_action_buttons()
    canvas.bind("<Button-1>", click)
    status_label.config(text="Nouvelle Partie. A toi de jouer" if your_turn else "Attendez que l adversaire joue...")

# --- Réseau : événements SocketIO ---
@sio.event
def connect():
    print("Connecté au serveur")
    sio.emit('join_game', {'id_game': id_game, 'id_player': id_player})

@sio.on('your_turn')
def on_your_turn():
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
    if not game_over:
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

def replay():
    clear_action_buttons()
    reset()


root.mainloop()