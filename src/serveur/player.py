from user import User

class Player(User):
    def __init__(self, user_instance, order):
        self.__dict__ = user_instance.__dict__.copy()
        self.order = order
        self.known_board = None

    def move(self, move):
        self.known_board.move(move)
