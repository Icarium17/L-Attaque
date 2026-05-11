from DAO.DAOConnection import Connection
import bcrypt
import secrets

class DAOUsers():
    def create_user(self, username, password, preferred_language, id_avatar, rights, animation, contrast):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        with Connection() as db:
            # Check if username already exists
            existing_user = db.fetch("SELECT * FROM users WHERE username=%s", (username,))
            if existing_user:
                return False, "USERNAME_ALREADY_EXISTS"  # Username already exists

            sql = """
            INSERT INTO users (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            params = (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast)

            if db.execute(sql, params):
                user_id = db.cursor.lastrowid
                session_key = secrets.token_hex(32)
                return True, user_id, session_key, "ACCOUNT_CREATED"
            return False, "ERROR"

    def connect(self, username, password):
        with Connection() as db:
            user = db.fetch("SELECT * FROM users WHERE username=%s", (username,))

            if not user:
                return False, 0

            stored_hash = user[0]["hashed_password"].encode()
            score = user[0]["score"]
            user_id = user[0]["_id"]
            if bcrypt.checkpw(password.encode(), stored_hash):
                session_key = secrets.token_hex(32)  # Generates a random session key
                return True, user_id, session_key, score

            return False, 0
        
        
    def get_all_users(self):
        with Connection() as db:
            return db.fetch("SELECT _id, username, rights FROM users")

    def delete_user(self, user_id):
        with Connection() as db:
            return db.execute("DELETE FROM users WHERE _id = %s", (user_id,))
        
    def update_score(self, user_id, new_score, win):
        with Connection() as db:
            return db.execute("""
                UPDATE users
                SET score = %s,
                    games_won = games_won + CASE WHEN %s THEN 1 ELSE 0 END,
                    games_lost = games_lost + CASE WHEN %s THEN 0 ELSE 1 END
                WHERE _id = %s
            """, (new_score, win, win, user_id))
        

        
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