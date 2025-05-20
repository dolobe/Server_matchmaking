import tkinter as tk
from tkinter import messagebox
import random
import requests
import copy

SERVER_URL = "http://127.0.0.1:8080"  # À adapter si besoin

class MorpionIAFrame(tk.Frame):
    def __init__(self, master, user, on_back):
        super().__init__(master, bg="#f5f6fa")
        self.user = user
        self.on_back = on_back
        self.symbol = "X"
        self.ia_symbol = "O"
        self.my_turn = True
        self.score = {"Vous": 0, "Ordinateur": 0, "Égalité": 0}
        self.difficulty = tk.StringVar(value="facile")
        self.build_ui()
        self.reset_board()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Score card
        score_card = tk.Frame(self, bg="#0d6efd", bd=0, relief="ridge")
        score_card.pack(pady=(18, 8), padx=20, fill="x")
        self.score_label = tk.Label(score_card, text=self.score_text(), font=("Arial", 13, "bold"), bg="#0d6efd", fg="white")
        self.score_label.pack(pady=8)
        # Retour bouton
        tk.Button(self, text="Retour menu", command=self.on_back, bg="#adb5bd", fg="#222", font=("Arial", 10, "bold"),
                    relief="flat", cursor="hand2", activebackground="#6c757d").pack(anchor="nw", padx=18, pady=(0, 8))
        # Difficulté
        diff_frame = tk.Frame(self, bg="#f5f6fa")
        diff_frame.pack(pady=(0, 5))
        tk.Label(diff_frame, text="Difficulté :", font=("Arial", 11, "bold"), bg="#f5f6fa", fg="#0d6efd").pack(side="left")
        for diff in [("Facile", "facile"), ("Moyen", "moyen"), ("Difficile", "difficile")]:
            tk.Radiobutton(diff_frame, text=diff[0], variable=self.difficulty, value=diff[1],
                            font=("Arial", 10), bg="#f5f6fa", fg="#222", selectcolor="#b6d4fe",
                            command=self.reset_board).pack(side="left", padx=5)
        # Statut
        self.status = tk.Label(self, text="À vous de jouer !", font=("Arial", 12), bg="#f5f6fa", fg="#0d6efd")
        self.status.pack(pady=10)
        # Plateau
        board_card = tk.Frame(self, bg="white", bd=2, relief="groove")
        board_card.pack(pady=10)
        self.board_frame = tk.Frame(board_card, bg="white")
        self.board_frame.pack(padx=10, pady=10)
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.board_frame, text="", width=5, height=2, font=("Arial", 22, "bold"),
                                bg="#e9ecef", fg="#222", relief="ridge", bd=2,
                                activebackground="#b6d4fe", cursor="hand2",
                                command=lambda x=i, y=j: self.play_move(x, y))
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.buttons[i][j] = btn

    def score_text(self):
        return f"Score - Vous: {self.score['Vous']} | Ordinateur: {self.score['Ordinateur']} | Égalité: {self.score['Égalité']}"

    def reset_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state="normal", bg="#e9ecef")
        self.my_turn = True
        self.status.config(text="À vous de jouer !")

    def play_move(self, x, y):
        if not self.my_turn or self.buttons[x][y]["text"]:
            return
        self.buttons[x][y].config(text=self.symbol, state="disabled", bg="#b6d4fe")
        if self.check_winner(self.symbol):
            self.score["Vous"] += 1
            self.score_label.config(text=self.score_text())
            self.status.config(text="Vous avez gagné !")
            self.save_ia_match("win")
            messagebox.showinfo("Victoire", "Bravo, vous avez gagné !")
            self.reset_board()
            return
        elif self.is_draw():
            self.score["Égalité"] += 1
            self.score_label.config(text=self.score_text())
            self.status.config(text="Égalité !")
            self.save_ia_match("draw")
            messagebox.showinfo("Égalité", "Match nul !")
            self.reset_board()
            return
        self.my_turn = False
        self.status.config(text="Tour de l'ordinateur...")
        self.after(700, self.ia_move)

    def ia_move(self):
        difficulty = self.difficulty.get()
        if difficulty == "facile":
            move = self.random_move()
        elif difficulty == "moyen":
            move = self.medium_move()
        else:
            move = self.minimax_move()
        if move:
            x, y = move
            self.buttons[x][y].config(text=self.ia_symbol, state="disabled", bg="#ffe5b4")
            if self.check_winner(self.ia_symbol):
                self.score["Ordinateur"] += 1
                self.score_label.config(text=self.score_text())
                self.status.config(text="L'ordinateur a gagné !")
                self.save_ia_match("lose")
                messagebox.showinfo("Défaite", "L'ordinateur a gagné !")
                self.reset_board()
                return
            elif self.is_draw():
                self.score["Égalité"] += 1
                self.score_label.config(text=self.score_text())
                self.status.config(text="Égalité !")
                self.save_ia_match("draw")
                messagebox.showinfo("Égalité", "Match nul !")
                self.reset_board()
                return
        self.my_turn = True
        self.status.config(text="À vous de jouer !")

    def random_move(self):
        empty = [(i, j) for i in range(3) for j in range(3) if not self.buttons[i][j]["text"]]
        return random.choice(empty) if empty else None

    def medium_move(self):
        # 50% chance random, 50% block/win if possible
        empty = [(i, j) for i in range(3) for j in range(3) if not self.buttons[i][j]["text"]]
        if not empty:
            return None
        # 50% random
        if random.random() < 0.5:
            return random.choice(empty)
        # Try to win
        for x, y in empty:
            if self.simulate_move(x, y, self.ia_symbol):
                return (x, y)
        # Try to block
        for x, y in empty:
            if self.simulate_move(x, y, self.symbol):
                return (x, y)
        return random.choice(empty)

    def minimax_move(self):
        board = [[self.buttons[i][j]["text"] for j in range(3)] for i in range(3)]
        best_score = -float("inf")
        best_move = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = self.ia_symbol
                    score = self.minimax(board, 0, False)
                    board[i][j] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        return best_move

    def minimax(self, board, depth, is_max):
        winner = self.get_winner(board)
        if winner == self.ia_symbol:
            return 10 - depth
        elif winner == self.symbol:
            return depth - 10
        elif all(board[i][j] != "" for i in range(3) for j in range(3)):
            return 0
        if is_max:
            best = -float("inf")
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.ia_symbol
                        best = max(best, self.minimax(board, depth + 1, False))
                        board[i][j] = ""
            return best
        else:
            best = float("inf")
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.symbol
                        best = min(best, self.minimax(board, depth + 1, True))
                        board[i][j] = ""
            return best

    def get_winner(self, board):
        wins = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
        ]
        for line in wins:
            vals = [board[x][y] for x, y in line]
            if vals[0] and vals.count(vals[0]) == 3:
                return vals[0]
        return None

    def simulate_move(self, x, y, symbol):
        board = [[self.buttons[i][j]["text"] for j in range(3)] for i in range(3)]
        board[x][y] = symbol
        return self.get_winner(board) == symbol

    def check_winner(self, symbol):
        b = [[self.buttons[i][j]["text"] for j in range(3)] for i in range(3)]
        wins = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
        ]
        for line in wins:
            if all(b[x][y] == symbol for x, y in line):
                return True
        return False

    def is_draw(self):
        return all(self.buttons[i][j]["text"] for i in range(3) for j in range(3))

    def save_ia_match(self, result):
        """
        result: "win", "lose", "draw"
        """
        try:
            data = {
                "username": self.user["username"],
                "result": result,
                "difficulty": self.difficulty.get()
            }
            requests.post(f"{SERVER_URL}/api/ia_match/", json=data, timeout=2)
        except Exception as e:
            messagebox.showwarning("Info", f"Score IA non enregistré (hors ligne)\n{e}")