import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.size = 3
        self.board = []
        self.players = []
        self.current_player_index = 0
        self.records = []
        self.init_ui()

    def init_ui(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=10)
        self.play_area_frame = tk.Frame(self.root)
        self.play_area_frame.pack()
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=10)

        tk.Label(self.menu_frame, text="Spieler 1:").grid(row=0, column=0)
        self.player1_entry = tk.Entry(self.menu_frame)
        self.player1_entry.grid(row=0, column=1)

        tk.Label(self.menu_frame, text="Spieler 2:").grid(row=1, column=0)
        self.player2_entry = tk.Entry(self.menu_frame)
        self.player2_entry.grid(row=1, column=1)

        tk.Label(self.menu_frame, text="Spielfeldgröße (ungerade Zahl):").grid(row=2, column=0)
        self.size_var = tk.IntVar(value=3)
        tk.Spinbox(self.menu_frame, from_=3, to=15, increment=2, textvariable=self.size_var).grid(row=2, column=1)

        self.start_button = tk.Button(self.menu_frame, text="Neues Spiel starten", command=self.start_game)
        self.start_button.grid(row=3, columnspan=2, pady=10)

        self.records_button = tk.Button(self.controls_frame, text="Rekordliste anzeigen", command=self.show_records)
        self.records_button.pack()

        self.current_player_label = tk.Label(self.controls_frame, text="")
        self.current_player_label.pack()

    def start_game(self):
        self.players = [self.player1_entry.get() or "Spieler 1", self.player2_entry.get() or "Spieler 2"]
        self.size = self.size_var.get()
        self.current_player_index = 0
        self.current_player_label.config(text=f"Am Zug: {self.players[self.current_player_index]}")
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.create_board()

    def create_board(self):
        for widget in self.play_area_frame.winfo_children():
            widget.destroy()
        for r in range(self.size):
            for c in range(self.size):
                btn = tk.Button(self.play_area_frame, text="", width=4, height=2,
                                command=lambda row=r, col=c: self.make_move(row, col))
                btn.grid(row=r, column=c)
                self.board[r][c] = btn

    def make_move(self, row, col):
        if self.board[row][col].cget("text") == "":
            mark = "X" if self.current_player_index == 0 else "O"
            self.board[row][col].config(text=mark)
            if self.check_winner(row, col, mark):
                messagebox.showinfo("Spiel beendet", f"{self.players[self.current_player_index]} hat gewonnen!")
                self.records.append(f"{self.players[self.current_player_index]} hat gewonnen")
                self.start_game()
            elif all(self.board[r][c].cget("text") != "" for r in range(self.size) for c in range(self.size)):
                messagebox.showinfo("Spiel beendet", "Unentschieden!")
                self.records.append("Unentschieden")
                self.start_game()
            else:
                self.current_player_index = 1 - self.current_player_index
                self.current_player_label.config(text=f"Am Zug: {self.players[self.current_player_index]}")

    def check_winner(self, row, col, mark):
        # Check row
        if all(self.board[row][c].cget("text") == mark for c in range(self.size)):
            return True
        # Check column
        if all(self.board[r][col].cget("text") == mark for r in range(self.size)):
            return True
        # Check main diagonal
        if all(self.board[i][i].cget("text") == mark for i in range(self.size)):
            return True
        # Check anti-diagonal
        if all(self.board[i][self.size - 1 - i].cget("text") == mark for i in range(self.size)):
            return True
        return False

    def show_records(self):
        if not self.records:
            messagebox.showinfo("Rekordliste", "Keine Einträge verfügbar.")
        else:
            messagebox.showinfo("Rekordliste", "\n".join(self.records))

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()