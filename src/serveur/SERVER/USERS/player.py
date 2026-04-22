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
        
        self.end_state_cache = {
            "piece_counts": {},
            "flag_position": None,
        }
        self.pieces = {} 
        
        self.opponent_belief_pieces_left = {}
        self.belief_pieces = {}
        self.opponent_pieces = {}
        self.initialize_piece_left()

        self.score = 0

    @property
    def pieces_left(self):
        return self.end_state_cache["piece_counts"]

    @pieces_left.setter
    def pieces_left(self, value):
        self.end_state_cache["piece_counts"] = value

    @property
    def flag_position(self):
        return self.end_state_cache["flag_position"]

    @flag_position.setter
    def flag_position(self, value):
        self.end_state_cache["flag_position"] = value


    def initialize_piece_left(self):
        for piece in PieceType:
            self.pieces_left[piece] = piece.count
            self.opponent_belief_pieces_left[piece] = piece.count

    def rebuild_piece_counts(self):
        self.flag_position = None
        for piece_type in PieceType:
            self.pieces_left[piece_type] = 0

        for piece in self.pieces.values():
            if piece.type is not None:
                self.pieces_left[piece.type] += 1
                if piece.type == PieceType.Drapeau:
                    self.flag_position = piece.position

    def sync_owned_pieces(self):
        self.pieces = self.known_board.get_pieces(self.order)
        self.rebuild_piece_counts()

    def remove_owned_piece(self, piece_id):
        piece = self.pieces.pop(piece_id, None)
        if piece is not None and piece.type is not None and self.pieces_left[piece.type] > 0:
            self.pieces_left[piece.type] -= 1
            if piece.type == PieceType.Drapeau:
                self.flag_position = None

    def add_belief_pieces(self, pieces):
        self.belief_pieces.update({piece.id: piece for piece in pieces})

    def update_belief_piece(self, piece):
        self.belief_pieces[piece.id] = piece

    def remove_belief_piece(self, piece_id):
        return self.belief_pieces.pop(piece_id, None)

    def add_revealed_opponent_piece(self, piece):
        self.opponent_pieces[piece.id] = piece

    def remove_revealed_opponent_piece(self, piece_id):
        return self.opponent_pieces.pop(piece_id, None)

    def get_hidden_belief_pieces(self):
        return list(self.belief_pieces.values())

    def get_revealed_opponent_pieces(self):
        return list(self.opponent_pieces.values())

    def get_all_known_opponent_pieces(self):
        known_opponent_pieces = {piece.id: piece for piece in self.belief_pieces.values()}
        known_opponent_pieces.update(self.opponent_pieces)
        return known_opponent_pieces

    def decrement_opponent_piece_left(self, piece_type):
        if piece_type is not None:
            self.opponent_belief_pieces_left[piece_type] -= 1
    
    def move(self, move):
        self.known_board.move(move)

    def remove_piece(self, piece):
        if piece and piece.id in self.pieces:
            self.remove_owned_piece(piece.id)

        
    def position_pieces(self, pieces):
        self.known_board.set_pieces(pieces)

    def update_belief_state_move(self, x, y, distance):
        piece = self.known_board.tiles[y][x].piece
        if not isinstance(piece, BeliefPiece):
            return

        piece.update_probabilities_on_move(distance)
        self.update_belief_piece(piece)

    def update_belief_state_loser(self, piece_to_remove):
        if piece_to_remove.owner != self.order:
            known_piece = self.remove_belief_piece(piece_to_remove.id) ##This could be a problem if the piece is not in belief_piece but in opponent_pieces
            self.remove_revealed_opponent_piece(piece_to_remove.id)
            piece_to_remove_type = piece_to_remove.type

            self.decrement_opponent_piece_left(piece_to_remove_type)

            if isinstance(known_piece, BeliefPiece):
                for piece in self.get_hidden_belief_pieces():
                    if isinstance(piece, BeliefPiece):
                        piece.update_probabilities(self.opponent_belief_pieces_left)

    def update_belief_state_winner(self, winner):
        if winner.owner != self.order:
            self.remove_belief_piece(winner.id)
            known_piece = self.known_board.tiles[winner.position[1]][winner.position[0]].piece
            self.add_revealed_opponent_piece(known_piece)
            self.decrement_opponent_piece_left(winner.type)




    


    
