import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://127.0.0.1:8080"  # À adapter si besoin

class StatsFrame(tk.Frame):
    def __init__(self, master, user, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.build_ui()
        self.load_stats()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Button(self, text="Retour menu", command=self.on_back).pack(anchor="nw", padx=10, pady=5)
        self.title = tk.Label(self, text="Profil & Statistiques", font=("Arial", 16))
        self.title.pack(pady=10)
        self.info = tk.Label(self, text="Chargement...", font=("Arial", 12))
        self.info.pack(pady=10)
        self.stats = tk.Label(self, text="", font=("Arial", 11))
        self.stats.pack(pady=10)

    def load_stats(self):
        try:
            resp = requests.get(f"{SERVER_URL}/api/stats/{self.user['username']}/")
            if resp.status_code == 200:
                data = resp.json()
                self.info.config(text=f"Utilisateur : {data.get('username', self.user['username'])}\nEmail : {data.get('email', '')}")
                self.stats.config(
                    text=f"Parties jouées : {data.get('games_played', 0)}\n"
                            f"Victoires : {data.get('games_won', 0)}\n"
                            f"Défaites : {data.get('games_lost', 0)}\n"
                            f"Égalités : {data.get('games_draw', 0)}"
                )
            else:
                self.info.config(text="Impossible de charger les statistiques.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des stats :\n{e}")
            self.info.config(text="Erreur de connexion.")
