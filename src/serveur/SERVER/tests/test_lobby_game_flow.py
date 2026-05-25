import os
import random
import sys
import unittest
from unittest.mock import MagicMock


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'SERVER'))
sys.path.insert(0, os.path.join(BASE_DIR, 'DAO'))
sys.path.insert(0, os.path.join(BASE_DIR, 'USERS'))
sys.path.insert(0, os.path.join(BASE_DIR, 'GAME'))

from GAME.move import Move
from GAME.piece import Piece, PieceType
from SERVER.lobbyManager import LobbyManager
from USERS.user import User


def build_setup_payload(order, variant=0):
    piece_types = []
    for piece_type in PieceType:
        piece_types.extend([piece_type] * piece_type.count)

    if variant == 1:
        piece_types = list(reversed(piece_types))
    elif variant == 2:
        mobile = [ptype for ptype in piece_types if ptype not in (PieceType.Bombe, PieceType.Drapeau)]
        immobile = [ptype for ptype in piece_types if ptype in (PieceType.Bombe, PieceType.Drapeau)]
        piece_types = mobile + immobile

    rows = range(6, 10)
    pieces = [
        Piece(index, piece_type, (x, y), order)
        for index, (piece_type, (x, y)) in enumerate(
            zip(piece_types, ((x, y) for y in rows for x in range(10)))
        )
    ]
    return [piece.send() for piece in pieces]


class TestLobbyGameFlow(unittest.TestCase):
    def setUp(self):
        self.lobby = LobbyManager()
        self.lobby.DAOUsers.update_score = MagicMock()
        self.lobby.DAOUsers.get_difficulty = MagicMock(return_value=0)
        self.user = User(1, "HUMAN_KEY", "Human", 0, "IDLE")
        self.lobby.active_users[self.user.key] = self.user

    def _play_first_legal_non_combat_move(self, session_key):
        game = self.lobby.games[session_key]
        player = game.get_player(session_key)

        for piece in player.pieces.values():
            if piece.type in (PieceType.Bombe, PieceType.Drapeau):
                continue

            x, y = piece.position
            for next_x, next_y in ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)):
                if not (0 <= next_x < game.board.cols and 0 <= next_y < game.board.rows):
                    continue

                if game.board.tiles[next_y][next_x].piece is not None:
                    continue

                move = Move((x, y), (next_x, next_y))
                valid, _ = game.game_rules.validate_move(player.order, move, game.board, update_history=False)
                if valid:
                    return self.lobby.move((session_key, x, y, next_x, next_y))

        self.fail("expected at least one legal non-combat opening move")

    def test_pvai_lobby_flow_does_not_end_after_setup_and_first_move(self):
        for difficulty in (0, 1, 2):
            for seed, variant in ((0, 0), (1, 2)):
                with self.subTest(difficulty=difficulty, seed=seed, variant=variant):
                    self.lobby.DAOUsers.get_difficulty.return_value = difficulty
                random.seed(seed)

                status, opponent = self.lobby.start_game((self.user.key, "ai"))
                self.assertEqual(status, "GAME_STARTED")
                self.assertEqual(opponent, "AI_Opponent")

                game = self.lobby.games[self.user.key]
                game.timers = MagicMock()
                game.ai_move_thread = MagicMock()

                setup_result = self.lobby.set_pieces((self.user.key, build_setup_payload(0, variant)))
                self.assertEqual(setup_result, ("SETUP_SUCCESS", "PLAYING"))
                self.assertEqual(self.lobby.get_status((self.user.key,))["status"], "PLAYING")

                move_result = self._play_first_legal_non_combat_move(self.user.key)

                self.assertEqual(move_result, (1, "MOVE_SUCCESS"))
                self.assertEqual(self.lobby.get_status((self.user.key,))["status"], "PLAYING")
                self.assertIsNone(game.end_reason)

                self.lobby.games.pop(self.user.key, None)
                self.user.status = "IDLE"


if __name__ == "__main__":
    unittest.main()