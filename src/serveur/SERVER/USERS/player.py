from USERS.user import User
from GAME.board import Board
from GAME.piece import BeliefPiece, PieceType

class Player(User):
    def __init__(self, user_instance, order, time_remaining = (60*15)):
        self.__dict__ = user_instance.__dict__.copy()
        self.user = user_instance
        self.order = order
        self.known_board = None
        self.time_remaining = time_remaining
        self.pieces_left = {}
        self.opponent_belief_pieces_left = {}
        self.pieces = {} 
        self.belief_pieces = None
        self.score = 0

        self.initialize_piece_left()

    def initialize_piece_left(self):
        for piece in PieceType:
            self.pieces_left[piece] = piece.count
            self.opponent_belief_pieces_left[piece] = piece.count
    
    def move(self, move):
        self.known_board.move(move)

    def remove_piece(self, piece):
        # Remove from pieces dict if present
        if piece and piece.id in self.pieces:
            del self.pieces[piece.id]

        
    def position_pieces(self, pieces):
        self.known_board.set_pieces(pieces)

    def update_belief_state_loser(self, piece_to_remove):
        if piece_to_remove.owner != self:
            piece_to_remove_type = piece_to_remove.type
            self.opponent_belief_pieces_left[piece_to_remove_type] -= 1
            for piece in self.belief_pieces:
                if isinstance(piece, BeliefPiece):
                    piece.update_probabilities(self.opponent_belief_pieces_left)

    def update_belief_state_winner(self, winner):
        if winner.owner != self:
            self.belief_pieces[winner.id] = winner
            self.opponent_belief_pieces_left[winner.type] -= 1


    


    
