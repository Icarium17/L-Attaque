
import unittest
import sys
import os
from collections import Counter
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from USERS.aiPlayer import AIPlayer
from GAME.piece import PieceType

class DummyUser:
    pass

class TestAIPlayerMediumSetupStrategies(unittest.TestCase):
    STRATEGIES = [
        "spread_out_bombs",
        "single_bomb_cluster",
        "spread_out_bomb_clusters",
        "bomb_side",
        "x_bomb",
        "front_line_bombs",
        "front_line_flag",
        "safe_flag",
        "corner_flag",
        "place_flag",
        "scouts_front",
        "spread_out_bomb_clusters_flag",
        "bottle_neck_lakes",
        "strong_center",
        "x_bomb_flag",
        "diagonal_bombs"
    ]

    VALID_MEDIUM_FLOW_BY_ORDER = {
        0: {
            "spread_out_bombs",
            "single_bomb_cluster",
            "spread_out_bomb_clusters",
            "bomb_side",
            "x_bomb",
            "front_line_bombs",
            "front_line_flag",
            "place_flag",
            "scouts_front",
            "spread_out_bomb_clusters_flag",
            "x_bomb_flag",
            "diagonal_bombs"
        },
        1: {
            "spread_out_bombs",
            "single_bomb_cluster",
            "spread_out_bomb_clusters",
            "bomb_side",
            "x_bomb",
            "diagonal_bombs",
            "safe_flag",
            "corner_flag",
            "spread_out_bomb_clusters_flag",
            "x_bomb_flag",
        },
    }

    def _run_medium_flow(self, strategy_name, order):
        random.seed(0)
        ai = AIPlayer(DummyUser(), order=order, difficulty=1)
        strategy = getattr(ai.setup_builder, strategy_name)
        initial_pieces = strategy()
        preplaced_positions = {piece.position: piece.type for piece in initial_pieces}
        final_pieces = ai.setup_builder.generate_pieces(
            ai.setup_builder.generate_rest_of_types(),
            initial_pieces,
        )
        return ai, preplaced_positions, final_pieces

    def _assert_full_inventory(self, pieces):
        self.assertEqual(len(pieces), 40)
        self.assertEqual(len({piece.position for piece in pieces}), 40)

        counts = Counter(piece.type for piece in pieces)
        expected_counts = {piece_type: piece_type.count for piece_type in PieceType}
        self.assertEqual(counts, expected_counts)

    def _all_pieces_in_rows(self, ai, pieces):
        row_start, row_end = ai.rows[ai.order]
        return all(
            0 <= piece.position[0] < 10 and row_start <= piece.position[1] < row_end
            for piece in pieces
        )

    def test_medium_flow_keeps_full_inventory_for_every_strategy(self):
        for order in (0, 1):
            for strategy_name in self.STRATEGIES:
                with self.subTest(order=order, strategy=strategy_name):
                    _, _, final_pieces = self._run_medium_flow(strategy_name, order)
                    self._assert_full_inventory(final_pieces)

    def test_medium_flow_preserves_preplaced_positions_for_every_strategy(self):
        for order in (0, 1):
            for strategy_name in self.STRATEGIES:
                with self.subTest(order=order, strategy=strategy_name):
                    _, preplaced_positions, final_pieces = self._run_medium_flow(strategy_name, order)
                    final_positions = {piece.position: piece.type for piece in final_pieces}

                    for position, piece_type in preplaced_positions.items():
                        self.assertIn(position, final_positions)
                        self.assertEqual(final_positions[position], piece_type)

    def test_medium_flow_identifies_valid_replacement_strategies(self):
        for order in (0, 1):
            for strategy_name in self.STRATEGIES:
                with self.subTest(order=order, strategy=strategy_name):
                    ai, _, final_pieces = self._run_medium_flow(strategy_name, order)
                    in_rows = self._all_pieces_in_rows(ai, final_pieces)
                    expected = strategy_name in self.VALID_MEDIUM_FLOW_BY_ORDER[order]
                    self.assertEqual(in_rows, expected)

    def test_valid_medium_replacements_keep_all_pieces_in_player_rows(self):
        for order, strategy_names in self.VALID_MEDIUM_FLOW_BY_ORDER.items():
            for strategy_name in strategy_names:
                with self.subTest(order=order, strategy=strategy_name):
                    ai, _, final_pieces = self._run_medium_flow(strategy_name, order)
                    self.assertTrue(self._all_pieces_in_rows(ai, final_pieces))

    def test_build_from_motif_composition_keeps_unique_flag_inventory(self):
        for order in (0, 1):
            with self.subTest(order=order):
                random.seed(0)
                ai = AIPlayer(DummyUser(), order=order, difficulty=1)
                pieces = ai.setup_library.build_from_motif([
                    ai.setup_builder.spread_out_bomb_clusters_flag,
                    ai.setup_builder.front_line_flag,
                ])

                self._assert_full_inventory(pieces)
                self.assertEqual(
                    sum(1 for piece in pieces if piece.type == PieceType.Drapeau),
                    PieceType.Drapeau.count,
                )

    def test_build_from_motif_composition_respects_piece_count_limits(self):
        for order in (0, 1):
            with self.subTest(order=order):
                random.seed(0)
                ai = AIPlayer(DummyUser(), order=order, difficulty=1)
                pieces = ai.setup_library.build_from_motif([
                    ai.setup_builder.spread_out_bombs,
                    ai.setup_builder.single_bomb_cluster,
                ])

                self._assert_full_inventory(pieces)
                self.assertEqual(
                    sum(1 for piece in pieces if piece.type == PieceType.Bombe),
                    PieceType.Bombe.count,
                )

if __name__ == '__main__':
    unittest.main()
