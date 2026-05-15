import unittest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from USERS.user import User
from USERS.player import Player
from USERS.aiPlayer import AIPlayer
from gameManager import GameManager

class TestGameSaveLoad(unittest.TestCase):
    def setUp(self):
        # Create users
        user = User(1, "SESSION_KEY", "TestPlayer", 0, "IDLE")
        ai_user = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")
        # Create players
        self.player = Player(user, 0)
        self.ai_player = AIPlayer(ai_user, 1, 2)  # difficulty 2
        self.players = [self.player, self.ai_player]
        # Create game
        self.game = GameManager(None, self.players)
        # Set up some pieces for both players
        from GAME.piece import Piece, PieceType
        for p in self.players:
            pieces = [
                Piece(0, PieceType.Marechal, (0, 0), p.order),
                Piece(1, PieceType.Drapeau, (1, 0), p.order)
            ]
            p.known_board.set_pieces(pieces)
            p.position_pieces(pieces)
            p.sync_owned_pieces()
        all_pieces = [
            Piece(0, PieceType.Marechal, (0, 0), 0),
            Piece(1, PieceType.Drapeau, (1, 0), 0),
            Piece(0, PieceType.Marechal, (0, 0), 1),
            Piece(1, PieceType.Drapeau, (1, 0), 1)
        ]
        self.game.board.set_pieces(all_pieces)
        self.game.player_to_move = 0
        self.player.time_remaining = 100
        self.ai_player.time_remaining = 100
        self.player.last_move = None
        self.ai_player.last_move = None
        self.player.score = 10
        self.ai_player.score = 20

    def test_save_and_load(self):
        # Save the game
        user_id, ai_difficulty, player_to_move, game_state_json = self.game.save(self.player.key)
        # Simulate loading
        game_state = json.loads(game_state_json)
        loaded_players = [
            Player(self.player.user, self.player.score),
            AIPlayer(self.ai_player.user, 1, ai_difficulty)
        ]
        loaded_players[0].load(game_state["player_boards"][0], game_state["times"][0], game_state["last_moves"][0])
        loaded_players[1].load(game_state["player_boards"][1], game_state["times"][1], game_state["last_moves"][1])
        loaded_game = GameManager.load(None, loaded_players, player_to_move, game_state["board"])
        # Check player info
        self.assertEqual(loaded_game.players[0].user.username, self.player.user.username)
        self.assertEqual(loaded_game.players[1].user.username, self.ai_player.user.username)
        self.assertEqual(loaded_game.players[0].score, self.player.score)
        self.assertEqual(loaded_game.players[1].score, self.ai_player.score)
        # Check pieces
        orig_pieces = self.player.known_board.return_pieces()
        loaded_pieces = loaded_game.players[0].known_board.return_pieces()
        self.assertEqual(len(orig_pieces), len(loaded_pieces))
        for op, lp in zip(orig_pieces, loaded_pieces):
            self.assertEqual(op["id"], lp["id"])
            self.assertEqual(op["type"], lp["type"])
            self.assertEqual(op["position"], lp["position"])
            self.assertEqual(op["owner"], lp["owner"])

if __name__ == "__main__":
    unittest.main()
