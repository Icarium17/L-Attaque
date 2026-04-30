import unittest
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'SERVER'))
sys.path.insert(0, os.path.join(BASE_DIR, 'DAO'))
sys.path.insert(0, os.path.join(BASE_DIR, 'USERS'))
sys.path.insert(0, os.path.join(BASE_DIR, 'GAME'))
from SERVER.lobbyManager import LobbyManager
from USERS.user import User

class TestLobbyManager(unittest.TestCase):
    def setUp(self):
        self.lobby = LobbyManager()
        # Create two mock users
        self.user1 = User(1, "KEY1", "User1", 0, "IDLE")
        self.user2 = User(2, "KEY2", "User2", 0, "IDLE")
        self.lobby.active_users["KEY1"] = self.user1
        self.lobby.active_users["KEY2"] = self.user2

    def test_start_game_multiplayer_waitlist_empty(self):
        # Waitlist is empty, user1 tries to start multiplayer
        result, opponent = self.lobby.start_game(("KEY1", "multiplayer"))
        self.assertEqual(result, "WAITING_FOR_OPPONENT")
        self.assertEqual(opponent, "")  # Now returns empty string, not None
        self.assertIn("KEY1", self.lobby.wait_list)
        # A pending game should be created for KEY1 with only one player
        self.assertIn("KEY1", self.lobby.games)
        game = self.lobby.games["KEY1"]
        self.assertEqual(len(game.players), 1)
        self.assertEqual(game.status, "WAITING")

    def test_start_game_multiplayer_waitlist_has_user(self):
        # Add user1 to waitlist, user2 tries to start multiplayer
        self.lobby.wait_list.append("KEY1")
        result, opponent = self.lobby.start_game(("KEY2", "multiplayer"))
        self.assertEqual(result, "GAME_STARTED")
        self.assertEqual(opponent, "User2")
        self.assertNotIn("KEY1", self.lobby.wait_list)
        self.assertNotIn("KEY2", self.lobby.wait_list)
        # Game should be created for both users
        self.assertIn("KEY1", self.lobby.games)
        self.assertIn("KEY2", self.lobby.games)
        game = self.lobby.games["KEY1"]
        self.assertIs(game, self.lobby.games["KEY2"])
        self.assertEqual(len(game.players), 2)
        self.assertEqual(game.status, "PLAYING")

if __name__ == "__main__":
    unittest.main()
