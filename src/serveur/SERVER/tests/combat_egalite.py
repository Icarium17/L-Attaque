import unittest
import random

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from types import SimpleNamespace

from GAME.piece import PieceType
from GAME.board import Board
from GAME.move import Move
from gameManager import GameManager
from GAME.gameRules import GameRules

class FakeLobbyManager:
    def end_game(self, winner, loser, reason):
        pass

class TestCombatEgalite(unittest.TestCase):
    def setUp(self):
        # Create 40 pieces per player with random types (excluding Drapeau and Bombe for variety)
        from USERS.user import User
        from USERS.player import Player
        from GAME.piece import Piece

        self.pieces_p1 = []
        self.pieces_p2 = []
        types = [t for t in PieceType if t not in (PieceType.Drapeau, PieceType.Bombe)]
        for i in range(40):
            t1 = random.choice(types)
            t2 = random.choice(types)
            self.pieces_p1.append(Piece(i, t1, (i%10, i//10), 0))
            self.pieces_p2.append(Piece(i, t2, (i%10, 9-i//10), 1))
        # Add Drapeau and Bombe for each player
        self.pieces_p1.append(Piece(40, PieceType.Drapeau, (0, 4), 0))
        self.pieces_p1.append(Piece(41, PieceType.Bombe, (1, 4), 0))
        self.pieces_p2.append(Piece(40, PieceType.Drapeau, (0, 5), 1))
        self.pieces_p2.append(Piece(41, PieceType.Bombe, (1, 5), 1))

        self.board = Board("original")
        for p in (self.pieces_p1, self.pieces_p2):
            self.board.set_pieces(p)
        self.lobby = FakeLobbyManager()
        user1 = User(account_id=1, key=0, username="p1", score=0)
        user2 = User(account_id=2, key=1, username="p2", score=0)
        self.players = [
            Player(user1, order=0, time_remaining=900),
            Player(user2, order=1, time_remaining=900)
        ]
        for player in self.players:
            player.known_board = Board("original")
        self.gm = GameManager(self.lobby, self.players)
        self.gm.board = self.board
        self.gm.players = self.players
        self.gm.game_rules = GameRules(self.board, "original")

    def test_draw_removes_both(self):
        # Place two pieces of equal power
        from GAME.piece import Piece
        colonel1 = Piece(100, PieceType.Colonel, (5, 5), 0)
        colonel2 = Piece(101, PieceType.Colonel, (5, 6), 1)
        self.board.set_pieces([colonel1, colonel2])
        # Simulate combat
        winner = self.gm.game_rules.combat(colonel1, colonel2)
        self.assertIsNone(winner)
        self.gm.set_boards_post_combat(winner, [colonel1, colonel2], self.board.tiles[6][5])
        self.assertIsNone(self.board.tiles[5][5].piece)
        self.assertIsNone(self.board.tiles[6][5].piece)

    def test_winner_moves_and_loser_removed(self):
        # Place a Marechal and a Lieutenant
        from GAME.piece import Piece
        marechal = Piece(200, PieceType.Marechal, (2, 2), 0)
        lieutenant = Piece(201, PieceType.Lieutenant, (2, 3), 1)
        self.board.set_pieces([marechal, lieutenant])
        winner = self.gm.game_rules.combat(marechal, lieutenant)
        self.assertEqual(winner, marechal)
        self.gm.set_boards_post_combat(winner, [lieutenant], self.board.tiles[3][2])
        self.assertIs(self.board.tiles[3][2].piece, marechal)
        self.assertIsNone(self.board.tiles[2][2].piece)

    def test_bomb_case(self):
        # Place a Bombe and a Capitaine
        from GAME.piece import Piece
        bomb = Piece(300, PieceType.Bombe, (4, 4), 1)
        capitaine = Piece(301, PieceType.Capitaine, (4, 3), 0)
        self.board.set_pieces([bomb, capitaine])
        winner = self.gm.game_rules.combat(capitaine, bomb)
        self.assertEqual(winner, bomb)
        self.gm.set_boards_post_combat(winner, [capitaine], self.board.tiles[4][4])
        self.assertIs(self.board.tiles[3][4].piece, None)
        self.assertIs(self.board.tiles[4][4].piece, bomb)

if __name__ == '__main__':
    unittest.main()
