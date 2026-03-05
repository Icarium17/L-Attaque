from user import User

class Player(User):
    def __init__(self, order):
        super()
        self.order = order