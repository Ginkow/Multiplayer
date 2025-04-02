import tkinter as tk
import uuid
import subprocess # Permet de lance un autre script python
import socketio

id_player = str(uuid.uuid4()) # Génère un ID unique pour chaque player
url = "http://192.168.1.129:6969" # URL du serveur de matchmaking
sio = socketio.Client()

# Interface Matchmaking
window = tk.Tk()
window.title("Matchmaking")
window.geometry("600x400")

label = tk.Label(window, text="Searching for a match...")
label.pack(pady=20)

button = tk.Button(window, text="Cancel", command=window.destroy)
button.pack(pady=20)

# Événements Socket.IO
@sio.event
def connect():
    print("Connected to matchmaking server.")
    # Envoie une requête pour rejoindre la salle d'attente
    sio.emit("waiting_room", {"id_player": id_player})

@sio.event
def disconnect():
    print("Disconnected from server.")
    
def start_match(id_game, opponent):
    """Lance le serveur de matchmaking."""
    print(f" Lancement du morpion contre {opponent} dans la partie {id_game}")
    subprocess.Popen(['python', '../Game/morpion.py', id_game, opponent, url]) # Lance le jeu de morpion avec l'ID de la partie et l'adversaire
    window.destroy()

@sio.on("match_found")
def check_match(data):
    """Vérifie si un match a été trouvé."""
    id_game = data["id_game"]
    opponent = data["opponent"]
    print(f"Match found with {opponent} in game {id_game}")
    label.config(text="Match found! Launching the game...")
    start_match(id_game, opponent)
    
@sio.on("waiting_room")
def wait_room(data):
    print(" Waiting for another player...")

# Connexion au serveur Socket.IO
try:
    sio.connect(url)
except Exception as e:
    print(f"Connection error: {e}")
    label.config(text="Unable to connect to the matchmaking server.")

window.mainloop()  # Démarre la boucle principale de l'interface graphique