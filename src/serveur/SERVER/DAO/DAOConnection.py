import mysql.connector

class Connection():
    """
    Context manager wrapper around the MySQL connection used by DAO classes.
    """
    def __enter__(self):
        """
        Open a database connection and create a dictionary cursor.

        Returns:
            Connection: The active connection wrapper.
        """
        self.conn = mysql.connector.connect(
            host="localhost",
            user="lattaque_user",
            password="stratego",
            database="lattaque"
        )
        self.cursor = self.conn.cursor(dictionary=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the cursor and connection when leaving the context manager.

        Args:
            exc_type: Exception type raised inside the context, if any.
            exc_val: Exception instance raised inside the context, if any.
            exc_tb: Traceback associated with the exception, if any.

        Returns:
            None
        """
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, params=None):
        """
        Execute one write query and commit the transaction.

        Args:
            sql: SQL statement to execute.
            params: Optional query parameters.

        Returns:
            bool: True on success, False when the database reports an error.
        """
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            print("SQL error:", e)
            return False

    def fetch(self, sql, params=None):
        """
        Execute one read query and return all fetched rows.

        Args:
            sql: SQL statement to execute.
            params: Optional query parameters.

        Returns:
            list: Query results as dictionaries.
        """
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()
