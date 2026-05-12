from USERS.user import User
from GAME.piece import BeliefPiece, Piece, PieceType

class Player(User):
    """
    Represents a player during a game, including owned pieces and knowledge about the opponent.

    This class tracks the player's own remaining pieces, cached flag position, and the imperfect
    information view of opponent pieces through hidden belief pieces and revealed opponent pieces.
    """
    def __init__(self, user_instance, order, time_remaining = (60*20)):
        """
        Initialize a Player from an existing user instance.

        Args:
            user_instance: The base user object whose data should be copied.
            order: The player's order in the game.
            time_remaining: Remaining time on the player's clock.
        """
        self.__dict__ = user_instance.__dict__.copy()
        self.user = user_instance
        self.order = int(order)
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
        self.last_move = None

    def load(self, known_pieces, time_remaining, last_move):
        self.set_pieces(known_pieces)
        self.time_remaining = time_remaining
        self.last_move = last_move
        self.populate_all_known_pieces(known_pieces)

    
    def populate_all_known_pieces(self, known_pieces):
        """
        Populate self.pieces, self.belief_pieces, and self.opponent_pieces from a list of all known pieces after a save.

        Args:
            known_pieces: Iterable of all known pieces (owned, opponent belief, revealed opponent pieces).

        Returns:
            None
        """
        self.pieces = {}
        self.belief_pieces = {}
        self.opponent_pieces = {}
        self.opponent_belief_pieces_left = {piece_type: piece_type.count for piece_type in PieceType}

        for piece in known_pieces:
            # Owned pieces
            if hasattr(piece, 'owner') and piece.owner == self.order:
                self.pieces[piece.id] = piece
            elif isinstance(piece, BeliefPiece):
                self.belief_pieces[piece.id] = piece
                if hasattr(piece, 'type') and piece.type is not None:
                    self.opponent_belief_pieces_left[piece.type] -= 1
            elif hasattr(piece, 'owner') and piece.owner != self.order:
                self.opponent_pieces[piece.id] = piece

        self.rebuild_piece_counts()
        


    @property
    def pieces_left(self):
        """
        Get the cached counts of the player's remaining own pieces.

        Returns:
            dict: Mapping from `PieceType` to remaining count.
        """
        return self.end_state_cache["piece_counts"]

    @pieces_left.setter
    def pieces_left(self, value):
        """
        Set the cached counts of the player's remaining own pieces.

        Args:
            value: Mapping from `PieceType` to remaining count.
        """
        self.end_state_cache["piece_counts"] = value

    @property
    def flag_position(self):
        """
        Get the cached position of the player's flag.

        Returns:
            tuple | None: The flag position if known, otherwise `None`.
        """
        return self.end_state_cache["flag_position"]

    @flag_position.setter
    def flag_position(self, value):
        """
        Set the cached position of the player's flag.

        Args:
            value: The new flag position or `None`.
        """
        self.end_state_cache["flag_position"] = value


    def initialize_piece_left(self):
        """
        Initialize piece-count dictionaries for both owned and opponent belief pieces.

        Returns:
            None
        """
        for piece in PieceType:
            self.pieces_left[piece] = piece.count
            self.opponent_belief_pieces_left[piece] = piece.count

    def rebuild_piece_counts(self):
        """
        Rebuild the cached counts of owned pieces from the current `pieces` dictionary.

        Returns:
            None
        """
        self.flag_position = None
        for piece_type in PieceType:
            self.pieces_left[piece_type] = 0

        for piece in self.pieces.values():
            if piece.type is not None:
                self.pieces_left[piece.type] += 1
                if piece.type == PieceType.Drapeau:
                    self.flag_position = piece.position

    def sync_owned_pieces(self):
        """
        Synchronize the player's owned pieces from the known board and rebuild piece counts.

        Returns:
            None
        """
        self.pieces = self.known_board.get_pieces(self.order)
        self.rebuild_piece_counts()

    def remove_owned_piece(self, piece_id):
        """
        Remove one of the player's own pieces and update cached piece counts.

        Args:
            piece_id: Identifier of the piece to remove.

        Returns:
            None
        """
        piece = self.pieces.pop(piece_id, None)
        if piece is not None:
            self.rebuild_piece_counts()

    def add_belief_pieces(self, pieces):
        """
        Add hidden opponent belief pieces to the player's knowledge state.

        Args:
            pieces: Iterable of `BeliefPiece` objects to add.

        Returns:
            None
        """
        self.belief_pieces.update({piece.id: piece for piece in pieces})

    def update_belief_piece(self, piece):
        """
        Update or insert a single hidden opponent belief piece.

        Args:
            piece: The `BeliefPiece` to store.

        Returns:
            None
        """
        self.belief_pieces[piece.id] = piece

    def remove_belief_piece(self, piece_id, type):
        """
        Remove a hidden opponent belief piece and decrement the corresponding remaining count.

        Args:
            piece_id: Identifier of the belief piece to remove.
            type: The concrete `PieceType` that has been revealed or eliminated.

        Returns:
            BeliefPiece | None: The removed belief piece if present, otherwise `None`.
        """
        self.decrement_opponent_belief_piece_left(type)
        return self.belief_pieces.pop(piece_id, None)

    def add_revealed_opponent_piece(self, piece):
        """
        Add a revealed opponent piece to the player's known opponent pieces.

        Args:
            piece: The revealed `Piece` to store.

        Returns:
            None
        """
        self.opponent_pieces[piece.id] = piece

    def remove_revealed_opponent_piece(self, piece_id):
        """
        Remove a revealed opponent piece from the player's known opponent pieces.

        Args:
            piece_id: Identifier of the revealed piece to remove.

        Returns:
            Piece | None: The removed piece if present, otherwise `None`.
        """
        return self.opponent_pieces.pop(piece_id, None)

    def get_hidden_belief_pieces(self):
        """
        Get all currently hidden opponent belief pieces.

        Returns:
            list: List of hidden opponent belief pieces.
        """
        return list(self.belief_pieces.values())

    def get_revealed_opponent_pieces(self):
        """
        Get all currently revealed opponent pieces.

        Returns:
            list: List of revealed opponent pieces.
        """
        return list(self.opponent_pieces.values())

    def get_all_known_opponent_pieces(self):
        """
        Get all opponent pieces known to the player, hidden and revealed.

        Returns:
            dict: Mapping from piece id to known opponent piece object.
        """
        known_opponent_pieces = {piece.id: piece for piece in self.belief_pieces.values()}
        known_opponent_pieces.update(self.opponent_pieces)
        return known_opponent_pieces

    def decrement_opponent_belief_piece_left(self, piece_type):
        """
        Decrement the remaining count for a specific opponent piece type.

        Args:
            piece_type: The opponent `PieceType` whose count should be decremented.

        Returns:
            None
        """
        if piece_type is not None:
            self.opponent_belief_pieces_left[piece_type] -= 1
    
    def move(self, move):
        """
        Apply a move on the player's known board.

        Args:
            move: The move to apply.

        Returns:
            None
        """
        self.known_board.move(move)

    def remove_piece(self, piece):
        """
        Remove one of the player's own pieces if it belongs to this player.

        Args:
            piece: The piece to remove.

        Returns:
            None
        """
        if piece and piece.id in self.pieces:
            self.remove_owned_piece(piece.id)

    def remove_piece_everywhere(self, piece, piece_type=None):
            """
            Remove a piece from all possible collections: own pieces, belief pieces, and revealed opponent pieces.
            Args:
                piece: The piece object to remove.
                piece_type: The type of the piece (required for belief piece removal, if not provided will use piece.type if available).
            Returns:
                None
            """
            # Remove from own pieces
            self.remove_piece(piece)
            # Remove from belief pieces
            if piece_type is None and hasattr(piece, 'type'):
                piece_type = piece.type
            if piece.id in self.belief_pieces:
                self.remove_belief_piece(piece.id, piece_type)
            # Remove from revealed opponent pieces
            if piece.id in self.opponent_pieces:
                self.remove_revealed_opponent_piece(piece.id)
    
    def change_belief_piece_to_piece(self, old_piece, piece_type, owner=None):
        """
        Convert a hidden belief piece into a concrete revealed piece.

        Args:
            old_piece: The belief piece to convert.
            piece_type: The revealed `PieceType`.
            owner: Optional owner override for the new concrete piece.

        Returns:
            Piece | None: The converted concrete piece, or `None` if conversion is not possible.
        """
        if isinstance(old_piece, BeliefPiece):
            x, y = old_piece.position
            new_piece = old_piece.upgrade(piece_type)

            if self.known_board is not None:
                self.known_board.tiles[y][x].piece = new_piece

            return new_piece

    def refresh_hidden_belief_probabilities(self):
        """
        Refresh probability distributions for all remaining hidden belief pieces.

        Returns:
            None
        """
        while True:
            upgraded_piece = False

            for piece in list(self.get_hidden_belief_pieces()):
                if not isinstance(piece, BeliefPiece):
                    continue

                piece.update_probabilities(self.opponent_belief_pieces_left)

                if self.upgrade_belief_piece_if_certain(piece) is not None:
                    upgraded_piece = True
                    break

            if not upgraded_piece:
                return

    def upgrade_belief_piece_if_certain(self, piece):
        """
        Convert a hidden belief piece into a revealed piece when its type is certain.

        Args:
            piece: The `BeliefPiece` to potentially upgrade.

        Returns:
            Piece | None: The revealed piece if an upgrade occurred, otherwise `None`.
        """
        if not isinstance(piece, BeliefPiece):
            return None

        upgraded_piece = piece.check_upgrade_bp_to_piece()
        if upgraded_piece is None:
            return None

        old_piece = self.remove_belief_piece(piece.id, upgraded_piece.type)
        new_piece = self.change_belief_piece_to_piece(old_piece, upgraded_piece.type, upgraded_piece.owner)

        if new_piece is not None:
            self.add_revealed_opponent_piece(new_piece)

        return new_piece
        
    def position_pieces(self, pieces):
        """
        Place a collection of pieces on the player's known board.

        Args:
            pieces: Iterable of pieces to place.

        Returns:
            None
        """
        self.known_board.set_pieces(pieces)

    def update_belief_state_move(self, x, y, distance):
        """
        Update belief-state probabilities after an observed opponent move.

        Args:
            x: Source x-coordinate of the move.
            y: Source y-coordinate of the move.
            distance: Distance traveled by the piece.

        Returns:
            None
        """
        piece = self.known_board.tiles[y][x].piece
        if not isinstance(piece, BeliefPiece):
            return

        piece.update_probabilities_on_move(distance)
        piece.update_probabilities(self.opponent_belief_pieces_left)
        if self.upgrade_belief_piece_if_certain(piece) is None:
            self.update_belief_piece(piece)
        else:
            self.refresh_hidden_belief_probabilities()


    def update_belief_state_loser(self, loser):
        """
        Update opponent knowledge after an opponent piece loses a combat.

        Args:
            loser: The losing piece from the combat.

        Returns:
            None
        """
        if loser.owner != self.order:
            piece_to_remove_type = loser.type
            known_piece = self.remove_belief_piece(loser.id, piece_to_remove_type)

            if isinstance(known_piece, BeliefPiece):
                self.refresh_hidden_belief_probabilities()
            else:
                self.remove_revealed_opponent_piece(loser.id)

    def update_belief_state_winner(self, winner):
        """
        Update opponent knowledge after an opponent piece wins a combat and is revealed.

        Args:
            winner: The winning piece from the combat.

        Returns:
            None
        """
        if winner.owner != self.order:
            piece_to_remove_type = winner.type
            old_piece = self.belief_pieces.get(winner.id)

            if isinstance(old_piece, BeliefPiece):
                old_piece = self.remove_belief_piece(winner.id, piece_to_remove_type)
                new_piece = self.change_belief_piece_to_piece(old_piece, winner.type, winner.owner)
                if new_piece:
                    self.add_revealed_opponent_piece(new_piece)
                    self.refresh_hidden_belief_probabilities()
            else:
                if self.known_board is not None:
                    x, y = winner.position
                    board_piece = self.known_board.tiles[y][x].piece
                    self.add_revealed_opponent_piece(board_piece if board_piece is not None else winner)
                else:
                    self.add_revealed_opponent_piece(winner)





    


    
