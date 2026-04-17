import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GAME.gameRules import GameRules
from GAME.piece import PieceType
from GAME.board import Board

class DummyPiece:
    def __init__(self, piece_type, owner=0):
        self.type = piece_type
        self.owner = owner
        self.position = (0, 0)

class TestCombat(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.rules = GameRules(self.board, "original")

    def test_equal_power(self):
        p1 = DummyPiece(PieceType.Lieutenant)
        p2 = DummyPiece(PieceType.Lieutenant)
        self.assertIsNone(self.rules.combat(p1, p2))

    def test_espion_vs_marechal(self):
        espion = DummyPiece(PieceType.Espion)
        marechal = DummyPiece(PieceType.Marechal)
        self.assertIs(self.rules.combat(espion, marechal), espion)
        self.assertIs(self.rules.combat(marechal, espion), marechal)

    def test_bomb_vs_demineur(self):
        bomb = DummyPiece(PieceType.Bombe)
        demineur = DummyPiece(PieceType.Demineur)
        self.assertIs(self.rules.combat(demineur, bomb), demineur)

    def test_bomb_vs_other(self):
        bomb = DummyPiece(PieceType.Bombe)
        major = DummyPiece(PieceType.Major)
        self.assertIs(self.rules.combat(major, bomb), bomb)

    def test_bomb_vs_other_board_state(self):
        # Place bomb and major on the board
        bomb = DummyPiece(PieceType.Bombe)
        major = DummyPiece(PieceType.Major)
        bomb.position = (2, 2)
        major.position = (2, 1)
        self.board.set_pieces([bomb, major])
        # Simulate major attacking bomb
        winner = self.rules.combat(major, bomb)
        # Remove loser and update board as in gameManager
        if winner is bomb:
            self.board.remove_piece(major)
        # Bomb should remain, major should be gone
        self.assertIs(self.board.tiles[2][2].piece, bomb)
        self.assertIsNone(self.board.tiles[1][2].piece)

    def test_flag_vs_any(self):
        flag = DummyPiece(PieceType.Drapeau)
        major = DummyPiece(PieceType.Major)
        self.assertIs(self.rules.combat(major, flag), major)
        self.assertIs(self.rules.combat(flag, major), major)

    def test_none_power(self):
        # Simulate a piece with no power
        class NoPower:
            def __init__(self):
                self.type = PieceType.Drapeau
                self.owner = 0
                self.position = (0, 0)
        flag = NoPower()
        major = DummyPiece(PieceType.Major)
        self.assertIs(self.rules.combat(flag, major), major)
        self.assertIs(self.rules.combat(major, flag), major)

    def test_higher_power(self):
        major = DummyPiece(PieceType.Major)
        lieutenant = DummyPiece(PieceType.Lieutenant)
        self.assertIs(self.rules.combat(major, lieutenant), major)
        self.assertIs(self.rules.combat(lieutenant, major), major)

if __name__ == "__main__":
    unittest.main()
