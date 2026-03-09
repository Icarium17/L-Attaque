import mysql

class Connexion():
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="lattaque_user",
            password="stratego",
            database="lattaque"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        self.conn.commit()

    def queries(self, sql, params = None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.conn.close()

        