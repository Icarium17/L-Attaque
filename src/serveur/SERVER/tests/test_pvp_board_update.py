import unittest

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GAME.piece import Piece, PieceType
from GAME.board import Board
from gameManager import GameManager
from USERS.user import User
from USERS.player import Player

class TestPVPBoardUpdate(unittest.TestCase):
    def setUp(self):
        user1 = User(1, "key1", "Alice", 0, "IDLE")
        user2 = User(2, "key2", "Bob", 0, "IDLE")
        player1 = Player(user1, 0)
        player2 = Player(user2, 1)
        self.players = [player1, player2]
        self.gm = GameManager(None, self.players)
        # Place one piece for each player in adjacent positions
        self.p0_piece = Piece(id=10, type=PieceType.Marechal, position=(5, 5), owner=0)
        self.p1_piece = Piece(id=20, type=PieceType.General, position=(5, 6), owner=1)
        self.gm.players[0].known_board.set_pieces([self.p0_piece])
        self.gm.players[0].sync_owned_pieces()
        self.gm.players[1].known_board.set_pieces([self.p1_piece])
        self.gm.players[1].sync_owned_pieces()
        # Set up boards for both players
        self.gm.board.set_pieces([self.p0_piece, self.p1_piece])

    def test_attacker_wins_and_boards_update(self):
        # Simulate a move where p0 attacks p1 and wins
        class DummyMove:
            def get_params(self):
                return (5, 5, 5, 6)
            moveFrom = (5, 5)
            moveTo = (5, 6)
        move = DummyMove()
        # Patch game rules so p0 always wins
        self.gm.game_rules.combat = lambda a, d: a
        self.gm.make_move(self.players[0].key, move)
        # Check main board
        tile = self.gm.board.tiles[6][5]
        self.assertIsNotNone(tile.piece)
        self.assertEqual(tile.piece.owner, 0)
        # Check p0's known board
        tile_p0 = self.gm.players[0].known_board.tiles[6][5]
        self.assertIsNotNone(tile_p0.piece)
        self.assertEqual(tile_p0.piece.owner, 0)
        # Check p1's known board (should not have p0's piece at (5,5))
        tile_p1_old = self.gm.players[1].known_board.tiles[5][5]
        self.assertIsNone(tile_p1_old.piece)
        tile_p1_new = self.gm.players[1].known_board.tiles[6][5]
        # If your logic puts a belief piece, check its id and owner
        if tile_p1_new.piece is not None:
            self.assertEqual(tile_p1_new.piece.owner, 0)
            self.assertEqual(tile_p1_new.piece.position, (5, 6))

    def test_attacker_wins_multiple_positions(self):
        # Place multiple pieces for both players
        p0_piece1 = Piece(id=11, type=PieceType.Marechal, position=(2, 2), owner=0)
        p1_piece1 = Piece(id=21, type=PieceType.General, position=(2, 3), owner=1)
        self.gm.players[0].known_board.set_pieces([self.p0_piece, p0_piece1])
        self.gm.players[0].sync_owned_pieces()
        self.gm.players[1].known_board.set_pieces([self.p1_piece, p1_piece1])
        self.gm.players[1].sync_owned_pieces()
        self.gm.board.set_pieces([self.p0_piece, self.p1_piece, p0_piece1, p1_piece1])
        # Simulate a move where p0_piece1 attacks p1_piece1 and wins
        class DummyMove2:
            def get_params(self):
                return (2, 2, 2, 3)
            moveFrom = (2, 2)
            moveTo = (2, 3)
        move2 = DummyMove2()
        self.gm.game_rules.combat = lambda a, d: a
        self.gm.make_move(self.players[0].key, move2)
        # Check p1's known board: p0_piece1 should be at (2,3), not at (2,2)
        tile_p1_old = self.gm.players[1].known_board.tiles[2][2]
        self.assertIsNone(tile_p1_old.piece)
        tile_p1_new = self.gm.players[1].known_board.tiles[3][2]
        if tile_p1_new.piece is not None:
            self.assertEqual(tile_p1_new.piece.owner, 0)
            self.assertEqual(tile_p1_new.piece.position, (2, 3))

    def test_attacker_loses_and_boards_update(self):
        # Simulate a move where p0 attacks p1 and loses
        class DummyMove:
            def get_params(self):
                return (5, 5, 5, 6)
            moveFrom = (5, 5)
            moveTo = (5, 6)
        move = DummyMove()
        # Patch game rules so p1 always wins
        self.gm.game_rules.combat = lambda a, d: d
        self.gm.make_move(self.players[0].key, move)
        # Check p0's known board: p0's piece should be removed from (5,5)
        tile_p0_old = self.gm.players[0].known_board.tiles[5][5]
        self.assertIsNone(tile_p0_old.piece)
        # Check p1's known board: p1's piece should remain at (5,6)
        tile_p1 = self.gm.players[1].known_board.tiles[6][5]
        self.assertIsNotNone(tile_p1.piece)
        self.assertEqual(tile_p1.piece.owner, 1)
        self.assertEqual(tile_p1.piece.position, (5, 6))

if __name__ == "__main__":
    unittest.main()
