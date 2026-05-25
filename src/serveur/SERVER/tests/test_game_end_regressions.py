import os
import random
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, patch


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GAME.move import Move
from GAME.board import Board
from GAME.piece import Piece, PieceType
from USERS.aiPlayer import AIPlayer
from USERS.player import Player
from USERS.user import User
from gameManager import AI_MOVE_EXECUTOR, GameManager, PlayerTimer


class DummyLobbyManager:
    def __init__(self):
        self.ended_games = []

    def end_game(self, winner, loser, reason):
        self.ended_games.append((winner.username, loser.username, reason))

    def too_long_wait(self, key):
        return None


class FakeTimer:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback

    def start(self):
        return None


def build_setup(order, variant=0):
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
    positions = [(x, y) for y in rows for x in range(10)]

    return [
        Piece(index, piece_type, positions[index], order)
        for index, piece_type in enumerate(piece_types)
    ]


class TestGameEndRegressions(unittest.TestCase):
    def _create_pvp_game(self):
        lobby = DummyLobbyManager()
        player_one = Player(User(1, "key1", "Alice", 0, "IDLE"), 0)
        player_two = Player(User(2, "key2", "Bob", 0, "IDLE"), 1)
        game = GameManager(lobby, [player_one, player_two], status="SETTING_UP")
        game.timers = MagicMock()
        return lobby, game

    def _play_first_legal_non_combat_move(self, game, player_key):
        player = game.get_player(player_key)
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
                    return game.make_move(player_key, move)

        self.fail("expected at least one legal non-combat opening move")

    def _get_sorted_legal_non_combat_moves(self, game, player):
        moves = game.game_rules.get_remaining_moves(player.pieces, player.order, game.board)
        non_combat_moves = []

        for move in moves:
            target_x, target_y = move.moveTo
            if game.board.tiles[target_y][target_x].piece is None:
                non_combat_moves.append(move)

        return sorted(
            non_combat_moves,
            key=lambda move: (move.moveFrom[1], move.moveFrom[0], move.moveTo[1], move.moveTo[0]),
        )

    def _player_end_state_facts(self, game, player):
        opponent = game.players[1 - player.order]
        return {
            "flag_captured": game.game_rules.check_flag_captured(player.pieces, player.pieces_left),
            "no_mobile_pieces": game.game_rules.check_no_mobile_pieces(player.pieces, player.pieces_left),
            "has_remaining_moves": game.game_rules.check_remaining_moves(player.order, player.pieces, game.board),
            "impassable_bomb_wall": game.game_rules.check_impassable_bomb_wall(
                player.pieces,
                opponent.pieces,
                opponent.order,
                game.board,
                player.pieces_left,
                opponent.pieces_left,
                opponent.flag_position,
            ),
            "flag_position": player.flag_position,
            "piece_count": len(player.pieces),
        }

    def _format_end_state_facts(self, game):
        return {
            player.username: self._player_end_state_facts(game, player)
            for player in game.players
        }

    def _assert_owned_piece_cache_matches_board(self, game, label):
        for player in game.players:
            board_pieces = game.board.get_pieces(player.order)
            cache_summary = {
                piece_id: (piece.type, piece.position)
                for piece_id, piece in player.pieces.items()
            }
            board_summary = {
                piece_id: (piece.type, piece.position)
                for piece_id, piece in board_pieces.items()
            }
            self.assertEqual(
                cache_summary,
                board_summary,
                f"{label}: cached pieces diverged from board for {player.username}",
            )

            expected_flag_position = next(
                (piece.position for piece in board_pieces.values() if piece.type == PieceType.Drapeau),
                None,
            )
            self.assertEqual(
                player.flag_position,
                expected_flag_position,
                f"{label}: cached flag position diverged for {player.username}",
            )

    def _assert_end_state_matches_live_board(self, game, label):
        for player in game.players:
            board_pieces = game.board.get_pieces(player.order)
            opponent_pieces = game.board.get_pieces(1 - player.order)

            cached_result = game.game_rules.check_player_end_state(player, game.players, game.board)
            board_result = game.game_rules.check_player_end_state(
                player,
                game.players,
                game.board,
                board_pieces,
                opponent_pieces,
            )

            self.assertEqual(
                cached_result[0],
                board_result[0],
                f"{label}: cached end-state boolean diverged from board for {player.username}",
            )

            if cached_result[1] is None or board_result[1] is None:
                self.assertEqual(
                    cached_result[1],
                    board_result[1],
                    f"{label}: cached end-state payload diverged from board for {player.username}",
                )
            else:
                cached_winner, cached_loser, cached_reason = cached_result[1]
                board_winner, board_loser, board_reason = board_result[1]
                self.assertEqual(
                    (cached_winner.username, cached_loser.username, cached_reason),
                    (board_winner.username, board_loser.username, board_reason),
                    f"{label}: cached end-state payload diverged from board for {player.username}",
                )

    def _prepare_move_for_submission(self, player, move):
        submitted_move = Move(move.moveFrom, move.moveTo)
        if player.order == 1 and not isinstance(player, AIPlayer):
            submitted_move.invert()
        return submitted_move

    def _set_tactical_position(self, game, pieces):
        game.board = Board(game.game_type)
        game.board.set_pieces(pieces)

        for player in game.players:
            player.known_board = Board(game.game_type)
            player.known_board.set_pieces([piece.clone() for piece in pieces])
            player.sync_owned_pieces()

        game.status = "PLAYING"
        game.player_to_move = 0
        game.winner = None
        game.loser = None
        game.end_reason = None

    def _execute_scripted_move(self, game, lobby, move):
        current_player = game.players[game.player_to_move]
        label = f"player={current_player.username}, move={move.moveFrom}->{move.moveTo}"
        self._assert_live_game_state(game, lobby, f"before scripted {label}")

        submitted_move = self._prepare_move_for_submission(current_player, move)

        with patch("gameManager.threading.Timer", FakeTimer):
            move_result = game.make_move(current_player.key, submitted_move)

        self.assertIn(move_result, ((1, "MOVE_SUCCESS"), (0, "BATTLE_HAPPENING")), label)

        if move_result == (0, "BATTLE_HAPPENING"):
            self.assertEqual(game.status, "BATTLE", label)
            game.change_turn()

        self._assert_live_game_state(game, lobby, f"after scripted {label}")

    def _run_scripted_sequence(self, game, lobby, moves):
        for move in moves:
            self._execute_scripted_move(game, lobby, move)

    def _create_pvai_game(self, difficulty=0):
        lobby = DummyLobbyManager()
        human = Player(User(10, "human", "Human", 0, "IDLE"), 0)
        ai = AIPlayer(User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE"), 1, difficulty)
        game = GameManager(lobby, [human, ai], status="PLAYING")
        game.timers = MagicMock()
        game.ai_move_thread = MagicMock()
        return lobby, game

    def _assert_live_game_state(self, game, lobby, label):
        facts = self._format_end_state_facts(game)
        diagnostic = (
            f"{label}: status={game.status}, end_reason={game.end_reason}, "
            f"winner={getattr(game.winner, 'username', None)}, loser={getattr(game.loser, 'username', None)}, "
            f"facts={facts}, ended_games={lobby.ended_games}"
        )

        self.assertEqual(game.status, "PLAYING", diagnostic)
        self.assertIsNone(game.end_reason, diagnostic)
        self.assertEqual(lobby.ended_games, [], diagnostic)

        self._assert_owned_piece_cache_matches_board(game, label)
        self._assert_end_state_matches_live_board(game, label)

        for player in game.players:
            player_facts = facts[player.username]
            self.assertFalse(player_facts["flag_captured"], diagnostic)
            self.assertFalse(player_facts["no_mobile_pieces"], diagnostic)
            self.assertTrue(player_facts["has_remaining_moves"], diagnostic)

    def _play_opening_sequence(self, game, lobby, plies, chooser=None):
        for ply in range(plies):
            current_player = game.players[game.player_to_move]
            label = f"ply={ply}, player={current_player.username}"
            self._assert_live_game_state(game, lobby, f"before {label}")

            if chooser is None:
                moves = self._get_sorted_legal_non_combat_moves(game, current_player)
                self.assertTrue(moves, f"{label}: expected a legal non-combat move")
                move = moves[0]
            else:
                move = chooser(game, current_player)

            submitted_move = self._prepare_move_for_submission(current_player, move)
            move_result = game.make_move(current_player.key, submitted_move)
            self.assertEqual(move_result, (1, "MOVE_SUCCESS"), f"{label}: move={move}")
            self._assert_live_game_state(game, lobby, f"after {label}")

    def test_pvp_multiple_setups_do_not_end_immediately(self):
        variants = ((0, 0), (1, 1), (2, 0))

        for player_one_variant, player_two_variant in variants:
            with self.subTest(player_one_variant=player_one_variant, player_two_variant=player_two_variant):
                lobby, game = self._create_pvp_game()

                self.assertEqual(game.check_valid_setup("key1", build_setup(0, player_one_variant)), "SETUP_SUCCESS")
                self.assertEqual(game.check_valid_setup("key2", build_setup(1, player_two_variant)), "SETUP_SUCCESS")

                self.assertEqual(game.status, "PLAYING")
                self.assertFalse(game.check_end_state())

                move_result = self._play_first_legal_non_combat_move(game, "key1")

                self.assertEqual(move_result, (1, "MOVE_SUCCESS"))
                self.assertEqual(lobby.ended_games, [])

    def test_pvai_multiple_ai_setups_do_not_end_immediately(self):
        human_variants = {
            0: 0,
            1: 2,
            2: 0,
        }

        for difficulty in (0, 1, 2):
            for seed in (0, 1, 2):
                with self.subTest(difficulty=difficulty, seed=seed):
                    random.seed(seed)

                    lobby = DummyLobbyManager()
                    human = Player(User(10, "human", "Human", 0, "IDLE"), 0)
                    ai = AIPlayer(User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE"), 1, difficulty)
                    game = GameManager(lobby, [human, ai], status="SETTING_UP")
                    game.timers = MagicMock()
                    game.ai_move_thread = MagicMock()

                    self.assertEqual(game.check_valid_setup("human", build_setup(0, human_variants[difficulty])), "SETUP_SUCCESS")
                    self.assertEqual(game.status, "PLAYING")
                    self.assertFalse(game.check_end_state())

                    move_result = self._play_first_legal_non_combat_move(game, "human")

                    self.assertEqual(move_result, (1, "MOVE_SUCCESS"))
                    self.assertEqual(lobby.ended_games, [])

    def test_pvai_reports_queued_status_while_shared_worker_is_busy(self):
        worker_started = threading.Event()
        release_worker = threading.Event()

        def block_shared_worker():
            worker_started.set()
            release_worker.wait(timeout=2)

        blocker = AI_MOVE_EXECUTOR.submit(block_shared_worker)
        self.assertTrue(worker_started.wait(timeout=1), "expected blocker task to occupy AI worker")

        try:
            lobby, game = self._create_pvai_game(difficulty=0)
            game.player_to_move = 0
            game.check_end_state = MagicMock(return_value=False)

            game.change_turn()

            self.assertEqual(game.ai_move_status, "queued")
            self.assertIsNotNone(game.ai_move_future)
            self.assertFalse(game.ai_move_future.running())
            self.assertEqual(game.get_status("human")["ai_status"], "queued")
        finally:
            release_worker.set()
            blocker.result(timeout=1)
            if game.ai_move_future is not None:
                game.ai_move_future.result(timeout=1)

    def test_pvp_opening_sequences_stay_live_across_many_plies(self):
        variants = ((0, 0), (1, 1), (2, 0), (2, 1))

        for player_one_variant, player_two_variant in variants:
            with self.subTest(player_one_variant=player_one_variant, player_two_variant=player_two_variant):
                lobby, game = self._create_pvp_game()

                self.assertEqual(game.check_valid_setup("key1", build_setup(0, player_one_variant)), "SETUP_SUCCESS")
                self.assertEqual(game.check_valid_setup("key2", build_setup(1, player_two_variant)), "SETUP_SUCCESS")

                self._play_opening_sequence(game, lobby, plies=12)

    def test_pvai_seeded_opening_sequences_stay_live_across_many_plies(self):
        human_variants = {
            0: 0,
            1: 2,
            2: 0,
        }

        for difficulty in (0, 1, 2):
            for seed in range(6):
                with self.subTest(difficulty=difficulty, seed=seed):
                    random.seed(seed)

                    lobby = DummyLobbyManager()
                    human = Player(User(10, "human", "Human", 0, "IDLE"), 0)
                    ai = AIPlayer(User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE"), 1, difficulty)
                    game = GameManager(lobby, [human, ai], status="SETTING_UP")
                    game.timers = MagicMock()
                    game.ai_move_thread = MagicMock()

                    self.assertEqual(game.check_valid_setup("human", build_setup(0, human_variants[difficulty])), "SETUP_SUCCESS")
                    self._play_opening_sequence(game, lobby, plies=12)

    def test_pvp_scripted_combat_sequence_keeps_game_alive(self):
        lobby, game = self._create_pvp_game()

        pieces = [
            Piece(1, PieceType.Drapeau, (0, 9), 0),
            Piece(2, PieceType.Bombe, (1, 9), 0),
            Piece(3, PieceType.Marechal, (4, 6), 0),
            Piece(4, PieceType.Colonel, (5, 7), 0),
            Piece(5, PieceType.Lieutenant, (8, 8), 0),
            Piece(101, PieceType.Drapeau, (9, 0), 1),
            Piece(102, PieceType.Bombe, (8, 0), 1),
            Piece(103, PieceType.Sergent, (4, 5), 1),
            Piece(104, PieceType.Marechal, (5, 4), 1),
            Piece(105, PieceType.Lieutenant, (8, 3), 1),
        ]
        self._set_tactical_position(game, pieces)

        scripted_moves = [
            Move((4, 6), (4, 5)),
            Move((5, 4), (5, 5)),
            Move((5, 7), (5, 6)),
            Move((5, 5), (5, 6)),
            Move((8, 8), (8, 7)),
            Move((8, 3), (8, 4)),
            Move((8, 7), (8, 6)),
            Move((8, 4), (8, 5)),
            Move((8, 6), (8, 5)),
        ]

        self._run_scripted_sequence(game, lobby, scripted_moves)

    def test_pvai_scripted_combat_sequence_keeps_game_alive(self):
        lobby, game = self._create_pvai_game(difficulty=1)

        pieces = [
            Piece(1, PieceType.Drapeau, (0, 9), 0),
            Piece(2, PieceType.Bombe, (1, 9), 0),
            Piece(3, PieceType.Marechal, (4, 6), 0),
            Piece(4, PieceType.Colonel, (5, 7), 0),
            Piece(5, PieceType.Lieutenant, (8, 8), 0),
            Piece(101, PieceType.Drapeau, (9, 0), 1),
            Piece(102, PieceType.Bombe, (8, 0), 1),
            Piece(103, PieceType.Sergent, (4, 5), 1),
            Piece(104, PieceType.Marechal, (5, 4), 1),
            Piece(105, PieceType.Lieutenant, (8, 3), 1),
        ]
        self._set_tactical_position(game, pieces)

        scripted_moves = [
            Move((4, 6), (4, 5)),
            Move((5, 4), (5, 5)),
            Move((5, 7), (5, 6)),
            Move((5, 5), (5, 6)),
            Move((8, 8), (8, 7)),
            Move((8, 3), (8, 4)),
            Move((8, 7), (8, 6)),
            Move((8, 4), (8, 5)),
            Move((8, 6), (8, 5)),
        ]

        self._run_scripted_sequence(game, lobby, scripted_moves)

    def test_pvp_draw_combat_does_not_trigger_false_end_state(self):
        lobby, game = self._create_pvp_game()

        pieces = [
            Piece(1, PieceType.Drapeau, (0, 9), 0),
            Piece(2, PieceType.Bombe, (1, 9), 0),
            Piece(3, PieceType.Colonel, (5, 6), 0),
            Piece(4, PieceType.Major, (8, 8), 0),
            Piece(101, PieceType.Drapeau, (9, 0), 1),
            Piece(102, PieceType.Bombe, (8, 0), 1),
            Piece(103, PieceType.Colonel, (5, 5), 1),
            Piece(104, PieceType.Major, (8, 3), 1),
        ]
        self._set_tactical_position(game, pieces)

        scripted_moves = [
            Move((5, 6), (5, 5)),
            Move((8, 3), (8, 4)),
            Move((8, 8), (8, 7)),
            Move((8, 4), (8, 5)),
        ]

        self._run_scripted_sequence(game, lobby, scripted_moves)


class TestPlayerTimerRegressions(unittest.TestCase):
    def test_shutdown_cancels_pending_delayed_resume(self):
        players = [
            Player(User(1, "key1", "Alice", 0, "IDLE"), 0),
            Player(User(2, "key2", "Bob", 0, "IDLE"), 1),
        ]
        timer = PlayerTimer(players, [player.time_remaining for player in players], MagicMock())

        timer.start(0)
        original_start = timer.start
        timer.start = MagicMock(wraps=original_start)

        timer.stop(0.05)
        timer.shutdown()
        time.sleep(0.1)

        timer.start.assert_not_called()


if __name__ == "__main__":
    unittest.main()