from DAO.DAOConnection import Connection

class DAOStats():
    def get_all_users(self):
        with Connection() as db:
            return db.fetch("SELECT _id, username, rights FROM users")
        
    def get_high_scores(self, limit = 10):
        with Connection() as db:
            rows = db.fetch("SELECT username, score, games_won, games_lost FROM users WHERE username != 'MCTS_AI' ORDER BY score DESC LIMIT %s", (limit,))
            return {
                row["username"]: {
                    "username" : row["username"],
                    "score": row["score"],
                    "games_won": row["games_won"],
                    "games_lost": row["games_lost"],
                }
                for row in rows
            }