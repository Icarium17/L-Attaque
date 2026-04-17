# python
# src/serveur/SERVER/test_gameManager.py

# Absolute import of the class under test (namespace package)


from types import SimpleNamespace
import unittest
import sys
import os



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameManager import GameManager
from GAME.piece import PieceType




class FakeKnownBoard:
    def __init__(self):
        self.removed = []
        self.moved = []

    def remove_piece(self, piece):
        self.removed.append(piece)

    def move_post_combat(self, piece, y, x):
        self.moved.append((piece, y, x))


class FakeBoard:
    def __init__(self):
        self.removed = []
        self.moved = []

    def remove_piece(self, piece):
        self.removed.append(piece)

    def move_post_combat(self, piece, y, x):
        self.moved.append((piece, y, x))


class FakePlayer:
    def __init__(self, key):
        self.key = key
        self.known_board = FakeKnownBoard()
        self.removed_pieces = []
        self.winner_updates = []
        self.loser_updates = []
        self.time_remaining = 100
        # also provide attributes referenced elsewhere if needed
        self.user = SimpleNamespace(status=None, score=0, username=f"user_{key}")

    def remove_piece(self, piece):
        self.removed_pieces.append(piece)

    def update_belief_state_winner(self, winner):
        self.winner_updates.append(winner)

    def update_belief_state_loser(self, loser):
        self.loser_updates.append(loser)


class TestSetBoardsPostCombat(unittest.TestCase):
    def setUp(self):
        # Create GameManager instance without invoking __init__
        self.gm = object.__new__(GameManager)
        # Replace players and board with fakes
        self.p1 = FakePlayer(0)
        self.p2 = FakePlayer(1)
        self.gm.players = [self.p1, self.p2]
        self.gm.board = FakeBoard()

    def make_piece(self, pid, ptype=None):
        # create a simple piece object with id and type attributes
        if ptype is None:
            # use a non-bombe dummy type
            ptype = SimpleNamespace(name="Soldat")
        return SimpleNamespace(id=pid, type=ptype)

    def test_draw_removes_both_from_all_boards(self):
        # draw scenario: winner is None, both pieces are losers
        attacker = self.make_piece("attacker")
        defender = self.make_piece("defender")
        tile = SimpleNamespace(piece=defender, y=4, x=5)

        losers = [attacker, defender]
        # Call method under test
        self.gm.set_boards_post_combat(None, losers, tile)

        # Both losers should have been removed from each player's known board and via player.remove_piece
        for loser in losers:
            # player-level removal
            self.assertIn(loser, self.p1.removed_pieces, "p1 should have had loser removed")
            self.assertIn(loser, self.p2.removed_pieces, "p2 should have had loser removed")
            # known_board removal
            self.assertIn(loser, self.p1.known_board.removed, "p1.known_board should have recorded removal")
            self.assertIn(loser, self.p2.known_board.removed, "p2.known_board should have recorded removal")
            # main board removal
            self.assertIn(loser, self.gm.board.removed, "main board should have removed the loser")

        # update_belief_state_loser should be called for both losers on each player
        self.assertEqual(self.p1.loser_updates.count(attacker), 1)
        self.assertEqual(self.p1.loser_updates.count(defender), 1)
        self.assertEqual(self.p2.loser_updates.count(attacker), 1)
        self.assertEqual(self.p2.loser_updates.count(defender), 1)

        # No move_post_combat should have been invoked on known_board or main board
        self.assertEqual(self.p1.known_board.moved, [])
        self.assertEqual(self.p2.known_board.moved, [])
        self.assertEqual(self.gm.board.moved, [])

    def test_attacker_wins_moves_winner_and_updates_beliefs(self):
        # attacker wins and moves onto defender's tile (tile.piece is defender)
        # winner.type must not be PieceType.Bombe to trigger move_post_combat
        dummy_type = SimpleNamespace()
        attacker = self.make_piece("attacker", ptype=dummy_type)
        defender = self.make_piece("defender", ptype=dummy_type)
        tile = SimpleNamespace(piece=defender, y=2, x=3)

        losers = [defender]
        # Call method under test with winner present
        self.gm.set_boards_post_combat(attacker, losers, tile)

        # For winner branch, each player's known_board.move_post_combat should be called with (winner, y, x)
        self.assertIn((attacker, 2, 3), self.p1.known_board.moved, "p1.known_board should have move_post_combat called for the winner")
        self.assertIn((attacker, 2, 3), self.p2.known_board.moved, "p2.known_board should have move_post_combat called for the winner")
        # main board should have move_post_combat called
        self.assertIn((attacker, 2, 3), self.gm.board.moved, "main board should have move_post_combat called for the winner")

        # In this branch, losers should NOT be removed via board.remove_piece (the code does not remove losers from board in winner branch)
        self.assertEqual(self.gm.board.removed, [], "main board.remove_piece should not have been called in winner branch")

        # Belief updates: winner updates and loser updates must be called
        self.assertIn(attacker, self.p1.winner_updates, "p1 should have received winner belief update")
        self.assertIn(attacker, self.p2.winner_updates, "p2 should have received winner belief update")
        self.assertIn(defender, self.p1.loser_updates, "p1 should have received loser belief update for defender")
        self.assertIn(defender, self.p2.loser_updates, "p2 should have received loser belief update for defender")

    def test_winner_bombe_does_not_move_but_losers_removed(self):
        # If winner.type == PieceType.Bombe, the code skips move_post_combat and falls through to else branch removal
        # Construct a winner whose type equals PieceType.Bombe
        # PieceType is imported from the module; create a piece with that type
        bomb_type = PieceType.Bombe if hasattr(PieceType, "Bombe") else SimpleNamespace()
        winner = self.make_piece("winner_bomb", ptype=bomb_type)
        defender = self.make_piece("defender")
        tile = SimpleNamespace(piece=defender, y=1, x=1)

        losers = [defender]
        # Call method under test
        self.gm.set_boards_post_combat(winner, losers, tile)

        # Because winner.type == Bombe, move_post_combat must NOT be called
        self.assertEqual(self.p1.known_board.moved, [], "p1.known_board should not have move_post_combat called for bomb winner")
        self.assertEqual(self.p2.known_board.moved, [], "p2.known_board should not have move_post_combat called for bomb winner")
        self.assertEqual(self.gm.board.moved, [], "main board should not have move_post_combat called for bomb winner")

        # Instead, losers should be removed from players and main board
        self.assertIn(defender, self.p1.removed_pieces)
        self.assertIn(defender, self.p2.removed_pieces)
        self.assertIn(defender, self.p1.known_board.removed)


if __name__ == '__main__':
    import unittest
    unittest.main()