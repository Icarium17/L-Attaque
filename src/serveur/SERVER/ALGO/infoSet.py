import copy
import random
from GAME.piece import BeliefPiece, Piece

class InfoSet:
    """
    Represents the information set for a player, including board state, player turn, and game rules.
    Provides methods for move generation, simulation, and belief piece handling.
    """
    def __init__(self, board_state, player_turn, game_rules):
        """
        Initialize an InfoSet.
        Args:
            board_state: The current board state.
            player_turn: The player whose turn it is.
            game_rules: The game rules object.
        """
        self.board_state = board_state
        self.player_turn = player_turn
        self.game_rules = game_rules

    def get_all_possible_moves(self):
        """
        Get all possible moves for the current player.
        
        Returns:
            list: List of possible moves for the current player.
        """
        pieces = self.board_state.get_pieces(self.player_turn)
        possible_moves = self.game_rules.get_remaining_moves(pieces, self.player_turn, self.board_state)
        return possible_moves

    def simulate_move(self, move):
        """
        Simulate a move and return the resulting board state if valid, else None.
        
        Args:
            move: The move to simulate.
        
        Returns:
            Board or None: The new board state if the move is valid, else None.
        """
        valid = self.validate_move(move)
        if not valid:
            return None
        new_board_state = copy.deepcopy(self.board_state)
        new_board_state.move(move)
        return new_board_state

    def validate_move(self, move):
        """
        Validate a move for the current player and board state.
        
        Args:
            move: The move to validate.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        valid, _ = self.game_rules.validate_move(self.player_turn, move, self.board_state)
        return valid

    def new_infoSet(self, move):
        """
        Return a new InfoSet after applying a move, or None if move is invalid.
        
        Args:
            move: The move to apply.
        
        Returns:
            InfoSet or None: The new InfoSet if the move is valid, else None.
        """
        new_board_state = self.simulate_move(move)
        if new_board_state is None:
            return None
        return InfoSet(new_board_state, 1 - self.player_turn, self.game_rules)

    def update_infoSet(self, move):
        """
        Update the current InfoSet in place by applying a move, if valid.
        
        Args:
            move: The move to apply.
        
        Returns:
            None if move is invalid, otherwise updates in place.
        """
        valid = self.validate_move(move)
        if not valid:
            return None
        self.board_state.move(move)
        self.player_turn = 1 - self.player_turn

    def actualize_belief_pieces(self, pieces_left):
        """
        Convert all BeliefPieces on the board to Pieces for one iteration of the algorithm.
        Uses backtracking to assign types to belief pieces based on remaining pieces.
        
        Args:
            pieces_left: Dictionary of remaining piece types to assign.
        """
        belief_pieces = []
        for row in self.board_state.tiles:
            for tile in row:
                if tile.piece is not None and isinstance(tile.piece, BeliefPiece):
                    belief_pieces.append(tile.piece)

        possible_setup = self.assign_types_backtracking(belief_pieces, pieces_left)

        if possible_setup is not None:
            for belief_piece, type in zip(belief_pieces, possible_setup):
                piece = Piece(belief_piece.id, type, belief_piece.position, belief_piece.owner)
                self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece

    def assign_types_backtracking(self, belief_pieces, pieces_left, i=0, assignment=None):
        """
        Recursively assign types to belief pieces using backtracking and probability weights.
        
        Args:
            belief_pieces: List of BeliefPiece objects to assign types to.
            pieces_left: Dictionary of remaining piece types to assign.
            i: Current index in belief_pieces (default 0).
            assignment: Current assignment list (default None).
        
        Returns:
            list or None: List of assigned types if successful, else None.
        """
        if assignment is None:
            assignment = []
        if i == len(belief_pieces):
            return assignment  # Success

        bp = belief_pieces[i]
        possible_types = [t for t in bp.probabilities if bp.probabilities[t] > 0 and pieces_left[t] > 0]
        if not possible_types:
            return None

        weights = [bp.probabilities[t] for t in possible_types]
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        else:
            weights = [1 / len(possible_types)] * len(possible_types)

        sampled_types = random.choices(possible_types, weights=weights, k=len(possible_types))

        seen = set()
        sampled_types = [x for x in sampled_types if not (x in seen or seen.add(x))]

        for t in sampled_types:
            pieces_left[t] -= 1
            result = self.assign_types_backtracking(belief_pieces, pieces_left, i+1, assignment + [t])
            pieces_left[t] += 1  # Backtrack
            if result is not None:
                return result

        return None


        