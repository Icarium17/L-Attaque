from connexion import Connexion
import bcrypt
import secrets

class ConnexionUsers():
    def __init__(self):
        self.db = Connexion()
    
    def create_user(self, username, password, preferred_language, id_avatar, rights, animation, contrast):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        sql = """
        INSERT INTO users (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast)

        with Connexion() as db:
            return db.execute(sql, params)

    
    def connect(self, username, password):
        with Connexion() as db:
            user = db.fetch("SELECT * FROM users WHERE username=%s", (username,))

            if not user:
                return False

            stored_hash = user[0]["hashed_password"].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                session_key = secrets.token_hex(32)  # Generates a random session key
                return True, session_key
            
            return False
