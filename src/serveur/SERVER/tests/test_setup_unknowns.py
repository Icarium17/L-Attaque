import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from GAME.piece import Piece, PieceType
from GAME.board import Board
from USERS.user import User
from USERS.player import Player
from gameManager import GameManager
from GAME.move import Move

class TestGameManagerSetup(unittest.TestCase):
    def setUp(self):
        # Create two users and players
        self.user1 = User(1, "key1", "Alice", 0, "IDLE")
        self.user2 = User(2, "key2", "Bob", 0, "IDLE")
        self.player1 = Player(self.user1, 0)
        self.player2 = Player(self.user2, 1)
        self.lobby = type('LobbyStub', (), {})()  # Dummy lobbyManager
        self.lobby.too_long_wait = lambda x: None
        self.gm = GameManager(self.lobby, [self.player1, self.player2])

    def make_pieces(self, order):
        # Place a valid Stratego setup (1 Marechal, 1 General, 2 Colonels, etc.)
        # We'll just fill the board from top left to bottom right, rows 6-9
        piece_counts = {
            PieceType.Marechal: 1,
            PieceType.General: 1,
            PieceType.Colonel: 2,
            PieceType.Major: 3,
            PieceType.Capitaine: 4,
            PieceType.Lieutenant: 4,
            PieceType.Sergent: 4,
            PieceType.Demineur: 5,
            PieceType.Eclaireur: 8,
            PieceType.Espion: 1,
            PieceType.Bombe: 6,
            PieceType.Drapeau: 1
        }
        pieces = []
        idx = 0
        yx = [(x, y) for y in range(6, 10) for x in range(10)]
        i = 0
        for ptype, count in piece_counts.items():
            for _ in range(count):
                pos = yx[i]
                pieces.append(Piece(idx, ptype, pos, order))
                idx += 1
                i += 1
        return pieces

    def test_both_players_setup_unknowns(self):
        # Player 1 setup
        pieces1 = self.make_pieces(0)
        result1 = self.gm.check_valid_setup(self.user1.key, pieces1)
        self.assertEqual(result1, "SETUP_SUCCESS")
        # Player 2 setup
        pieces2 = self.make_pieces(1)
        result2 = self.gm.check_valid_setup(self.user2.key, pieces2)
        self.assertEqual(result2, "SETUP_SUCCESS")
        # Check both players' known_board has only BeliefPiece for opponent's pieces
        for player, opp in [(self.player1, self.player2), (self.player2, self.player1)]:
            for y in range(10):
                for x in range(10):
                    tile = player.known_board.tiles[y][x]
                    if tile.piece and tile.piece.owner == opp.order:
                        from GAME.piece import BeliefPiece
                        self.assertIsInstance(tile.piece, BeliefPiece)

        # Make a move with player 1: move the first non-flag, non-bomb piece forward
        # Find a movable piece for player 1
        for piece in pieces1:
            if piece.type not in (PieceType.Bombe, PieceType.Drapeau):
                x, y = piece.position
                move = Move((x, y), (x, y-1))
                break
        status, msg = self.gm.make_move(self.user1.key, move)
        self.assertEqual(status, 1)
        # Check main board: piece should have moved
        moved_piece = self.gm.board.tiles[y-1][x].piece
        self.assertIsNotNone(moved_piece)
        self.assertEqual(moved_piece.owner, 0)
        # Check player 1's known_board: piece should have moved
        moved_piece_p1 = self.player1.known_board.tiles[y-1][x].piece
        self.assertIsNotNone(moved_piece_p1)
        self.assertEqual(moved_piece_p1.owner, 0)
        # Check player 2's known_board: should still have BeliefPiece for player 1's piece
        moved_piece_p2 = self.player2.known_board.tiles[y-1][x].piece
        from GAME.piece import BeliefPiece
        self.assertIsInstance(moved_piece_p2, BeliefPiece)

if __name__ == "__main__":
    unittest.main()
