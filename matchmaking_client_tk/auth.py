import tkinter as tk
from tkinter import messagebox
import requests

SERVER_URL = "http://127.0.0.1:8080"  # À adapter si besoin

class AuthFrame(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master, bg="#f5f6fa")
        self.on_login_success = on_login_success
        self.mode = "login"  # ou "register"
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        card = tk.Frame(self, bg="white", bd=2, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=320 if self.mode == "register" else 260)

        tk.Label(card, text="Matchmaking", font=("Arial", 18, "bold"), fg="#0d6efd", bg="white").pack(pady=(18, 2))
        tk.Label(card, text="Authentification", font=("Arial", 13), fg="#555", bg="white").pack(pady=(0, 12))

        self.username_entry = self._labeled_entry(card, "Nom d'utilisateur")
        self.password_entry = self._labeled_entry(card, "Mot de passe", show="*")
        if self.mode == "register":
            self.email_entry = self._labeled_entry(card, "Email (optionnel)")

        btn_color = "#0d6efd" if self.mode == "login" else "#198754"
        btn_text = "Connexion" if self.mode == "login" else "Inscription"
        action_btn = tk.Button(card, text=btn_text, command=self.login if self.mode == "login" else self.register,
                                width=22, bg=btn_color, fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", activebackground="#0056b3")
        action_btn.pack(pady=12)

        switch_text = "Créer un compte" if self.mode == "login" else "J'ai déjà un compte"
        switch_btn = tk.Button(card, text=switch_text, command=self.toggle_mode, fg="#0d6efd", bg="white",
                                relief="flat", font=("Arial", 10, "underline"), cursor="hand2", activeforeground="#198754")
        switch_btn.pack()

    def _labeled_entry(self, parent, label, show=None):
        frame = tk.Frame(parent, bg="white")
        frame.pack(pady=6, padx=18, fill="x")
        tk.Label(frame, text=label, width=16, anchor="w", bg="white", fg="#444", font=("Arial", 10)).pack(side="left")
        entry = tk.Entry(frame, show=show, font=("Arial", 11), relief="solid", bd=1, highlightthickness=1, highlightcolor="#0d6efd")
        entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
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