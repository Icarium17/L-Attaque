from USERS.user import User
from GAME.board import Board
from GAME.piece import PieceType

class Player(User):
    def __init__(self, user_instance, order, time_remaining = (60*15)):
        self.__dict__ = user_instance.__dict__.copy()
        self.user = user_instance
        self.order = order
        self.known_board = None
        self.time_remaining = time_remaining
        self.pieces_left = {}
        self.pieces = {}
        self.belief_pieces = None
        self.score = 0

        self.initialize_piece_left()

    def initialize_piece_left(self):
        for piece in PieceType:
            self.pieces_left[piece] = piece.count
    
    def move(self, move):
        self.known_board.move(move)

    def position_pieces(self, pieces):
        self.known_board.set_pieces(pieces)

    def update_belief_states(self, piece_to_remove):
        if piece_to_remove.owner != self:
            piece_to_remove_type = piece_to_remove.type
            self.pieces_left[piece_to_remove_type] -= 1
            for belief_piece in self.belief_pieces:
                belief_piece.update_probabilities(self.pieces_left)


    


    
