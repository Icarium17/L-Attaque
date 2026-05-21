import os
import random
import sys
import unittest
from collections import Counter


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from USERS.aiPlayer import AIPlayer
from GAME.piece import PieceType


class DummyUser:
    pass


class TestAIPlayerHardSetup(unittest.TestCase):
    def _build_hard_setup(self, order, seed):
        random.seed(seed)
        ai = AIPlayer(DummyUser(), order=order, difficulty=2)
        pieces = ai.setup_pieces()
        return ai, pieces

    def _assert_valid_hard_setup(self, ai, pieces):
        row_start, row_end = ai.rows[ai.order]

        self.assertEqual(len(pieces), 40)
        self.assertEqual(len({piece.position for piece in pieces}), len(pieces))
        self.assertTrue(
            all(0 <= piece.position[0] < 10 and row_start <= piece.position[1] < row_end for piece in pieces),
            "all hard setup pieces should stay inside the player's setup rows",
        )

        counts = Counter(piece.type for piece in pieces)
        expected_counts = {piece_type: piece_type.count for piece_type in PieceType}
        self.assertEqual(counts, expected_counts)

    def test_hard_setup_keeps_exact_inventory_and_rows_for_multiple_seeds(self):
        for order in (0, 1):
            for seed in range(10):
                with self.subTest(order=order, seed=seed):
                    ai, pieces = self._build_hard_setup(order, seed)
                    self._assert_valid_hard_setup(ai, pieces)

    def test_hard_setup_always_places_single_flag_and_six_bombs(self):
        for order in (0, 1):
            for seed in range(10):
                with self.subTest(order=order, seed=seed):
                    _, pieces = self._build_hard_setup(order, seed)
                    counts = Counter(piece.type for piece in pieces)
                    self.assertEqual(counts[PieceType.Drapeau], 1)
                    self.assertEqual(counts[PieceType.Bombe], 6)


if __name__ == '__main__':
    unittest.main()