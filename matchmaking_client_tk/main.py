import tkinter as tk
from auth import AuthFrame
from morpion import MorpionFrame
from stats import StatsFrame
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.info("Démarrage de l'application Tkinter.")
        self.title("Client Matchmaking - Morpion")
        self.geometry("400x500")
        self.resizable(False, False)
        self.current_user = None
        self.show_auth()

    def show_auth(self):
        logging.info("Affichage de l'écran d'authentification.")
        self.clear()
        self.auth_frame = AuthFrame(self, self.on_login_success)
        self.auth_frame.pack(fill="both", expand=True)

    def on_login_success(self, user_data):
        logging.info(f"Connexion réussie pour l'utilisateur : {user_data.get('username')}")
        self.current_user = user_data
        self.show_menu()

    def show_menu(self):
        logging.info(f"Affichage du menu principal pour l'utilisateur : {self.current_user.get('username')}")
        self.clear()
        menu = tk.Frame(self)
        menu.pack(fill="both", expand=True)
        tk.Label(menu, text=f"Bienvenue {self.current_user['username']}", font=("Arial", 16)).pack(pady=20)
        tk.Button(menu, text="Jouer au Morpion", command=self.show_morpion, width=25).pack(pady=10)
        tk.Button(menu, text="Statistiques & Profil", command=self.show_stats, width=25).pack(pady=10)
        tk.Button(menu, text="Déconnexion", command=self.logout, width=25).pack(pady=10)

    def show_morpion(self):
        logging.info(f"L'utilisateur {self.current_user.get('username')} lance une partie de morpion.")
        self.clear()
        self.morpion_frame = MorpionFrame(self, self.current_user, self.show_menu)
        self.morpion_frame.pack(fill="both", expand=True)

    def show_stats(self):
        logging.info(f"L'utilisateur {self.current_user.get('username')} consulte ses statistiques.")
        self.clear()
        self.stats_frame = StatsFrame(self, self.current_user, self.show_menu)
        self.stats_frame.pack(fill="both", expand=True)

    def logout(self):
        logging.info(f"L'utilisateur {self.current_user.get('username')} s'est déconnecté.")
        self.current_user = None
        self.show_auth()

    def clear(self):
        logging.debug("Nettoyage de la fenêtre principale.")
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    logging.info("Lancement du client Matchmaking Tkinter.")
    app = MainApp()
    app.mainloop()