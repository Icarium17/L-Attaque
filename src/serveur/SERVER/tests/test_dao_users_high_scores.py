import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DAO.DAOUsers import DAOUsers

class TestDAOUsersHighScores(unittest.TestCase):
    @patch('DAO.DAOUsers.Connection')
    def test_update_score_and_high_scores(self, mock_connection):
        # Setup initial scores and user ids
        user_ids = {
            'ericlabonte': 1,
            'eddy': 2,
            'po': 3,
            'Charleee': 4,
        }
        # Mock the database connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        # Simulate score update calls
        def execute_side_effect(sql, params=None):
            # Simulate updating scores in a local dict
            if sql.startswith("UPDATE users SET score = score +"):
                for name, uid in user_ids.items():
                    if params[1] == uid:
                        scores[name] += params[0]
                return mock_cursor
            elif sql.startswith("SELECT username, score FROM users"):
                # Return the scores sorted as the real query would
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                return MagicMock(fetchall=MagicMock(return_value=[{'username': name, 'score': score} for name, score in sorted_scores]))
            return mock_cursor

        # Initial scores
        scores = {
            'ericlabonte': 100,
            'eddy': 50,
            'po': 30,
            'Charleee': 10,
            'user1': 0,
            'user2': 0,
        }
        mock_db.execute.side_effect = execute_side_effect
        mock_connection.return_value.__enter__.return_value = mock_db

        dao = DAOUsers()
        # Add points to users
        dao.update_score(user_ids['eddy'], 25)        # eddy: 50 -> 75
        dao.update_score(user_ids['Charleee'], 50)    # Charleee: 10 -> 60
        dao.update_score(user_ids['po'], 40)          # po: 30 -> 70
        dao.update_score(user_ids['ericlabonte'], 5)  # ericlabonte: 100 -> 105

        # Now check high scores
        high_scores = dao.get_high_scores(limit=6)
        self.assertEqual(high_scores[0]['username'], 'ericlabonte')
        self.assertEqual(high_scores[0]['score'], 105)
        self.assertEqual(high_scores[1]['username'], 'eddy')
        self.assertEqual(high_scores[1]['score'], 75)
        self.assertEqual(high_scores[2]['username'], 'po')
        self.assertEqual(high_scores[2]['score'], 70)
        self.assertEqual(high_scores[3]['username'], 'Charleee')
        self.assertEqual(high_scores[3]['score'], 60)
        self.assertEqual(high_scores[4]['score'], 0)
        self.assertEqual(high_scores[5]['score'], 0)
            
    @patch('DAO.DAOUsers.Connection')
    def test_get_high_scores(self, mock_connection):
        # Mock the database cursor and its fetchall method
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        # The order should be: ericlabonte (100), eddy (50), po (30), Charleee (10), then others with 0
        mock_cursor.fetchall.return_value = [
            {'username': 'ericlabonte', 'score': 100},
            {'username': 'eddy', 'score': 50},
            {'username': 'po', 'score': 30},
            {'username': 'Charleee', 'score': 10},
            {'username': 'user1', 'score': 0},
            {'username': 'user2', 'score': 0},
        ]
        mock_db.execute.return_value = mock_cursor
        mock_connection.return_value.__enter__.return_value = mock_db

        dao = DAOUsers()
        scores = dao.get_high_scores(limit=6)
        self.assertEqual(scores[0]['username'], 'ericlabonte')
        self.assertEqual(scores[0]['score'], 100)
        self.assertEqual(scores[1]['username'], 'eddy')
        self.assertEqual(scores[1]['score'], 50)
        self.assertEqual(scores[2]['username'], 'po')
        self.assertEqual(scores[2]['score'], 30)
        self.assertEqual(scores[3]['username'], 'Charleee')
        self.assertEqual(scores[3]['score'], 10)
        self.assertEqual(scores[4]['score'], 0)
        self.assertEqual(scores[5]['score'], 0)

if __name__ == '__main__':
    unittest.main()
