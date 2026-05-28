from DAO.DAOConnection import Connection

class DAOStats():
    """
    Data-access helpers for leaderboard and account statistics queries.
    """
    def get_all_users(self):
        """
        Fetch basic identity and rights information for all users.

        Returns:
            list: User rows containing id, username, and rights.
        """
        with Connection() as db:
            return db.fetch("SELECT _id, username, rights FROM users WHERE username != 'MCTS_AI' AND username != 'admin'")
        
    def get_high_scores(self, limit = 10):
        """
        Fetch the top-ranked non-AI users ordered by score.

        Args:
            limit: Maximum number of leaderboard rows to return.

        Returns:
            dict: Leaderboard entries keyed by username.
        """
        with Connection() as db:
            rows = db.fetch("SELECT username, score, games_won, games_lost FROM users WHERE username != 'MCTS_AI' AND username != 'admin' ORDER BY score DESC LIMIT %s",(limit,))
            return {
                row["username"]: {
                    "username" : row["username"],
                    "score": row["score"],
                    "games_won": row["games_won"],
                    "games_lost": row["games_lost"],
                }
                for row in rows
            }