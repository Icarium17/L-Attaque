class User():
    def __init__(self, account_id, key, username, score, status = "IDLE"):
        self.account_id = account_id
        self.key = key
        self.username = username
        self.score = score
        self.status = status