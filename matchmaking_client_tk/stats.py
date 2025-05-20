import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://127.0.0.1:8080"  # À adapter si besoin

class StatsFrame(tk.Frame):
    def __init__(self, master, user, on_back):
        super().__init__(master, bg="#f5f6fa")
        self.user = user
        self.on_back = on_back
        self.build_ui()
        self.load_stats()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Carte profil
        profile_card = tk.Frame(self, bg="white", bd=2, relief="groove")
        profile_card.pack(pady=(20, 10), padx=30, fill="x")
        tk.Button(profile_card, text="Retour menu", command=self.on_back, bg="#adb5bd", fg="#222", font=("Arial", 10, "bold"),
                    relief="flat", cursor="hand2", activebackground="#6c757d").pack(anchor="nw", padx=10, pady=(10, 0))
        self.title = tk.Label(profile_card, text="Profil & Statistiques", font=("Arial", 16, "bold"), bg="white", fg="#0d6efd")
        self.title.pack(pady=(10, 2))
        self.info = tk.Label(profile_card, text="Chargement...", font=("Arial", 12), bg="white", fg="#444")
        self.info.pack(pady=(0, 10))
        # Carte stats
        self.stats_card = tk.Frame(self, bg="#e9ecef", bd=0, relief="flat")
        self.stats_card.pack(pady=(5, 10), padx=30, fill="x")
        self.stats = tk.Label(self.stats_card, text="", font=("Arial", 12), bg="#e9ecef", fg="#222", justify="left")
        self.stats.pack(pady=12, padx=10)

    def load_stats(self):
        try:
            resp = requests.get(f"{SERVER_URL}/api/stats/{self.user['username']}/")
            if resp.status_code == 200:
                data = resp.json()
                self.info.config(
                    text=f"Utilisateur : {data.get('username', self.user['username'])}\nEmail : {data.get('email', '')}"
                )
                self.stats.config(
                    text=(
                        "Statistiques en ligne :\n"
                        f"  Parties jouées : {data.get('games_played', 0)}\n"
                        f"  Victoires : {data.get('games_won', 0)}\n"
                        f"  Défaites : {data.get('games_lost', 0)}\n"
                        f"  Égalités : {data.get('games_draw', 0)}\n\n"
                        "Statistiques contre l'ordinateur (toutes difficultés) :\n"
                        f"  Victoires IA : {data.get('ia_wins', 0)}\n"
                        f"  Défaites IA : {data.get('ia_loses', 0)}\n"
                        f"  Égalités IA : {data.get('ia_draws', 0)}\n\n"
                        "Détail par difficulté :\n"
                        f"  Facile   - V: {data.get('ia_wins_facile', 0)} | D: {data.get('ia_loses_facile', 0)} | É: {data.get('ia_draws_facile', 0)}\n"
                        f"  Moyen    - V: {data.get('ia_wins_moyen', 0)} | D: {data.get('ia_loses_moyen', 0)} | É: {data.get('ia_draws_moyen', 0)}\n"
                        f"  Difficile- V: {data.get('ia_wins_difficile', 0)} | D: {data.get('ia_loses_difficile', 0)} | É: {data.get('ia_draws_difficile', 0)}"
                    )
                )
            else:
                self.info.config(text="Impossible de charger les statistiques.")
                self.stats.config(text="")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des stats :\n{e}")
            self.info.config(text="Erreur de connexion.")
            self.stats.config(text="")
