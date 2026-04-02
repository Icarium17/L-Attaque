import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from MCTS import MCTS
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from GAME.gameRules import GameRules
from GAME.board import Board
from USERS.player import Player
from gameManager import GameManager
from lobbyManager import LobbyManager

class TestMCTS(unittest.TestCase):
    def setUp(self):
        # Create users and AI players
        user1 = User(0, "aaa", "AI_1", 0)
        ai1 = AIPlayer(user1, 0, 0)
        user2 = User(1, "bbb", "AI_2", 0)
        ai2 = AIPlayer(user2, 1, 0)
        self.players = [ai1, ai2]

        # Create game and rules
        self.lobby = LobbyManager()
        self.game = GameManager(self.lobby, self.players, "original")
        
        for i in range(0, 2):
            self.game.setup_ai_player(i)

        for y, row in enumerate(self.game.board.tiles):
            for x, tile in enumerate(row):
                print(f"({x}, {y}): {tile.piece} {tile.piece.type if tile.piece is not None else None}")


        # MCTS instance
        self.mcts = MCTS(ai1, self.game.game_rules, self.players)

    def test_algo_runs(self):
        try:
            print(self.mcts.algo())
        except Exception as e:
            self.fail(f"MCTS algo() raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
