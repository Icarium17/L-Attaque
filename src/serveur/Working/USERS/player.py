from user import User
from GAME.board import board

class Player(User):
    def __init__(self, user_instance, order, time_remaining = (30*60)):
        self.__dict__ = user_instance.__dict__.copy()
        self.order = order
        self.known_board = None
        self.time_remaining = time_remaining

    def move(self, move):
        self.known_board.move(move)

    def position_pieces(self, pieces):
        self.board.set_pieces(pieces)

    def initialize_game(self):
        pass

    def turn(self):
        pass

    def update_belief_state(self):
        pass

    