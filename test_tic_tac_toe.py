import unittest
from unittest.mock import MagicMock
from tic_tac_toe import TicTacToe  # Stelle sicher, dass der Pfad korrekt ist

class TestTicTacToe(unittest.TestCase):

    def test_valid_username(self):
        # Mock das Tkinter-Root-Objekt und die IntVar-Instanz
        mock_root = MagicMock()
        mock_intvar = MagicMock()
        mock_root.title = MagicMock()  # Mock für die title-Methode
        TicTacToe.root = mock_root
        TicTacToe.size_var = mock_intvar
        
        game = TicTacToe(mock_root)  # Mock-Root wird übergeben
        valid_username = "ValidUser1"
        invalid_username1 = "Usr"
        invalid_username2 = "User!@#"
        
        self.assertTrue(game.is_valid_username(valid_username))
        self.assertFalse(game.is_valid_username(invalid_username1))
        self.assertFalse(game.is_valid_username(invalid_username2))

    def test_invalid_move(self):
        # Mock das Tkinter-Root-Objekt
        mock_root = MagicMock()
        game = TicTacToe(mock_root)  # Mock-Root wird übergeben
        game.start_game()
        
        # Simuliere, dass der Zug an einer bestimmten Position gemacht wird
        game.board[0][0] = MagicMock()  # Mock der Schaltfläche
        game.board[0][0].config = MagicMock()  # Mock für die config-Methode
        game.board[0][0].cget = MagicMock(return_value="X")  # Mock für cget
        
        game.make_move(0, 0)  # Ungültiger Zug (bereits belegt)
        self.assertEqual(game.board[0][0].cget("text"), "X")  # Muss weiterhin "X" sein

if __name__ == "__main__":
    unittest.main()
