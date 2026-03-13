import mysql

class Connexion:
    def __enter__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="lattaque_user",
            password="stratego",
            database="lattaque"
        )
        self.cursor = self.conn.cursor(dictionary=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True  
        except mysql.connector.Error as e:
            print("SQL error:", e)
            return False

    def fetch(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()