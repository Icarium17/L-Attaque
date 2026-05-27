import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import copy
import time
import unittest
from ALGO.mcts import MCTS
from ALGO.infoSet import InfoSet
from ALGO.node import Node
from GAME.move import Move
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from GAME.piece import BeliefPiece, Piece, PieceType
from gameManager import GameManager
from lobbyManager import LobbyManager

class TestMCTS(unittest.TestCase):
    def setUp(self):
        # Create users and AI players
        user1 = User(0, "aaa", "AI_1", 0)
        ai1 = AIPlayer(user1, 0, 1)
        user2 = User(1, "bbb", "AI_2", 0)
        ai2 = AIPlayer(user2, 1, 1)
        self.players = [ai1, ai2]

        # Create game and rules
        self.lobby = LobbyManager()
        self.game = GameManager(self.lobby, self.players, "original")

        for i in range(0, 2):
            self.game.setup_ai_player(i)

        # MCTS instance
        self.mcts = MCTS(MCTS.build_snapshot(ai1, self.game.game_type, self.players))

    def _reset_hard_rollout_for_custom_board(self):
        ai = self.players[0]
        ai.difficulty = 2
        self.mcts = MCTS(MCTS.build_snapshot(ai, self.game.game_type, self.players))
        self.mcts._reset_rollout_state()

        for row in self.mcts.algo_infoSet.board_state.tiles:
            for tile in row:
                tile.piece = None

    def _place_rollout_piece(self, piece):
        x, y = piece.position
        self.mcts.algo_infoSet.board_state.tiles[y][x].piece = piece

    def test_algo_runs(self):
        try:
            mcts = self.mcts
            start_time = time.perf_counter()
            for _ in range(100):  # or while time remains
                print("algo")
                mcts.algo()
            move = mcts.get_best_move()

            print(move.get_params() if move else "No move found")
            print(time.perf_counter() - start_time)
            self.assertIsNotNone(move, "No move found by MCTS")
        except Exception as e:
            self.fail(f"MCTS algo() raised an exception: {e}")

    def test_reset_rollout_state_determinizes_impossible_beliefs(self):
        self.game.finish_set_up()
        ai = self.players[0]
        self.mcts = MCTS(MCTS.build_snapshot(ai, self.game.game_type, self.players))
        hidden_beliefs = ai.get_hidden_belief_pieces()

        self.assertTrue(hidden_beliefs, "Expected hidden belief pieces after setup")

        for belief_piece in hidden_beliefs:
            for piece_type in list(belief_piece.probabilities.keys()):
                belief_piece.probabilities[piece_type] = 1.0 if piece_type == PieceType.Drapeau else 0.0

        for piece_type in ai.opponent_belief_pieces_left:
            ai.opponent_belief_pieces_left[piece_type] = 0
        ai.opponent_belief_pieces_left[PieceType.Drapeau] = 1

        self.mcts._reset_rollout_state()

        opponent_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1 - ai.order)
        self.assertTrue(opponent_pieces)
        self.assertTrue(all(piece.type is not None for piece in opponent_pieces.values()))

    def test_actualize_belief_pieces_skips_backtracking_on_id_mismatch(self):
        self.game.finish_set_up()
        ai = self.players[0]
        info_set = InfoSet(copy.deepcopy(ai.known_board), ai.order, self.game.game_rules)

        hidden_beliefs = ai.get_hidden_belief_pieces()
        self.assertGreater(len(hidden_beliefs), 1, "Expected multiple hidden belief pieces after setup")
        stale_hidden_beliefs = hidden_beliefs + [BeliefPiece(9999, (-1, -1), 1 - ai.order)]

        info_set.actualize_belief_pieces(
            stale_hidden_beliefs,
            ai.opponent_belief_pieces_left.copy(),
        )

        stats = info_set.actualize_stats
        opponent_pieces = info_set.board_state.get_pieces(1 - ai.order)

        self.assertTrue(stats["used_mismatch_recovery"])
        self.assertTrue(stats["used_random_fallback"])
        self.assertEqual(stats["recursive_calls"], 0)
        self.assertTrue(all(piece.type is not None for piece in opponent_pieces.values()))

    def test_prior_evaluate_medium_move_ignores_stale_move_with_empty_source(self):
        self.game.finish_set_up()
        ai = self.players[0]
        self.mcts = MCTS(MCTS.build_snapshot(ai, self.game.game_type, self.players))
        self.mcts._reset_rollout_state()

        stale_move = Move((0, 4), (0, 5))

        score = self.mcts.prior_evaluate_medium_move(stale_move)

        self.assertLess(score, 0)

    def test_prior_evaluate_difficult_move_ignores_stale_move_with_empty_source(self):
        self.game.finish_set_up()
        ai = self.players[0]
        ai.difficulty = 2
        self.mcts = MCTS(MCTS.build_snapshot(ai, self.game.game_type, self.players))
        self.mcts._reset_rollout_state()

        stale_move = Move((0, 4), (0, 5))

        score = self.mcts.prior_evaluate_difficult_move(stale_move)

        self.assertLess(score, 0)

    def test_selection_soft_skips_stale_child_and_keeps_it_in_tree(self):
        self.game.finish_set_up()
        ai = self.players[0]
        self.mcts = MCTS(MCTS.build_snapshot(ai, self.game.game_type, self.players))
        self.mcts._reset_rollout_state()

        legal_moves = self.mcts.algo_infoSet.get_all_possible_moves()
        self.assertTrue(legal_moves, "Expected at least one legal move for selection test")

        valid_move = legal_moves[0]
        stale_move = Move((0, 4), (0, 5))

        root = self.mcts.root_node
        root.tried_moves = set(legal_moves)

        stale_child = Node(root, stale_move, 1 - ai.order)
        stale_child.visit_count = 5
        stale_child.value = 5
        stale_child.prior = 1.0

        valid_child = Node(root, valid_move, 1 - ai.order)
        valid_child.visit_count = 1
        valid_child.value = 0
        valid_child.prior = 0.0

        root.children = [stale_child, valid_child]

        filtered_untried_moves = self.mcts.selection()

        self.assertIsNotNone(filtered_untried_moves)
        self.assertIs(self.mcts.current_node, valid_child)
        self.assertIn(stale_child, root.children)

    def test_revealed_hunt_bonus_for_adjacent_counter(self):
        self._reset_hard_rollout_for_custom_board()

        my_spy = Piece(100, PieceType.Espion, (4, 4), 0)
        revealed_enemy_marshal = Piece(200, PieceType.Marechal, (5, 4), 1, revealed=True)

        self._place_rollout_piece(my_spy)
        self._place_rollout_piece(revealed_enemy_marshal)

        my_pieces = self.mcts.algo_infoSet.board_state.get_pieces(0)
        opp_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1)

        bonus = self.mcts._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces)

        self.assertAlmostEqual(bonus, 1.0)

    def test_revealed_hunt_bonus_for_safe_two_step_lane(self):
        self._reset_hard_rollout_for_custom_board()

        my_spy = Piece(101, PieceType.Espion, (3, 4), 0)
        revealed_enemy_marshal = Piece(201, PieceType.Marechal, (5, 4), 1, revealed=True)

        self._place_rollout_piece(my_spy)
        self._place_rollout_piece(revealed_enemy_marshal)

        my_pieces = self.mcts.algo_infoSet.board_state.get_pieces(0)
        opp_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1)

        bonus = self.mcts._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces)

        self.assertAlmostEqual(bonus, 0.5)

    def test_revealed_hunt_two_step_bonus_blocked_by_immediate_recapture_risk(self):
        self._reset_hard_rollout_for_custom_board()

        my_marshal = Piece(102, PieceType.Marechal, (3, 4), 0)
        revealed_enemy_general = Piece(202, PieceType.General, (5, 4), 1, revealed=True)
        enemy_spy_guard = Piece(203, PieceType.Espion, (4, 3), 1, revealed=True)

        self._place_rollout_piece(my_marshal)
        self._place_rollout_piece(revealed_enemy_general)
        self._place_rollout_piece(enemy_spy_guard)

        my_pieces = self.mcts.algo_infoSet.board_state.get_pieces(0)
        opp_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1)

        bonus = self.mcts._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces)

        self.assertAlmostEqual(bonus, 0.0)

    def test_revealed_hunt_bonus_uses_mcts_revealed_target(self):
        self._reset_hard_rollout_for_custom_board()

        my_spy = Piece(104, PieceType.Espion, (4, 4), 0)
        enemy_marshal = Piece(204, PieceType.Marechal, (5, 4), 1, revealed=False)
        enemy_marshal.mcts_revealed = True

        self._place_rollout_piece(my_spy)
        self._place_rollout_piece(enemy_marshal)

        my_pieces = self.mcts.algo_infoSet.board_state.get_pieces(0)
        opp_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1)

        bonus = self.mcts._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces)

        self.assertAlmostEqual(bonus, 0.75)

    def test_revealed_hunt_bonus_for_colonel_with_general_counter(self):
        self._reset_hard_rollout_for_custom_board()

        my_general = Piece(105, PieceType.General, (4, 4), 0)
        revealed_enemy_colonel = Piece(205, PieceType.Colonel, (5, 4), 1, revealed=True)

        self._place_rollout_piece(my_general)
        self._place_rollout_piece(revealed_enemy_colonel)

        my_pieces = self.mcts.algo_infoSet.board_state.get_pieces(0)
        opp_pieces = self.mcts.algo_infoSet.board_state.get_pieces(1)

        bonus = self.mcts._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces)

        self.assertAlmostEqual(bonus, 0.8)

if __name__ == "__main__":
    unittest.main()
