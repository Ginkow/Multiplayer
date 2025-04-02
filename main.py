import subprocess
import time

# Lance le matchmaking
server_matchmaking = subprocess.Popen(['python', 'Matchmaking/server_multi.py'])
time.sleep(2)

# Lance le serveur de sauvegarde
# sauvegarde = subprocess.Popen(['python', 'Sauve/server_sauvegarde.py'])
# time.sleep(5)

try:
    # Attendre que les processus se terminent
    print("Serveurs en cours d'exécution...")
    server_matchmaking.wait()
    # sauvegarde.wait()
except KeyboardInterrupt:
    print("Arrêt des serveurs...")
    server_matchmaking.terminate()
    # sauvegarde.terminate()