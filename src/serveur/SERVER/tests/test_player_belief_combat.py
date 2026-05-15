import os
import sys
import unittest
from pprint import pformat

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GAME.board import Board
from GAME.move import Move
from GAME.piece import BeliefPiece, Piece, PieceType
from USERS.player import Player


class DummyUser:
    pass


class TestPlayerBeliefCombatUpdates(unittest.TestCase):
    def setUp(self):
        self.player = Player(DummyUser(), order=0)
        self.player.known_board = Board()

    def _serialize_piece(self, piece):
        data = {
            "id": piece.id,
            "position": piece.position,
            "owner": piece.owner,
        }

        if isinstance(piece, BeliefPiece):
            data["kind"] = "belief"
            data["probabilities"] = {
                piece_type.name: round(probability, 4)
                for piece_type, probability in piece.probabilities.items()
            }
        else:
            data["kind"] = "revealed"
            data["type"] = piece.type.name if piece.type else None

        return data

    def _print_belief_state(self, label):
        hidden_pieces = {
            piece_id: self._serialize_piece(piece)
            for piece_id, piece in self.player.belief_pieces.items()
        }
        revealed_pieces = {
            piece_id: self._serialize_piece(piece)
            for piece_id, piece in self.player.opponent_pieces.items()
        }
        remaining_counts = {
            piece_type.name: count
            for piece_type, count in self.player.opponent_belief_pieces_left.items()
        }

        print(f"\n--- {label} ---")
        print(f"hidden belief pieces: {pformat(hidden_pieces)}")
        print(f"revealed opponent pieces: {pformat(revealed_pieces)}")
        print(f"remaining belief counts: {pformat(remaining_counts)}")

    def test_loser_hidden_belief_piece_removes_it_and_decrements_count(self):
        hidden_piece = BeliefPiece(10, (3, 3), owner=1)
        other_hidden_piece = BeliefPiece(11, (4, 3), owner=1)
        self.player.add_belief_pieces([hidden_piece, other_hidden_piece])

        initial_count = self.player.opponent_belief_pieces_left[PieceType.Major]
        loser = Piece(10, PieceType.Major, (3, 3), owner=1)

        self.player.update_belief_state_loser(loser)
        self._print_belief_state("after hidden loser")

        self.assertNotIn(10, self.player.belief_pieces)
        self.assertIn(11, self.player.belief_pieces)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Major],
            initial_count - 1,
        )
        self.assertEqual(self.player.opponent_pieces, {})

    def test_loser_revealed_piece_removes_it_from_revealed_dict(self):
        revealed_piece = Piece(12, PieceType.Capitaine, (5, 5), owner=1)
        self.player.add_revealed_opponent_piece(revealed_piece)

        initial_count = self.player.opponent_belief_pieces_left[PieceType.Capitaine]
        loser = Piece(12, PieceType.Capitaine, (5, 5), owner=1)

        self.player.update_belief_state_loser(loser)
        self._print_belief_state("after revealed loser")

        self.assertNotIn(12, self.player.opponent_pieces)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Capitaine],
            initial_count - 1,
        )

    def test_winner_hidden_belief_piece_becomes_revealed_piece(self):
        hidden_piece = BeliefPiece(13, (6, 6), owner=1)
        other_hidden_piece = BeliefPiece(14, (7, 6), owner=1)
        self.player.add_belief_pieces([hidden_piece, other_hidden_piece])

        initial_count = self.player.opponent_belief_pieces_left[PieceType.Colonel]
        winner = Piece(13, PieceType.Colonel, (6, 6), owner=1)

        self.player.update_belief_state_winner(winner)
        self._print_belief_state("after hidden winner")

        self.assertNotIn(13, self.player.belief_pieces)
        self.assertIn(13, self.player.opponent_pieces)
        revealed_piece = self.player.opponent_pieces[13]
        self.assertIsInstance(revealed_piece, Piece)
        self.assertNotIsInstance(revealed_piece, BeliefPiece)
        self.assertEqual(revealed_piece.type, PieceType.Colonel)
        self.assertEqual(revealed_piece.owner, 1)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Colonel],
            initial_count - 1,
        )

    def test_winner_already_revealed_piece_updates_without_decrementing_count(self):
        old_revealed_piece = Piece(15, PieceType.Lieutenant, (1, 1), owner=1)
        self.player.add_revealed_opponent_piece(old_revealed_piece)

        initial_count = self.player.opponent_belief_pieces_left[PieceType.Lieutenant]
        winner = Piece(15, PieceType.Lieutenant, (1, 2), owner=1)

        self.player.update_belief_state_winner(winner)
        self._print_belief_state("after revealed winner")

        self.assertIn(15, self.player.opponent_pieces)
        updated_piece = self.player.opponent_pieces[15]
        self.assertEqual(updated_piece.position, (1, 2))
        self.assertEqual(updated_piece.owner, 1)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Lieutenant],
            initial_count,
        )

    def test_hidden_winner_after_post_combat_move_does_not_duplicate_old_square(self):
        hidden_piece = BeliefPiece(16, (1, 3), owner=1)
        self.player.position_pieces([hidden_piece])
        self.player.add_belief_pieces([hidden_piece])

        winner = Piece(16, PieceType.Sergent, (1, 4), owner=1)

        self.player.known_board.move_post_combat(winner.clone(), 4, 1)
        self.player.update_belief_state_winner(winner)

        self.assertIsNone(self.player.known_board.tiles[3][1].piece)

        destination_piece = self.player.known_board.tiles[4][1].piece
        self.assertIsNotNone(destination_piece)
        self.assertEqual(destination_piece.id, 16)
        self.assertEqual(destination_piece.owner, 1)
        self.assertEqual(destination_piece.type, PieceType.Sergent)

        matching_positions = []
        for y in range(self.player.known_board.rows):
            for x in range(self.player.known_board.cols):
                piece = self.player.known_board.tiles[y][x].piece
                if piece is not None and piece.id == 16 and piece.owner == 1:
                    matching_positions.append((x, y))

        self.assertEqual(matching_positions, [(1, 4)])

    def test_hidden_piece_move_then_other_loss_keeps_belief_state_consistent(self):
        moving_piece = BeliefPiece(20, (1, 1), owner=1)
        other_hidden_piece = BeliefPiece(21, (2, 1), owner=1)
        self.player.position_pieces([moving_piece, other_hidden_piece])
        self.player.add_belief_pieces([moving_piece, other_hidden_piece])

        move = Move((1, 1), (1, 2))
        initial_major_count = self.player.opponent_belief_pieces_left[PieceType.Major]

        self.player.update_belief_state_move(1, 1, 1)
        self.player.move(move)
        self.player.update_belief_state_loser(Piece(21, PieceType.Major, (2, 1), owner=1))
        self._print_belief_state("after one-tile move then other hidden loser")

        self.assertIsNone(self.player.known_board.tiles[1][1].piece)
        self.assertIs(self.player.known_board.tiles[2][1].piece, moving_piece)
        self.assertEqual(moving_piece.position, (1, 2))
        self.assertIn(20, self.player.belief_pieces)
        self.assertNotIn(21, self.player.belief_pieces)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Major],
            initial_major_count - 1,
        )
        self.assertAlmostEqual(sum(moving_piece.probabilities.values()), 1.0)
        self.assertEqual(moving_piece.probabilities[PieceType.Bombe], 0.0)
        self.assertEqual(moving_piece.probabilities[PieceType.Drapeau], 0.0)
        self.assertGreater(moving_piece.probabilities[PieceType.Eclaireur], 0.0)

    def test_hidden_piece_long_move_then_other_win_keeps_only_scout_possible(self):
        moving_piece = BeliefPiece(30, (0, 0), owner=1)
        other_hidden_piece = BeliefPiece(31, (1, 0), owner=1)
        self.player.position_pieces([moving_piece, other_hidden_piece])
        self.player.add_belief_pieces([moving_piece, other_hidden_piece])

        move = Move((0, 0), (0, 3))
        initial_colonel_count = self.player.opponent_belief_pieces_left[PieceType.Colonel]

        self.player.update_belief_state_move(0, 0, 3)
        self.player.move(move)
        self.player.update_belief_state_winner(Piece(31, PieceType.Colonel, (1, 0), owner=1))
        self._print_belief_state("after long move then other hidden winner")

        self.assertIsNone(self.player.known_board.tiles[0][0].piece)
        upgraded_piece = self.player.known_board.tiles[3][0].piece
        self.assertIsInstance(upgraded_piece, Piece)
        self.assertNotIsInstance(upgraded_piece, BeliefPiece)
        self.assertEqual(upgraded_piece.position, (0, 3))
        self.assertEqual(upgraded_piece.type, PieceType.Eclaireur)
        self.assertNotIn(30, self.player.belief_pieces)
        self.assertIn(30, self.player.opponent_pieces)
        self.assertNotIn(31, self.player.belief_pieces)
        self.assertIn(31, self.player.opponent_pieces)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Colonel],
            initial_colonel_count - 1,
        )
        self.assertEqual(self.player.opponent_belief_pieces_left[PieceType.Eclaireur], 7)

    def test_hidden_piece_long_move_upgrades_to_revealed_scout(self):
        moving_piece = BeliefPiece(40, (2, 2), owner=1)
        self.player.position_pieces([moving_piece])
        self.player.add_belief_pieces([moving_piece])

        initial_scout_count = self.player.opponent_belief_pieces_left[PieceType.Eclaireur]

        self.player.update_belief_state_move(2, 2, 3)
        self._print_belief_state("after long move upgrade")

        self.assertNotIn(40, self.player.belief_pieces)
        self.assertIn(40, self.player.opponent_pieces)
        upgraded_piece = self.player.opponent_pieces[40]
        self.assertIsInstance(upgraded_piece, Piece)
        self.assertNotIsInstance(upgraded_piece, BeliefPiece)
        self.assertEqual(upgraded_piece.type, PieceType.Eclaireur)
        self.assertEqual(self.player.known_board.tiles[2][2].piece, upgraded_piece)
        self.assertEqual(
            self.player.opponent_belief_pieces_left[PieceType.Eclaireur],
            initial_scout_count - 1,
        )

    def test_refresh_hidden_probabilities_upgrades_piece_when_only_one_type_left(self):
        hidden_piece = BeliefPiece(50, (4, 4), owner=1)
        self.player.position_pieces([hidden_piece])
        self.player.add_belief_pieces([hidden_piece])

        for piece_type in PieceType:
            self.player.opponent_belief_pieces_left[piece_type] = 0
        self.player.opponent_belief_pieces_left[PieceType.Major] = 1

        self.player.refresh_hidden_belief_probabilities()
        self._print_belief_state("after refresh upgrade")

        self.assertNotIn(50, self.player.belief_pieces)
        self.assertIn(50, self.player.opponent_pieces)
        upgraded_piece = self.player.opponent_pieces[50]
        self.assertEqual(upgraded_piece.type, PieceType.Major)
        self.assertEqual(self.player.known_board.tiles[4][4].piece, upgraded_piece)
        self.assertEqual(self.player.opponent_belief_pieces_left[PieceType.Major], 0)


if __name__ == '__main__':
    unittest.main()
