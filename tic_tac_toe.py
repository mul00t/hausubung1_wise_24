import tkinter as tk
from tkinter import messagebox
import threading
import time
import csv
import os
import re
import logging
from datetime import datetime

# Logging-Konfiguration
logging.basicConfig(filename="game_log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Benutzerdefinierte Exception für ungültige Benutzernamen
class InvalidUsernameError(Exception):
    """Exception, die ausgelöst wird, wenn der Benutzername ungültig ist."""
    pass


class TicTacToe:
    """
    Hauptklasse für das Tic-Tac-Toe-Spiel.

    Diese Klasse enthält die Spiellogik, das Benutzerinterface und die Funktionen
    zum Verwalten von Spielerinteraktionen, Spielständen und Rekorden.
    """
    def __init__(self, root):
        """
        Initialisiert die Spielumgebung.

        :param root: Das Tkinter-Hauptfenster
        """
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

        # Überprüfen, ob die Rekorddatei existiert, andernfalls wird sie erstellt
        try:
            if not os.path.exists(self.records):
                with open(self.records, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Player", "Time (seconds)"])
        except IOError as e:
            self.log_error(f"Fehler beim Zugriff auf die Datei: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Zugriff auf die Datei: {e}")
            return

        self.init_ui()

    def init_ui(self):
        """
        Initialisiert die Benutzeroberfläche mit Tkinter Widgets.
        """
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
        """
        Startet ein neues Spiel, basierend auf den Benutzereingaben für Spieler und Spielfeldgröße.
        Überprüft die Benutzernamen auf Gültigkeit.
        """
        player1_name = self.player1_entry.get()
        player2_name = self.player2_entry.get()

        # Überprüfen, ob die Benutzernamen gültig sind
        try:
            if not self.is_valid_username(player1_name):
                raise InvalidUsernameError(f"Der Benutzername von Spieler 1 '{player1_name}' ist ungültig.")
            if not self.is_valid_username(player2_name):
                raise InvalidUsernameError(f"Der Benutzername von Spieler 2 '{player2_name}' ist ungültig.")
        except InvalidUsernameError as e:
            self.log_error(str(e))
            messagebox.showerror("Ungültiger Benutzername", str(e))
            return
        
        # Setzen der Spieler und Spielfeldgröße
        self.players = [player1_name or "Spieler 1", player2_name or "Spieler 2"]
        self.size = self.size_var.get()
        self.current_player_index = 0
        self.current_player_label.config(text=f"Am Zug: {self.players[self.current_player_index]}")
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.elapsed_time = 0
        self.start_timer()
        self.create_board()

    def is_valid_username(self, username):
        """
        Überprüft, ob der Benutzername den festgelegten Kriterien entspricht.

        :param username: Der Benutzername, der überprüft werden soll
        :return: True, wenn der Benutzername gültig ist, andernfalls False
        """
        if len(username) < 5:
            return False
        if len(re.findall(r'\d', username)) > 3:
            return False
        forbidden_characters = r'[<>:"/\\|?*]'
        if re.search(forbidden_characters, username):
            return False
        return True

    def create_board(self):
        """
        Erzeugt das Spielfeld mit Buttons in der Benutzeroberfläche basierend auf der Spielfeldgröße.
        """
        for widget in self.play_area_frame.winfo_children():
            widget.destroy()
        for r in range(self.size):
            for c in range(self.size):
                btn = tk.Button(self.play_area_frame, text="", width=4, height=2,
                                command=lambda row=r, col=c: self.make_move(row, col))
                btn.grid(row=r, column=c)
                self.board[r][c] = btn

    def make_move(self, row, col):
        """
        Führt einen Zug aus und überprüft, ob der Zug das Spiel beendet hat.

        :param row: Die Zeile des Zugs
        :param col: Die Spalte des Zugs
        """
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
        """
        Überprüft, ob der Spieler gewonnen hat.

        :param row: Die Zeile des letzten Zuges
        :param col: Die Spalte des letzten Zuges
        :param mark: Das Symbol des Spielers ("X" oder "O")
        :return: True, wenn der Spieler gewonnen hat, andernfalls False
        """
        # Überprüfen der Reihen, Spalten und Diagonalen
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
        """
        Zeigt die Rekordliste an.
        """
        try:
            if not os.path.exists(self.records) or os.stat(self.records).st_size == 0:
                messagebox.showinfo("Rekordliste", "Keine Einträge verfügbar.")
            else:
                with open(self.records, "r") as f:
                    records = f.readlines()
                    messagebox.showinfo("Rekordliste", "".join(records))
        except IOError as e:
            self.log_error(f"Fehler beim Laden der Rekordliste: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Rekordliste: {e}")

    def start_timer(self):
        """
        Startet den Timer, der die vergangene Zeit während des Spiels verfolgt.
        """
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()

    def update_timer(self):
        """
        Aktualisiert den Timer jede Sekunde.
        """
        while self.timer_running:
            time.sleep(1)
            self.elapsed_time += 1
            self.timer_label.config(text=f"Zeit: {self.elapsed_time} Sekunden")

    def stop_timer(self):
        """
        Stoppt den Timer.
        """
        self.timer_running = False

    def save_board_to_file(self):
        """
        Speichert das aktuelle Spielfeld in einer .txt-Datei.
        """
        try:
            with open("board_state.txt", "w") as f:
                for row in self.board:
                    f.write(" ".join(cell.cget("text") if cell.cget("text") != "" else "_" for cell in row) + "\n")
        except IOError as e:
            self.log_error(f"Fehler beim Speichern des Spielfelds: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern des Spielfelds: {e}")

    def check_and_save_record(self, player, time_elapsed):
        """
        Speichert den Rekord in einer CSV-Datei, wenn das Spiel beendet wurde.

        :param player: Der Name des Spielers, der gewonnen hat
        :param time_elapsed: Die Zeit, die der Spieler zum Gewinnen benötigt hat
        """
        try:
            if time_elapsed > 0:  # Keine Rekorde für Unentschieden
                with open(self.records, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([player, time_elapsed])
        except IOError as e:
            self.log_error(f"Fehler beim Speichern des Rekords: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern des Rekords: {e}")

    def log_error(self, error_message):
        """
        Protokolliert Fehler in einer Log-Datei.

        :param error_message: Die Fehlermeldung, die protokolliert werden soll
        """
        logging.error(error_message)


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
