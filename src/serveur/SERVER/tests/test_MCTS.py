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
from GAME.piece import BeliefPiece, PieceType
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

if __name__ == "__main__":
    unittest.main()
