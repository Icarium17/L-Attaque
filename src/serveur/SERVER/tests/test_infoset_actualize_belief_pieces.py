import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ALGO.infoSet import InfoSet
from GAME.piece import BeliefPiece, Piece, PieceType
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from gameManager import GameManager
from lobbyManager import LobbyManager


class TestInfoSetActualizeBeliefPieces(unittest.TestCase):
    def setUp(self):
        user1 = User(0, "aaa", "AI_1", 0)
        ai1 = AIPlayer(user1, 0, 1)
        user2 = User(1, "bbb", "AI_2", 0)
        ai2 = AIPlayer(user2, 1, 1)
        self.players = [ai1, ai2]

        self.lobby = LobbyManager()
        self.game = GameManager(self.lobby, self.players, "original")

        for i in range(0, 2):
            self.game.setup_ai_player(i)

        self.game.finish_set_up()
        self.ai = self.players[0]

    def _make_info_set(self):
        return InfoSet(copy.deepcopy(self.ai.known_board), self.ai.order, self.game.game_rules)

    def _assert_opponent_tiles_are_concrete_pieces(self, info_set):
        opponent_order = 1 - self.ai.order
        concrete_pieces = info_set.board_state.get_pieces(opponent_order)

        self.assertTrue(concrete_pieces)
        self.assertTrue(all(isinstance(piece, Piece) for piece in concrete_pieces.values()))
        self.assertTrue(all(not isinstance(piece, BeliefPiece) for piece in concrete_pieces.values()))
        self.assertTrue(all(piece.type is not None for piece in concrete_pieces.values()))

        for row in info_set.board_state.tiles:
            for tile in row:
                if tile.piece is not None and tile.piece.owner == opponent_order:
                    self.assertNotIsInstance(tile.piece, BeliefPiece)

    def test_actualize_replaces_hidden_belief_pieces_in_normal_case(self):
        info_set = self._make_info_set()
        hidden_beliefs = self.ai.get_hidden_belief_pieces()

        self.assertTrue(hidden_beliefs)

        info_set.actualize_belief_pieces(
            hidden_beliefs,
            self.ai.opponent_belief_pieces_left.copy(),
        )

        self.assertFalse(info_set.actualize_stats["used_mismatch_recovery"])
        self._assert_opponent_tiles_are_concrete_pieces(info_set)

    def test_actualize_replaces_hidden_belief_pieces_when_backtracking_falls_back(self):
        info_set = self._make_info_set()
        hidden_beliefs = self.ai.get_hidden_belief_pieces()

        for belief_piece in hidden_beliefs:
            for piece_type in list(belief_piece.probabilities.keys()):
                belief_piece.probabilities[piece_type] = 1.0 if piece_type == PieceType.Drapeau else 0.0

        pieces_left = {piece_type: 0 for piece_type in self.ai.opponent_belief_pieces_left}
        pieces_left[PieceType.Drapeau] = 1

        info_set.actualize_belief_pieces(hidden_beliefs, pieces_left)

        self.assertTrue(info_set.actualize_stats["used_random_fallback"])
        self._assert_opponent_tiles_are_concrete_pieces(info_set)

    def test_actualize_replaces_hidden_belief_pieces_when_hidden_ids_are_stale(self):
        info_set = self._make_info_set()
        hidden_beliefs = self.ai.get_hidden_belief_pieces()
        stale_hidden_beliefs = hidden_beliefs + [BeliefPiece(9999, (-1, -1), 1 - self.ai.order)]

        info_set.actualize_belief_pieces(
            stale_hidden_beliefs,
            self.ai.opponent_belief_pieces_left.copy(),
        )

        self.assertTrue(info_set.actualize_stats["used_mismatch_recovery"])
        self.assertTrue(info_set.actualize_stats["used_random_fallback"])
        self.assertEqual(info_set.actualize_stats["recursive_calls"], 0)
        self._assert_opponent_tiles_are_concrete_pieces(info_set)

    def test_actualize_replaces_hidden_belief_pieces_when_hidden_list_is_empty(self):
        info_set = self._make_info_set()

        info_set.actualize_belief_pieces([], self.ai.opponent_belief_pieces_left.copy())

        self.assertTrue(info_set.actualize_stats["used_mismatch_recovery"])
        self.assertTrue(info_set.actualize_stats["used_random_fallback"])
        self.assertEqual(info_set.actualize_stats["recursive_calls"], 0)
        self._assert_opponent_tiles_are_concrete_pieces(info_set)

    def test_clone_for_rollout_creates_independent_board_with_fresh_cache(self):
        info_set = self._make_info_set()
        hidden_beliefs = self.ai.get_hidden_belief_pieces()

        info_set.sync_opponent_knowledge(
            hidden_beliefs,
            self.ai.get_revealed_opponent_pieces(),
        )
        info_set.get_all_possible_moves()

        cloned_info_set = info_set.clone_for_rollout()

        self.assertIsNot(cloned_info_set, info_set)
        self.assertIsNot(cloned_info_set.board_state, info_set.board_state)
        self.assertEqual(cloned_info_set.player_turn, info_set.player_turn)
        self.assertIs(cloned_info_set.game_rules, info_set.game_rules)
        self.assertEqual(cloned_info_set._possible_moves_cache, {0: {}, 1: {}})

        original_piece = info_set.board_state.tiles[0][0].piece
        cloned_piece = cloned_info_set.board_state.tiles[0][0].piece
        self.assertIsNot(cloned_piece, original_piece)
        self.assertEqual(cloned_piece.id, original_piece.id)
        self.assertEqual(cloned_piece.position, original_piece.position)
        self.assertEqual(cloned_piece.revealed, original_piece.revealed)

        cloned_piece.position = (9, 9)
        self.assertNotEqual(cloned_piece.position, original_piece.position)


if __name__ == "__main__":
    unittest.main()