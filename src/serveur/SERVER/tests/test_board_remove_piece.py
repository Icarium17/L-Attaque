import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GAME.board import Board
from GAME.gameRules import GameRules
from GAME.piece import Piece, PieceType
from USERS.player import Player
from USERS.user import User

from gameManager import GameManager
from GAME.move import Move
from unittest.mock import MagicMock

class DummyPiece:
    def __init__(self, piece_id, position, owner=0):
        self.id = piece_id
        self.position = position
        self.owner = owner

class DummyPlayer:
    def __init__(self):
        self.pieces = {}

    def remove_piece(self, piece):
        self.pieces.pop(piece.id, None)


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

    def test_attacker_win_piece_only_on_new_pos_on_loser_board(self):
        """
        After attacker wins a combat, ensure the attacker's piece is only present at the new position on the loser's board.
        """
        # Setup two boards: attacker's and loser's
        attacker_board = Board()
        loser_board = Board()
        # Place attacker at (1, 1), defender at (1, 2)
        attacker = Piece(100, PieceType.Marechal, (1, 1), 0)
        defender = Piece(200, PieceType.Lieutenant, (1, 2), 1)
        attacker_board.set_pieces([attacker, defender])
        loser_board.set_pieces([attacker, defender])

        # Simulate combat: attacker wins
        rules = GameRules("original")
        winner = rules.combat(attacker, defender)
        self.assertIs(winner, attacker)

        # Remove defender from loser's board, move attacker to defender's position
        loser_board.remove_piece(defender)
        loser_board.move_post_combat(attacker, 2, 1, (1, 1))

        # Check attacker's piece is only at (1,2) (i.e., [2][1]) on loser's board
        for y in range(loser_board.rows):
            for x in range(loser_board.cols):
                piece = loser_board.tiles[y][x].piece
                if (x, y) == (1, 2):
                    self.assertIs(piece, attacker, "Attacker should be at new position on loser's board")
                else:
                    if piece is not None:
                        self.assertFalse(piece is attacker, f"Attacker should not be at {(x, y)} on loser's board")


    def test_make_move_attacker_win_updates_loser_board(self):
            """
            Use GameManager and make_move to check that after attacker wins, the loser's board only has the attacker's piece at the new position.
            """

            # Setup dummy lobbyManager
            class DummyLobbyManager:
                def too_long_wait(self, key): pass
                def end_game(self, winner, loser, reason): pass

            # Create two players
            player0 = make_player(1, 0, "Blue")
            player1 = make_player(2, 1, "Red")
            player0.known_board = Board()
            player1.known_board = Board()
            player0.time_remaining = 1000
            player1.time_remaining = 1000

            # Create GameManager
            gm = GameManager(DummyLobbyManager(), [player0, player1], status="PLAYING")
            gm.timers = MagicMock()  # Disable timers

            # Place attacker and defender
            from GAME.piece import Piece, PieceType
            attacker = Piece(100, PieceType.Marechal, (1, 1), 0)
            defender = Piece(200, PieceType.Lieutenant, (1, 2), 1)
            gm.board.set_pieces([attacker, defender])
            player0.known_board.set_pieces([attacker.clone(), defender.clone()])
            player1.known_board.set_pieces([attacker.clone(), defender.clone()])
            player0.pieces[attacker.id] = attacker
            player1.pieces[defender.id] = defender

            # Both players are ready
            gm.status = "PLAYING"
            gm.player_to_move = 0

            # Make the move: attacker moves from (1,1) to (1,2)
            move = Move((1, 1), (1, 2))
            result = gm.make_move(player0.key, move)

            # After combat, check loser's board (player1)
            # The attacker's piece should only be at (1,2) on player1's known_board
            found = 0
            for y in range(player1.known_board.rows):
                for x in range(player1.known_board.cols):
                    piece = player1.known_board.tiles[y][x].piece
                    if (x, y) == (1, 2):
                        if piece is not None and piece.id == attacker.id:
                            found += 1
                    elif piece is not None and piece.id == attacker.id:
                        self.fail(f"Attacker should not be at {(x, y)} on loser's board")
            self.assertEqual(found, 1, "Attacker should be at new position on loser's board exactly once")
                        

if __name__ == "__main__":
    unittest.main()
