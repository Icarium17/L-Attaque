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
            return mock_cursor

        def fetch_side_effect(sql, params=None):
            if sql.startswith("SELECT username, score, games_won, games_lost FROM users"):
                sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
                limited_scores = sorted_scores[:params[0]]
                return [
                    {
                        'username': name,
                        'score': score,
                        'games_won': 0,
                        'games_lost': 0,
                    }
                    for name, score in limited_scores
                ]
            return []

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
        mock_db.fetch.side_effect = fetch_side_effect
        mock_connection.return_value.__enter__.return_value = mock_db

        dao = DAOUsers()
        # Add points to users
        dao.update_score(user_ids['eddy'], 25)        # eddy: 50 -> 75
        dao.update_score(user_ids['Charleee'], 50)    # Charleee: 10 -> 60
        dao.update_score(user_ids['po'], 40)          # po: 30 -> 70
        dao.update_score(user_ids['ericlabonte'], 5)  # ericlabonte: 100 -> 105

        # Now check high scores
        high_scores = dao.get_high_scores(limit=6)
        self.assertEqual(list(high_scores), ['ericlabonte', 'eddy', 'po', 'Charleee', 'user1', 'user2'])
        self.assertEqual(high_scores['ericlabonte']['score'], 105)
        self.assertEqual(high_scores['eddy']['score'], 75)
        self.assertEqual(high_scores['po']['score'], 70)
        self.assertEqual(high_scores['Charleee']['score'], 60)
        self.assertEqual(high_scores['user1']['score'], 0)
        self.assertEqual(high_scores['user2']['score'], 0)
            
    @patch('DAO.DAOUsers.Connection')
    def test_get_high_scores(self, mock_connection):
        # Mock the database cursor and its fetchall method
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        # The order should be: ericlabonte (100), eddy (50), po (30), Charleee (10), then others with 0
        mock_db.fetch.return_value = [
            {'username': 'ericlabonte', 'score': 100, 'games_won': 5, 'games_lost': 1},
            {'username': 'eddy', 'score': 50, 'games_won': 2, 'games_lost': 3},
            {'username': 'po', 'score': 30, 'games_won': 1, 'games_lost': 4},
            {'username': 'Charleee', 'score': 10, 'games_won': 0, 'games_lost': 2},
            {'username': 'user1', 'score': 0, 'games_won': 0, 'games_lost': 0},
            {'username': 'user2', 'score': 0, 'games_won': 0, 'games_lost': 0},
        ]
        mock_connection.return_value.__enter__.return_value = mock_db

        dao = DAOUsers()
        scores = dao.get_high_scores(limit=6)
        self.assertEqual(list(scores), ['ericlabonte', 'eddy', 'po', 'Charleee', 'user1', 'user2'])
        self.assertEqual(scores['ericlabonte']['score'], 100)
        self.assertEqual(scores['eddy']['score'], 50)
        self.assertEqual(scores['po']['score'], 30)
        self.assertEqual(scores['Charleee']['score'], 10)
        self.assertEqual(scores['user1']['score'], 0)
        self.assertEqual(scores['user2']['score'], 0)
        self.assertEqual(scores['ericlabonte']['games_won'], 5)
        self.assertEqual(scores['ericlabonte']['games_lost'], 1)

if __name__ == '__main__':
    unittest.main()
