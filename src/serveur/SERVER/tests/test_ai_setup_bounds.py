import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from USERS.aiPlayer import AIPlayer
from USERS.user import User


class TestAISetupBounds(unittest.TestCase):
    def test_bomb_side_never_creates_out_of_bounds_positions(self):
        user = User(0, "aaa", "AI_1", 0)
        ai = AIPlayer(user, 0, 1)

        for _ in range(200):
            ai.exclude_types.clear()
            pieces = ai.setup_library.setup_builder.bomb_side()

            self.assertTrue(pieces)
            for piece in pieces:
                x, y = piece.position
                self.assertGreaterEqual(x, 0)
                self.assertLess(x, 10)
                self.assertGreaterEqual(y, ai.rows[ai.order][0])
                self.assertLess(y, ai.rows[ai.order][1])


if __name__ == "__main__":
    unittest.main()