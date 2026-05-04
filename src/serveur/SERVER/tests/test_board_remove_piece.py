import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GAME.board import Board
from GAME.gameRules import GameRules
from GAME.piece import Piece, PieceType
from USERS.player import Player
from USERS.user import User

class DummyPiece:
    def __init__(self, piece_id, position, owner=0):
        self.id = piece_id
        self.position = position
        self.owner = owner

class DummyPlayer:
    def __init__(self):
        self.pieces = {}


def make_player(account_id, order, username):
    return Player(User(account_id, f"KEY{account_id}", username, 0), order)

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

    def test_remove_owned_piece_updates_player_flag_cache(self):
        player = make_player(1, 0, "Blue")
        flag = Piece(100, PieceType.Drapeau, (2, 3), 0)
        self.board.tiles[3][2].piece = flag
        player.pieces[flag.id] = flag
        player.rebuild_piece_counts()

        player.remove_piece(flag)

        self.assertNotIn(flag.id, player.pieces)
        self.assertEqual(player.pieces_left[PieceType.Drapeau], 0)
        self.assertIsNone(player.flag_position)

    def test_check_player_end_state_detects_removed_flag_after_player_removal(self):
        rules = GameRules("original")
        player = make_player(1, 0, "Blue")
        opponent = make_player(2, 1, "Red")
        flag = Piece(101, PieceType.Drapeau, (2, 3), 0)
        self.board.tiles[3][2].piece = flag
        player.pieces[flag.id] = flag
        player.rebuild_piece_counts()

        player.remove_piece(flag)
        self.board.remove_piece(flag)

        ended, result = rules.check_player_end_state(player, [player, opponent], self.board)

        self.assertTrue(ended)
        self.assertIs(result[0], opponent)
        self.assertIs(result[1], player)
        self.assertEqual(result[2], "Blue's flag was captured")

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

    def test_remove_both_pieces_after_tie(self):
        # Simulate a tie: two pieces at adjacent positions
        piece1 = DummyPiece(1, (1, 1), owner=0)
        piece2 = DummyPiece(2, (1, 2), owner=1)
        self.board.tiles[1][1].piece = piece1
        self.board.tiles[2][1].piece = piece2
        self.player.pieces[piece1.id] = piece1
        other_player = DummyPlayer()
        other_player.pieces[piece2.id] = piece2
        # Remove both after tie
        self.board.remove_piece(piece1, self.player)
        self.board.remove_piece(piece2, other_player)
        self.assertIsNone(self.board.tiles[1][1].piece)
        self.assertIsNone(self.board.tiles[2][1].piece)
        self.assertNotIn(piece1.id, self.player.pieces)
        self.assertNotIn(piece2.id, other_player.pieces)

    def test_remove_piece_reflected_in_return_pieces(self):
        # Place and remove a piece, check return_pieces
        self.board.remove_piece(self.piece, self.player)
        all_pieces = self.board.return_pieces()
        # Should not include removed piece
        self.assertTrue(all(p['id'] != self.piece.id for p in all_pieces))

    def test_remove_piece_on_multiple_boards(self):
        # Simulate 3 boards: main, belief, opponent
        main_board = Board()
        belief_board = Board()
        opponent_board = Board()
        piece = DummyPiece(99, (4, 4), owner=0)
        for b in [main_board, belief_board, opponent_board]:
            b.tiles[4][4].piece = piece
        # Remove from all
        for b in [main_board, belief_board, opponent_board]:
            b.remove_piece(piece)
            self.assertIsNone(b.tiles[4][4].piece)

    def test_remove_piece_does_not_remove_same_id_other_owner(self):
        allied_piece = DummyPiece(7, (1, 1), owner=0)
        enemy_piece = DummyPiece(7, (2, 2), owner=1)
        self.board.tiles[1][1].piece = allied_piece
        self.board.tiles[2][2].piece = enemy_piece

        self.board.remove_piece(allied_piece)

        self.assertIsNone(self.board.tiles[1][1].piece)
        self.assertIs(self.board.tiles[2][2].piece, enemy_piece)

    def test_move_post_combat_clears_source_tile(self):
        winner = DummyPiece(55, (3, 3), owner=0)
        self.board.tiles[3][3].piece = winner

        self.board.move_post_combat(winner, 4, 3, (3, 3))

        self.assertIsNone(self.board.tiles[3][3].piece)
        self.assertIs(self.board.tiles[4][3].piece, winner)
        self.assertEqual(winner.position, (3, 4))

    def test_remove_both_pieces_after_tie_and_return_pieces(self):
        # Tie: both pieces should be gone from return_pieces
        piece1 = DummyPiece(10, (2, 2), owner=0)
        piece2 = DummyPiece(11, (2, 3), owner=1)
        self.board.tiles[2][2].piece = piece1
        self.board.tiles[3][2].piece = piece2
        self.player.pieces[piece1.id] = piece1
        other_player = DummyPlayer()
        other_player.pieces[piece2.id] = piece2
        self.board.remove_piece(piece1, self.player)
        self.board.remove_piece(piece2, other_player)
        all_pieces = self.board.return_pieces()
        self.assertTrue(all(p['id'] not in (piece1.id, piece2.id) for p in all_pieces))

if __name__ == "__main__":
    unittest.main()
