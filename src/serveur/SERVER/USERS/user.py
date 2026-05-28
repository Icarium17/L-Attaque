class User():
    """
    Represent one connected or persisted user account.
    """
    def __init__(self, account_id, key, username, score, status = "IDLE"):
        """
        Initialize a user with account identity and session state.

        Args:
            account_id: Persistent database identifier.
            key: Session key associated with the user.
            username: Display name.
            score: Current score value.
            status: Current lobby or game status.
        """
        self.account_id = account_id
        self.key = key
        self.username = username
        self.score = score
        self.status = status