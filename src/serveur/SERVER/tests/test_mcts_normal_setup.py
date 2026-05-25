import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from GAME.gameRules import GameRules
from GAME.board import Board
from GAME.piece import PieceType
from SERVER.gameManager import GameManager
from SERVER.lobbyManager import LobbyManager

class TestMCTSWithNormalAISetup(unittest.TestCase):
    def setUp(self):
        # Create dummy lobby and users
        self.lobby = LobbyManager()
        user1 = User(0, "ai1_key", "AI_1", 0, "IDLE")
        user2 = User(1, "ai2_key", "AI_2", 0, "IDLE")
        self.ai1 = AIPlayer(user1, 0, 1)
        self.ai2 = AIPlayer(user2, 1, 1)
        self.players = [self.ai1, self.ai2]
        self.gm = GameManager(self.lobby, self.players, "original")

        # Simulate both AIs placing their pieces (normal game flow)
        for i, ai in enumerate(self.players):
            ai_pieces = ai.setup_pieces()
            self.gm.board.set_pieces(ai_pieces)
            ai.position_pieces(self.gm.clone_pieces(ai_pieces))
            ai.sync_owned_pieces()
            self.gm.players_ready.add(ai.key)
            ai.game_rules = self.gm.game_rules
            ai.players = self.players

        # Call finish_set_up to set up belief pieces, etc.
        self.gm.finish_set_up()

    def test_board_and_belief_pieces(self):
        # Check that both AIs have belief_pieces set for the opponent
        self.assertTrue(len(self.ai1.belief_pieces) > 0)
        self.assertTrue(len(self.ai2.belief_pieces) > 0)
        # Check that the board is set up
        self.assertIsNotNone(self.gm.board)
        # You can now add MCTS tests here using self.gm, self.ai1, self.ai2

    def test_mcts_returns_move(self):
        """
        Run MCTS for the first AI and check that it returns a move.
        """
        from ALGO.mcts import MCTS
        mcts = MCTS(MCTS.build_snapshot(self.ai1, self.gm.game_type, self.players))
        # Run a few iterations to ensure a move is found
        for _ in range(10):
            mcts.algo()
        move = mcts.get_best_move()
        print(f"MCTS returned move: {move}")
        self.assertIsNotNone(move, "MCTS did not return a move")

if __name__ == "__main__":
    unittest.main()
