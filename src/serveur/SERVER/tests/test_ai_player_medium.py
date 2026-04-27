import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from USERS.aiPlayer import AIPlayer
from GAME.piece import PieceType

class DummyUser:
    pass

class TestAIPlayerMediumSetup(unittest.TestCase):
    def test_generate_piece_list_medium_places_bombs_and_40_pieces(self):
        ai = AIPlayer(DummyUser(), order=0, difficulty=2)
        pieces = ai.setup_pieces()
        # Count bombs
        bomb_positions = [p.position for p in pieces if getattr(p, 'type', None) == PieceType.Bombe]
        print("All pieces:")
        for p in pieces:
            print(f"Type: {getattr(p, 'type', None)}, Position: {getattr(p, 'position', None)}")
        self.assertEqual(len(bomb_positions), 6)
        self.assertEqual(len(pieces), 40)
        # Ensure all bomb positions are unique
        self.assertEqual(len(bomb_positions), len(set(bomb_positions)))

if __name__ == '__main__':
    unittest.main()
