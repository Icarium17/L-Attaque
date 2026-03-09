from connexion import Connexion

class ConnexionUsers():
    def create_user(self, username, hashed_password, preferred_language, id_avatar, rights, animation, contrast):
        
        
        hashed_password = hashed_password.decode('utf-8')

        query = "INSERT INTO users (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast) VALUES (%s, %s, %s, %s, %s, %s, %s)", (username, hashed_password, preferred_language, id_avatar, rights, animation, contrast)
        