import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://127.0.0.1:8080"  # À adapter si besoin

class AuthFrame(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.mode = "login"  # ou "register"
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Authentification", font=("Arial", 16)).pack(pady=10)
        self.username_entry = self._labeled_entry("Nom d'utilisateur")
        self.password_entry = self._labeled_entry("Mot de passe", show="*")
        if self.mode == "register":
            self.email_entry = self._labeled_entry("Email (optionnel)")
        tk.Button(self, text="Connexion" if self.mode == "login" else "Inscription",
                    command=self.login if self.mode == "login" else self.register,
                    width=20).pack(pady=10)
        tk.Button(self, text="Créer un compte" if self.mode == "login" else "J'ai déjà un compte",
                    command=self.toggle_mode, fg="blue", relief="flat").pack()

    def _labeled_entry(self, label, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label, width=18, anchor="w").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def toggle_mode(self):
        self.mode = "register" if self.mode == "login" else "login"
        self.build_ui()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        try:
            resp = requests.post(f"{SERVER_URL}/api/login/", json={
                "username": username,
                "password": password
            })
            if resp.status_code == 200:
                user_data = resp.json()
                self.on_login_success(user_data)
            else:
                messagebox.showerror("Erreur", resp.json().get("detail", "Connexion échouée."))
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion au serveur impossible.\n{e}")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get() if hasattr(self, "email_entry") else ""
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        try:
            resp = requests.post(f"{SERVER_URL}/api/register/", json={
                "username": username,
                "password": password,
                "email": email
            })
            if resp.status_code == 201:
                messagebox.showinfo("Succès", "Inscription réussie, connectez-vous.")
                self.toggle_mode()
            else:
                messagebox.showerror("Erreur", resp.json().get("detail", "Inscription échouée."))
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion au serveur impossible.\n{e}")