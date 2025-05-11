import tkinter as tk
import uuid
import subprocess # Permet de lance un autre script python
import socketio
import os
import sys

id_player = str(uuid.uuid4()) # Génère un ID unique pour chaque player
url = "http://192.168.1.129:6969" # URL du serveur de matchmaking
sio = socketio.Client()
pseudo = ""

# Interface Matchmaking
window = tk.Tk()
window.title("Matchmaking")
window.geometry("600x400")
name = tk.StringVar(window)

label = tk.Label(window, text="Choose your username :")
label.pack(pady=(20, 5))
tk.Entry(window, textvariable=name).pack(pady=30)

search_btn = tk.Button(window, text="Searching for a match...")
search_btn.pack(pady=20)

cancel_btn = tk.Button(window, text="Cancel", command=window.destroy)
cancel_btn.pack(pady=20)

# Événements Socket.IO
@sio.event
def connect():
    print("Connected to matchmaking server.")
    # Envoie une requête pour rejoindre la salle d'attente
    sio.emit("waiting_room", {"id_player": id_player, "pseudo": pseudo})

@sio.event
def disconnect():
    print("Disconnected from server.")
    
# def start_match(id_game, opponent, symbol):
#     """Lance le serveur de matchmaking."""
#     print(f" Lancement du morpion contre {opponent} dans la partie {id_game}")
#     subprocess.Popen(['python', 'Game/morpion.py', id_game, opponent, symbol, url]) # Lance le jeu de morpion avec l'ID de la partie et l'adversaire
#     window.destroy()
    
def start_match(id_game, opponent, symbol):
    subprocess.Popen([
        sys.executable,
        os.path.join('Game', 'morpion.py'),
        str(id_game), str(opponent), str(symbol), str(url)
    ])
    window.destroy()

@sio.on("match_found")
def check_match(data):
    """Vérifie si un match a été trouvé."""
    id_game = data["id_game"]
    opponent = data["opponent"]
    symbol = data["symbol"]
    print(f"Match found with {opponent} in game {id_game}")
    label.config(text="Match found! Launching the game...")
    start_match(id_game, opponent, symbol)
    
@sio.on("waiting_room")
def wait_room(data):
    print(" Waiting for another player...")
    
def start_search():
    """Démarre la recherche de partie après saisie du pseudo"""
    global pseudo
    pseudo = name.get().strip() or "Invited"
    try:
        sio.connect(url)        # la connexion ne se fait qu’ici
    except Exception as e:
        print(f"Connection error: {e}")

search_btn.config(command=start_search)


# Connexion au serveur Socket.IO
# try:
#     sio.connect(url)
# except Exception as e:
#     print(f"Connection error: {e}")
#     label.config(text="Unable to connect to the matchmaking server.")

window.mainloop()  # Démarre la boucle principale de l'interface graphique