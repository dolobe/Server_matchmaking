# import tkinter as tk
# from tkinter import messagebox
# import threading
# import websocket
# import json
# import logging

# SERVER_WS_URL = "ws://127.0.0.1:8080/ws/matchmaking/"  # À adapter si besoin

# # Configuration du logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[logging.StreamHandler()]
# )

# class MorpionFrame(tk.Frame):
#     def __init__(self, master, user, on_back):
#         super().__init__(master)
#         self.user = user
#         self.on_back = on_back
#         self.ws = None
#         self.symbol = None
#         self.opponent_symbol = None
#         self.my_turn = False
#         self.opponent = None
#         self.match_id = None
#         self.score = {"Vous": 0, "Adversaire": 0, "Égalité": 0}
#         logging.info(f"Initialisation du MorpionFrame pour l'utilisateur {self.user['username']}")
#         self.build_ui()
#         self.connect_ws()

#     def build_ui(self):
#         logging.debug("Construction de l'interface du plateau de jeu.")
#         for widget in self.winfo_children():
#             widget.destroy()
#         tk.Button(self, text="Retour menu", command=self.on_back).pack(anchor="nw", padx=10, pady=5)
#         self.status = tk.Label(self, text="Connexion au serveur...", font=("Arial", 12))
#         self.status.pack(pady=10)
#         self.score_label = tk.Label(self, text=self.score_text(), font=("Arial", 11))
#         self.score_label.pack(pady=5)
#         self.board_frame = tk.Frame(self)
#         self.board_frame.pack(pady=10)
#         self.buttons = [[None for _ in range(3)] for _ in range(3)]
#         for i in range(3):
#             for j in range(3):
#                 btn = tk.Button(self.board_frame, text="", width=5, height=2, font=("Arial", 20),
#                                 command=lambda x=i, y=j: self.play_move(x, y), state="disabled")
#                 btn.grid(row=i, column=j, padx=3, pady=3)
#                 self.buttons[i][j] = btn
#         logging.info("Interface du plateau de jeu construite.")

#     def score_text(self):
#         return f"Score - Vous: {self.score['Vous']} | Adversaire: {self.score['Adversaire']} | Égalité: {self.score['Égalité']}"

#     def connect_ws(self):
#         logging.info("Connexion WebSocket en cours...")
#         def run_ws():
#             self.ws = websocket.WebSocketApp(
#                 SERVER_WS_URL,
#                 on_open=self.on_open,
#                 on_message=self.on_message,
#                 on_error=self.on_error,
#                 on_close=self.on_close
#             )
#             self.ws.run_forever()
#         threading.Thread(target=run_ws, daemon=True).start()

#     def on_open(self, ws):
#         logging.info(f"WebSocket ouverte pour {self.user['username']}. Envoi de join_queue.")
#         join_msg = json.dumps({"action": "join_queue", "username": self.user["username"]})
#         ws.send(join_msg)
#         self.set_status("En file d'attente...")

#     def on_message(self, ws, message):
#         logging.info(f"Message WebSocket reçu : {message}")
#         data = json.loads(message)
#         action = data.get("action")
#         if action == "start_match":
#             self.opponent = data.get("opponent")
#             self.symbol = data.get("symbol")
#             self.opponent_symbol = "O" if self.symbol == "X" else "X"
#             self.match_id = data.get("match_id")
#             self.my_turn = data.get("your_turn", False)
#             logging.info(f"Début du match contre {self.opponent} (symbole: {self.symbol}, à moi de jouer: {self.my_turn})")
#             self.reset_board()
#             self.set_status(f"Match contre {self.opponent} - {'À vous de jouer !' if self.my_turn else 'En attente du coup adverse...'}")
#             self.enable_board(self.my_turn)
#         elif action == "opponent_move":
#             x, y = data.get("x"), data.get("y")
#             symbol = data.get("symbol", self.opponent_symbol)
#             logging.info(f"Coup adverse reçu : ({x}, {y}) avec symbole {symbol}")
#             self.buttons[x][y].config(text=symbol, state="disabled")
#             self.my_turn = True
#             self.set_status("À vous de jouer !")
#             self.enable_board(True)
#         elif action == "end_match":
#             winner = data.get("winner")
#             if winner == self.user["username"]:
#                 self.score["Vous"] += 1
#                 msg = "Vous avez gagné !"
#                 logging.info("Victoire de l'utilisateur.")
#             elif winner == "draw":
#                 self.score["Égalité"] += 1
#                 msg = "Égalité !"
#                 logging.info("Match nul.")
#             else:
#                 self.score["Adversaire"] += 1
#                 msg = f"{self.opponent} a gagné !"
#                 logging.info("Défaite de l'utilisateur.")
#             self.set_status(msg)
#             self.score_label.config(text=self.score_text())
#             self.enable_board(False)
#             logging.info("Fin de match, préparation pour une nouvelle partie.")
#             self.after(2000, self.replay)
#         else:
#             logging.warning(f"Action WebSocket inconnue : {action}")

#     def play_move(self, x, y):
#         logging.info(f"Tentative de jouer en ({x}, {y}) par {self.user['username']}")
#         if not self.my_turn or self.buttons[x][y]["text"]:
#             logging.warning("Coup non autorisé (pas à votre tour ou case déjà prise).")
#             return
#         self.buttons[x][y].config(text=self.symbol, state="disabled")
#         self.my_turn = False
#         self.set_status("En attente du coup adverse...")
#         self.enable_board(False)
#         move_msg = json.dumps({"action": "play_move", "x": x, "y": y})
#         if self.ws:
#             logging.info(f"Envoi du coup au serveur : {move_msg}")
#             self.ws.send(move_msg)

#     def reset_board(self):
#         logging.info("Réinitialisation du plateau de jeu.")
#         for i in range(3):
#             for j in range(3):
#                 self.buttons[i][j].config(text="", state="disabled")
#         self.enable_board(self.my_turn)

#     def enable_board(self, enable):
#         logging.debug(f"{'Activation' if enable else 'Désactivation'} du plateau pour l'utilisateur.")
#         for i in range(3):
#             for j in range(3):
#                 if not self.buttons[i][j]["text"]:
#                     self.buttons[i][j].config(state="normal" if enable else "disabled")

#     def set_status(self, msg):
#         logging.info(f"Changement de statut affiché : {msg}")
#         self.status.config(text=msg)

#     def replay(self):
#         logging.info("Nouvelle partie demandée, retour en file d'attente.")
#         self.set_status("Nouvelle partie... En attente d'un adversaire.")
#         self.reset_board()
#         if self.ws:
#             join_msg = json.dumps({"action": "join_queue", "username": self.user["username"]})
#             logging.info(f"Ré-envoi de join_queue : {join_msg}")
#             self.ws.send(join_msg)

#     def on_error(self, ws, error):
#         logging.error(f"Erreur WebSocket : {error}")
#         self.set_status("Erreur de connexion WebSocket.")
#         messagebox.showerror("Erreur", f"WebSocket: {error}")

#     def on_close(self, ws, close_status_code, close_msg):
#         logging.info(f"WebSocket fermée (code: {close_status_code}, msg: {close_msg})")
#         self.set_status("Connexion WebSocket fermée.")

import tkinter as tk
from tkinter import messagebox
import threading
import websocket
import json
import logging

SERVER_WS_URL = "ws://127.0.0.1:8080/ws/matchmaking/"  # À adapter si besoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class MorpionFrame(tk.Frame):
    def __init__(self, master, user, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.ws = None
        self.symbol = None
        self.opponent_symbol = None
        self.my_turn = False
        self.opponent = None
        self.match_id = None
        self.score = {"Vous": 0, "Adversaire": 0, "Égalité": 0}
        logging.info(f"Initialisation du MorpionFrame pour l'utilisateur {self.user['username']}")
        self.build_ui()
        self.connect_ws()

    def build_ui(self):
        logging.debug("Construction de l'interface du plateau de jeu.")
        for widget in self.winfo_children():
            widget.destroy()
        tk.Button(self, text="Retour menu", command=self.on_back).pack(anchor="nw", padx=10, pady=5)
        self.status = tk.Label(self, text="Connexion au serveur...", font=("Arial", 12))
        self.status.pack(pady=10)
        self.score_label = tk.Label(self, text=self.score_text(), font=("Arial", 11))
        self.score_label.pack(pady=5)
        self.board_frame = tk.Frame(self)
        self.board_frame.pack(pady=10)
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.board_frame, text="", width=5, height=2, font=("Arial", 20),
                                command=lambda x=i, y=j: self.play_move(x, y), state="disabled")
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.buttons[i][j] = btn
        logging.info("Interface du plateau de jeu construite.")

    def score_text(self):
        return f"Score - Vous: {self.score['Vous']} | Adversaire: {self.score['Adversaire']} | Égalité: {self.score['Égalité']}"

    def connect_ws(self):
        logging.info("Connexion WebSocket en cours...")
        def run_ws():
            self.ws = websocket.WebSocketApp(
                SERVER_WS_URL,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.run_forever()
        threading.Thread(target=run_ws, daemon=True).start()

    def on_open(self, ws):
        logging.info(f"WebSocket ouverte pour {self.user['username']}. Envoi de join_queue.")
        join_msg = json.dumps({"action": "join_queue", "username": self.user["username"]})
        ws.send(join_msg)
        self.set_status("En file d'attente...")

    def on_message(self, ws, message):
        logging.info(f"Message WebSocket reçu : {message}")
        data = json.loads(message)
        action = data.get("action")
        if action == "start_match":
            self.opponent = data.get("opponent")
            self.symbol = data.get("symbol")
            self.opponent_symbol = "O" if self.symbol == "X" else "X"
            self.match_id = data.get("match_id")
            self.my_turn = data.get("your_turn", False)
            logging.info(f"Début du match contre {self.opponent} (symbole: {self.symbol}, à moi de jouer: {self.my_turn})")
            self.reset_board()
            self.set_status(f"Match contre {self.opponent} - {'À vous de jouer !' if self.my_turn else 'En attente du coup adverse...'}")
            self.enable_board(self.my_turn)
        elif action == "opponent_move":
            x, y = data.get("x"), data.get("y")
            symbol = data.get("symbol", self.opponent_symbol)
            logging.info(f"Coup adverse reçu : ({x}, {y}) avec symbole {symbol}")
            self.buttons[x][y].config(text=symbol, state="disabled")
            self.my_turn = True
            self.set_status("À vous de jouer !")
            self.enable_board(True)
        elif action == "end_match":
            winner = data.get("winner")
            if winner == self.user["username"]:
                self.score["Vous"] += 1
                msg = "Vous avez gagné !"
                logging.info("Victoire de l'utilisateur.")
            elif winner == "draw":
                self.score["Égalité"] += 1
                msg = "Égalité !"
                logging.info("Match nul.")
            else:
                self.score["Adversaire"] += 1
                msg = f"{self.opponent} a gagné !"
                logging.info("Défaite de l'utilisateur.")
            self.set_status(msg)
            self.score_label.config(text=self.score_text())
            self.enable_board(False)
            logging.info("Fin de match, préparation pour une nouvelle partie.")
            self.after(2000, self.replay)
        else:
            logging.warning(f"Action WebSocket inconnue : {action}")

    def play_move(self, x, y):
        logging.info(f"Tentative de jouer en ({x}, {y}) par {self.user['username']}")
        # On ne joue que si c'est notre tour ET la case est vide
        if not self.my_turn:
            logging.warning("Ce n'est pas votre tour.")
            return
        if self.buttons[x][y]["text"]:
            logging.warning("Case déjà prise.")
            return
        self.buttons[x][y].config(text=self.symbol, state="disabled")
        self.my_turn = False  # On ne peut plus jouer tant que l'adversaire n'a pas joué
        self.set_status("En attente du coup adverse...")
        self.enable_board(False)
        move_msg = json.dumps({"action": "play_move", "x": x, "y": y})
        if self.ws:
            logging.info(f"Envoi du coup au serveur : {move_msg}")
            self.ws.send(move_msg)

    def reset_board(self):
        logging.info("Réinitialisation du plateau de jeu.")
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state="disabled")
        self.enable_board(self.my_turn)

    def enable_board(self, enable):
        logging.debug(f"{'Activation' if enable else 'Désactivation'} du plateau pour l'utilisateur.")
        for i in range(3):
            for j in range(3):
                if not self.buttons[i][j]["text"]:
                    self.buttons[i][j].config(state="normal" if enable else "disabled")
                else:
                    self.buttons[i][j].config(state="disabled")

    def set_status(self, msg):
        logging.info(f"Changement de statut affiché : {msg}")
        self.status.config(text=msg)

    def replay(self):
        logging.info("Nouvelle partie demandée, retour en file d'attente.")
        self.set_status("Nouvelle partie... En attente d'un adversaire.")
        self.reset_board()
        if self.ws:
            join_msg = json.dumps({"action": "join_queue", "username": self.user["username"]})
            logging.info(f"Ré-envoi de join_queue : {join_msg}")
            self.ws.send(join_msg)

    def on_error(self, ws, error):
        logging.error(f"Erreur WebSocket : {error}")
        self.set_status("Erreur de connexion WebSocket.")
        messagebox.showerror("Erreur", f"WebSocket: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(f"WebSocket fermée (code: {close_status_code}, msg: {close_msg})")
        self.set_status("Connexion WebSocket fermée.")