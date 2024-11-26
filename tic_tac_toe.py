import tkinter as tk
from tkinter import messagebox
import threading
import time
import csv
import os
import re


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.size = 3
        self.board = []
        self.players = []
        self.current_player_index = 0
        self.records = "records.csv"
        self.timer_thread = None
        self.timer_running = False
        self.elapsed_time = 0

        try:
            if not os.path.exists(self.records):
                with open(self.records, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Player", "Time (seconds)"])
        except IOError as e:
            messagebox.showerror("Fehler", f"Fehler beim Zugriff auf die Datei: {e}")
            return

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

        self.timer_label = tk.Label(self.controls_frame, text="Zeit: 0 Sekunden")
        self.timer_label.pack()

    def start_game(self):
        player1_name = self.player1_entry.get()
        player2_name = self.player2_entry.get()
        
        if not self.is_valid_username(player1_name):
            messagebox.showerror("Ungültiger Benutzername", "Der Benutzername von Spieler 1 ist ungültig. Stellen Sie sicher, dass er mindestens 5 Zeichen lang ist, nicht mehr als 3 Zahlen enthält und keine unerlaubten Sonderzeichen.")
            return
        
        if not self.is_valid_username(player2_name):
            messagebox.showerror("Ungültiger Benutzername", "Der Benutzername von Spieler 2 ist ungültig. Stellen Sie sicher, dass er mindestens 5 Zeichen lang ist, nicht mehr als 3 Zahlen enthält und keine unerlaubten Sonderzeichen.")
            return
        
        self.players = [player1_name or "Spieler 1", player2_name or "Spieler 2"]
        self.size = self.size_var.get()
        self.current_player_index = 0
        self.current_player_label.config(text=f"Am Zug: {self.players[self.current_player_index]}")
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.elapsed_time = 0
        self.start_timer()
        self.create_board()

    def is_valid_username(self, username):
        # Mindestlänge 5 Zeichen
        if len(username) < 5:
            return False
        
        # Maximal 3 Zahlen
        if len(re.findall(r'\d', username)) > 3:
            return False
        
        # Verbote Sonderzeichen (z.B. Windows Dateinamen verbotene Zeichen)
        forbidden_characters = r'[<>:"/\\|?*]'  # Windows verbotene Zeichen
        if re.search(forbidden_characters, username):
            return False
        
        return True

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
                self.stop_timer()
                self.save_board_to_file()
                messagebox.showinfo("Spiel beendet", f"{self.players[self.current_player_index]} hat gewonnen!")
                self.check_and_save_record(self.players[self.current_player_index], self.elapsed_time)
                self.start_game()
            elif all(self.board[r][c].cget("text") != "" for r in range(self.size) for c in range(self.size)):
                self.stop_timer()
                self.save_board_to_file()
                messagebox.showinfo("Spiel beendet", "Unentschieden!")
                self.start_game()
            else:
                self.current_player_index = 1 - self.current_player_index
                self.current_player_label.config(text=f"Am Zug: {self.players[self.current_player_index]}")

    def check_winner(self, row, col, mark):
        if all(self.board[row][c].cget("text") == mark for c in range(self.size)):
            return True
        if all(self.board[r][col].cget("text") == mark for r in range(self.size)):
            return True
        if all(self.board[i][i].cget("text") == mark for i in range(self.size)):
            return True
        if all(self.board[i][self.size - 1 - i].cget("text") == mark for i in range(self.size)):
            return True
        return False

    def show_records(self):
        try:
            if not os.path.exists(self.records) or os.stat(self.records).st_size == 0:
                messagebox.showinfo("Rekordliste", "Keine Einträge verfügbar.")
            else:
                with open(self.records, "r") as f:
                    records = f.readlines()
                    messagebox.showinfo("Rekordliste", "".join(records))
        except IOError as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Rekordliste: {e}")

    def start_timer(self):
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()

    def update_timer(self):
        while self.timer_running:
            time.sleep(1)
            self.elapsed_time += 1
            self.timer_label.config(text=f"Zeit: {self.elapsed_time} Sekunden")

    def stop_timer(self):
        self.timer_running = False

    def save_board_to_file(self):
        try:
            with open("board_state.txt", "w") as f:
                for row in self.board:
                    f.write(" ".join(cell.cget("text") or "." for cell in row) + "\n")
        except IOError as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern des Spielfelds: {e}")

    def check_and_save_record(self, player, time_elapsed):
        if time_elapsed < 1:  # No record for draw
            return
        try:
            with open(self.records, "a") as f:
                writer = csv.writer(f)
                writer.writerow([player, time_elapsed])
        except IOError as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern des Rekords: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TicTacToe(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")
