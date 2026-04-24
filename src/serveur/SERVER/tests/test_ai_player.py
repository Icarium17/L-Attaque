
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from USERS.aiPlayer import AIPlayer
from GAME.piece import PieceType

class DummyUser:
    pass

class TestAIPlayerBombPlacement(unittest.TestCase):
    def test_spread_out_bomb_clusters_preserves_positions(self):
        ai = AIPlayer(DummyUser(), order=0, difficulty=0)
        # Call the bomb cluster placement
        # Instead of relying on internal state, capture the pieces list directly
        pieces = []
        pieces = ai.spread_out_bomb_clusters()
        # Print all piece positions and types
        print("All pieces:")
        for p in pieces:
            print(f"Type: {getattr(p, 'type', None)}, Position: {getattr(p, 'position', None)}")
        bomb_positions = [p.position for p in pieces if getattr(p, 'type', None) == PieceType.Bombe]
        self.assertGreaterEqual(len(bomb_positions), 2)
        self.assertEqual(len(bomb_positions), len(set(bomb_positions)))

if __name__ == '__main__':
    unittest.main()
