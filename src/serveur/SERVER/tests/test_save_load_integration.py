import unittest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from USERS.user import User
from USERS.player import Player
from USERS.aiPlayer import AIPlayer
from GAME.piece import Piece, PieceType
from gameManager import GameManager
from lobbyManager import LobbyManager

class TestGameSaveLoadIntegration(unittest.TestCase):
    def local_save(self, my_key):
        game = self.lobby.games[my_key]
        user_id = self.user.account_id
        ai_difficulty = self.ai_player.difficulty
        player_to_move = game.player_to_move
        game_state = {
            "player_boards": [player.known_board.save_board() for player in game.players],
            "board": game.board.return_pieces(),
            "scores": [player.score for player in game.players],
            "times": [player.time_remaining for player in game.players],
            "last_moves": [player.last_move for player in game.players]
        }
        game_state_json = json.dumps(game_state)
        # Simulate DB save success
        return (1, "SAVE_COMPLETE"), (user_id, ai_difficulty, player_to_move, game_state_json)

    def local_load(self, my_key, saved_tuple):
        user_id, ai_difficulty, player_to_move, game_state_json = saved_tuple
        game_state = json.loads(game_state_json)
        player_score = game_state["scores"][0] if game_state["scores"] else 0
        ai_score = game_state["scores"][1] if game_state["scores"] else 0
        boards = []
        for b in [game_state["board"], game_state["player_boards"][0], game_state["player_boards"][1]]:
            boards.append(self.lobby.convert_pieces(b))
        player = Player(self.user, 0, player_score)
        player.load(boards[1], game_state["times"][0], game_state["last_moves"][0])
        ai_user = User(-1, "AI_KEY", "AI_Opponent", ai_score, "IDLE")
        ai_player = AIPlayer(ai_user, 1, ai_difficulty, ai_score)
        ai_player.load(boards[2], game_state["times"][1], game_state["last_moves"][1])
        players = [player, ai_player]
        game = GameManager.load(self.lobby, players, player_to_move, boards[0])
        self.lobby.games[player.key] = game
        return (1, "RESTORED")
    
    def setUp(self):
        # Setup LobbyManager and register user
        self.lobby = LobbyManager()
        self.user = User(1, "SESSION_KEY", "TestPlayer", 0, "IDLE")
        self.ai_user = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")
        self.player = Player(self.user, 0)
        self.ai_player = AIPlayer(self.ai_user, 1, 2)
        self.lobby.active_users[self.user.key] = self.user
        self.lobby.games[self.user.key] = GameManager(self.lobby, [self.player, self.ai_player])
        # Set up some pieces for both players
        for p in [self.player, self.ai_player]:
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
        self.lobby.games[self.user.key].board.set_pieces(all_pieces)
        self.lobby.games[self.user.key].player_to_move = 0
        self.player.time_remaining = 100
        self.ai_player.time_remaining = 100
        self.player.last_move = None
        self.ai_player.last_move = None
        self.player.score = 10
        self.ai_player.score = 20

    def test_save_and_load_integration(self):
        # Save using local_save (bypassing DB)
        save_result, saved_tuple = self.local_save(self.user.key)
        self.assertEqual(save_result[0], 1)
        # Remove the game to simulate a fresh load
        del self.lobby.games[self.user.key]
        # Load using local_load (bypassing DB)
        load_result = self.local_load(self.user.key, saved_tuple)
        self.assertEqual(load_result[0], 1)
        # Check that the loaded game is present and correct
        loaded_game = self.lobby.games[self.user.key]
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

        # Check belief pieces for both player and ai_player
        self.assert_belief_pieces_equal(self.player, loaded_game.players[0])
        self.assert_belief_pieces_equal(self.ai_player, loaded_game.players[1])

    def assert_belief_pieces_equal(self, orig_player, loaded_player):
            # Compare keys
            self.assertEqual(set(orig_player.belief_pieces.keys()), set(loaded_player.belief_pieces.keys()))
            for key in orig_player.belief_pieces:
                orig_bp = orig_player.belief_pieces[key]
                loaded_bp = loaded_player.belief_pieces[key]
                self.assertEqual(orig_bp.id, loaded_bp.id)
                self.assertEqual(orig_bp.position, loaded_bp.position)
                self.assertEqual(orig_bp.owner, loaded_bp.owner)
                # Compare probabilities dict
                self.assertEqual(orig_bp.probabilities, loaded_bp.probabilities)
                # Compare evidence_weights dict
                self.assertEqual(orig_bp.evidence_weights, loaded_bp.evidence_weights)

if __name__ == "__main__":
    unittest.main()
