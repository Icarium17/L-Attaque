import bcrypt
import secrets

from DAO.DAOConnection import Connection

class DAOUsers():
    """
    Data-access helpers for user accounts, authentication, and score updates.
    """
    def create_user(self, username, password, preferred_language, id_avatar, rights, animation, contrast):
        """
        Create a new user account when the username is still available.

        Args:
            username: Requested username.
            password: Plaintext password to hash before storage.
            preferred_language: Initial language preference.
            id_avatar: Selected avatar identifier.
            rights: Initial permission level.
            animation: Animation preference flag.
            contrast: Contrast preference flag.

        Returns:
            tuple: Success payload with new user id and session key, or an error code.
        """
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
        """
        Authenticate a user by username and password.

        Args:
            username: Username to look up.
            password: Plaintext password to verify.

        Returns:
            tuple: Success payload with user id, session key, and score, or a failure marker.
        """
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

    def delete_user(self, user_id):
        """
        Delete one user account by identifier.

        Args:
            user_id: Database id of the user to delete.

        Returns:
            bool: True when the delete succeeded, otherwise False.
        """
        with Connection() as db:
            return db.execute("DELETE FROM users WHERE _id = %s", (user_id,))
        
    def update_score(self, user_id, new_score, win):
        """
        Update a user's score and win/loss counters after a game.

        Args:
            user_id: Database id of the user to update.
            new_score: New rating or score value.
            win: Whether the game result was a win.

        Returns:
            bool: True when the update succeeded, otherwise False.
        """
        with Connection() as db:
            return db.execute("""
                UPDATE users
                SET score = %s,
                    games_won = games_won + CASE WHEN %s THEN 1 ELSE 0 END,
                    games_lost = games_lost + CASE WHEN %s THEN 0 ELSE 1 END
                WHERE _id = %s
            """, (new_score, win, win, user_id))
        