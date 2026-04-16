import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GAME.board import Board

class DummyPiece:
    def __init__(self, piece_id, position, owner=0):
        self.id = piece_id
        self.position = position
        self.owner = owner

class DummyPlayer:
    def __init__(self):
        self.pieces = {}

class TestBoardRemovePiece(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.player = DummyPlayer()
        # Place a piece at (2, 3)
        self.piece = DummyPiece(42, (2, 3))
        self.board.tiles[3][2].piece = self.piece
        self.player.pieces[self.piece.id] = self.piece

    def test_remove_piece_from_board(self):
        self.board.remove_piece(self.piece)
        self.assertIsNone(self.board.tiles[3][2].piece, "Piece should be removed from the board tile")

    def test_remove_piece_from_player(self):
        self.board.remove_piece(self.piece, self.player)
        self.assertIsNone(self.board.tiles[3][2].piece, "Piece should be removed from the board tile")
        self.assertNotIn(self.piece.id, self.player.pieces, "Piece should be removed from player's pieces dict")

    def test_remove_piece_not_in_player(self):
        # Remove from board, but not in player's pieces
        other_piece = DummyPiece(99, (4, 5))
        self.board.tiles[5][4].piece = other_piece
        self.board.remove_piece(other_piece, self.player)
        self.assertIsNone(self.board.tiles[5][4].piece, "Piece should be removed from the board tile")
        self.assertNotIn(other_piece.id, self.player.pieces, "Piece not in player's pieces dict, should not raise error")

    def test_remove_piece_twice(self):
        self.board.remove_piece(self.piece, self.player)
        # Removing again should not raise error
        self.board.remove_piece(self.piece, self.player)
        self.assertIsNone(self.board.tiles[3][2].piece)
        self.assertNotIn(self.piece.id, self.player.pieces)

if __name__ == "__main__":
    unittest.main()
