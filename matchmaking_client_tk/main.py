import tkinter as tk
from auth import AuthFrame
from morpion import MorpionFrame
from morpion_ia import MorpionIAFrame
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
        self.geometry("400x520")
        self.resizable(False, False)
        self.configure(bg="#f5f6fa")
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
        menu = tk.Frame(self, bg="white", bd=2, relief="groove")
        menu.place(relx=0.5, rely=0.5, anchor="center", width=340, height=340)
        tk.Label(menu, text="Matchmaking Morpion", font=("Arial", 17, "bold"), fg="#0d6efd", bg="white").pack(pady=(22, 2))
        tk.Label(menu, text=f"Bienvenue {self.current_user['username']}", font=("Arial", 13), fg="#444", bg="white").pack(pady=(0, 18))
        tk.Button(menu, text="Jouer", command=self.show_play_choice, width=25, height=2, bg="#0d6efd", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#0056b3").pack(pady=8)
        tk.Button(menu, text="Statistiques & Profil", command=self.show_stats, width=25, height=2, bg="#198754", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#145c32").pack(pady=8)
        tk.Button(menu, text="Déconnexion", command=self.logout, width=25, height=2, bg="#dc3545", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#a71d2a").pack(pady=8)

    def show_play_choice(self):
        self.clear()
        frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=340, height=260)
        tk.Label(frame, text="Choisissez votre mode de jeu :", font=("Arial", 14, "bold"), fg="#0d6efd", bg="white").pack(pady=(25, 18))
        tk.Button(frame, text="Jouer contre un autre utilisateur", command=self.show_morpion, width=30, bg="#0d6efd", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#0056b3").pack(pady=7)
        tk.Button(frame, text="Jouer contre l'ordinateur", command=self.show_morpion_ia, width=30, bg="#198754", fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#145c32").pack(pady=7)
        tk.Button(frame, text="Retour au menu", command=self.show_menu, width=30, bg="#adb5bd", fg="#222", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#6c757d").pack(pady=(18, 0))

    def show_morpion(self):
        logging.info(f"L'utilisateur {self.current_user.get('username')} lance une partie de morpion en ligne.")
        self.clear()
        self.morpion_frame = MorpionFrame(self, self.current_user, self.show_menu)
        self.morpion_frame.pack(fill="both", expand=True)

    def show_morpion_ia(self):
        logging.info(f"L'utilisateur {self.current_user.get('username')} lance une partie contre l'ordinateur.")
        self.clear()
        self.morpion_ia_frame = MorpionIAFrame(self, self.current_user, self.show_menu)
        self.morpion_ia_frame.pack(fill="both", expand=True)

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