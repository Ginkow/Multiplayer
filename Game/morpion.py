import tkinter as tk
import socketio
import sys

# --- Récupération des arguments ---
if len(sys.argv) >= 4:
    id_game = sys.argv[1]
    opponent = sys.argv[2]
    server_url = sys.argv[3]
else:
    id_game = "test"
    opponent = "unknown"
    server_url = "http://localhost:6969"

# --- Connexion SocketIO ---
sio = socketio.Client()
sio.connect(server_url)

# --- Variables de jeu ---
root = tk.Tk()
root.title(f"Morpion - Partie {id_game} contre {opponent}")
board = [" " for _ in range(9)]
buttons = []
player_symbol = "X"
your_turn = False


# --- Logique de jeu ---
def make_move(index):
    global your_turn
    if board[index] == " " and your_turn:
        board[index] = player_symbol
        update_ui()
        sio.emit('play', {
            'id_game': id_game,
            'index': index,
            'symbol': player_symbol
        })
        check_winner()
        your_turn = False

def update_ui():
    for i in range(9):
        buttons[i].config(text=board[i])

def check_winner():
    win_conditions = [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != " ":
            print(f"Le joueur {board[a]} a gagné !")
            root.destroy()

def create_grid():
    for i in range(9):
        btn = tk.Button(root, text=" ", width=10, height=3, font=("Arial", 20),
                        command=lambda i=i: make_move(i))
        btn.grid(row=i//3, column=i%3)
        buttons.append(btn)


# --- Gestion des événements réseau ---
@sio.event
def connect():
    print("Connecté au serveur")
    sio.emit('join_game', {'id_game': id_game})

@sio.on('your_turn')
def on_your_turn(data):
    global your_turn
    your_turn = True
    print("C’est ton tour !")

@sio.on('opponent_move')
def on_opponent_move(data):
    index = data['index']
    symbol = data['symbol']
    board[index] = symbol
    update_ui()
    check_winner()

# --- Lancement du jeu ---
create_grid()
root.mainloop()
