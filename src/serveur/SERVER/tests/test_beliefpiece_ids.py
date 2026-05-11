import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GAME.piece import Piece, BeliefPiece, PieceType
from GAME.board import Board
from gameManager import GameManager
from USERS.user import User
from USERS.player import Player

class TestBeliefPieceIDs(unittest.TestCase):
    def setUp(self):
        # Create two users and players
        user1 = User(1, "key1", "Alice", 0, "IDLE")
        user2 = User(2, "key2", "Bob", 0, "IDLE")
        player1 = Player(user1, 0)
        player2 = Player(user2, 1)
        self.players = [player1, player2]
        self.gm = GameManager(None, self.players)

    def test_beliefpiece_ids_match(self):
        # Simulate player 0 setup
        pieces_p0 = [Piece(id=i, type=PieceType.Marechal, position=(i, 0), owner=0) for i in range(3)]
        self.gm.players[0].known_board.set_pieces(pieces_p0)
        self.gm.players[0].sync_owned_pieces()
        # Simulate player 1 setup
        pieces_p1 = [Piece(id=i, type=PieceType.General, position=(i, 9), owner=1) for i in range(3)]
        self.gm.players[1].known_board.set_pieces(pieces_p1)
        self.gm.players[1].sync_owned_pieces()
        # Call set_unknowns_pieces for player 0
        p0_pieces = self.gm.players[0].known_board.get_pieces(0)
        self.gm.set_unknowns_pieces(0, p0_pieces)
        # Check that for each position, the id matches between real and belief pieces
        real_pos_id = {(p.position): p.id for p in p0_pieces.values()}
        belief_pos_id = {bp["position"]: bp["id"] for bp in self.gm.players[1].known_board.return_pieces() if bp["owner"] == 0}
        self.assertEqual(real_pos_id, belief_pos_id)

if __name__ == "__main__":
    unittest.main()
