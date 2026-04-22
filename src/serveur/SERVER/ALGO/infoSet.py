import copy
import random
import time
from GAME.piece import BeliefPiece, Piece


## Should only store observable states. the sampled board should be in the algo, not in the nodes.
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

    def sync_opponent_knowledge(self, hidden_belief_pieces, revealed_opponent_pieces):
        for piece in hidden_belief_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

        for piece in revealed_opponent_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

    def actualize_belief_pieces(self, hidden_belief_pieces, pieces_left):
        belief_piece_ids = {piece.id for piece in hidden_belief_pieces}
        belief_pieces = []
        for row in self.board_state.tiles:
            for tile in row:
                if (
                    tile.piece is not None
                    and isinstance(tile.piece, BeliefPiece)
                    and tile.piece.id in belief_piece_ids
                ):
                    belief_pieces.append(tile.piece)

        possible_setup = self.assign_types_backtracking(belief_pieces, pieces_left)

        if possible_setup is None:
            possible_setup = self.assign_types_random(belief_pieces, pieces_left)

        if possible_setup is not None:
            for belief_piece, type in zip(belief_pieces, possible_setup):
                piece = Piece(belief_piece.id, type, belief_piece.position, belief_piece.owner)
                self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece

        


    ## TODO : make this better. the algo shouldnt have to fall back on a random distribution if this function doesnt work so often
    def assign_types_backtracking(self, belief_pieces, pieces_left, i=0, assignment=None, do_sort=True, start_time=None, timeout=0.5):
        """
        Recursively assign types to belief pieces using backtracking and probability weights.

        This function attempts to assign a type to each belief piece such that all constraints are satisfied,
        using a backtracking algorithm guided by probability weights. It can optionally sort the pieces to improve efficiency.

        Args:
            belief_pieces (list): List of BeliefPiece objects to assign types to.
            pieces_left (dict): Dictionary of remaining piece types to assign (type -> count).
            i (int): Current index in belief_pieces (default 0).
            assignment (list): Current assignment list (default None).
            do_sort (bool): Whether to sort belief_pieces by constraint (default True, only at top level).
            start_time (float): Time when the function was first called (for timeout).
            timeout (float): Maximum allowed time in seconds for the search.

        Returns:
            list or None: List of assigned types if successful, else None if no valid assignment is found or timeout is reached.
        """
        if assignment is None:
            assignment = []

        if start_time is None:
            start_time = time.monotonic()
        elif time.monotonic() - start_time > timeout:
            return None

        if do_sort:
            def num_possible_types(bp):
                return sum(1 for t in bp.probabilities if bp.probabilities[t] > 0 and pieces_left[t] > 0)
            indexed_belief_pieces = list(enumerate(belief_pieces))
            sorted_indexed = sorted(indexed_belief_pieces, key=lambda x: num_possible_types(x[1]))
            if not sorted_indexed:
                return None  # TODO : hadle correctly
            sorted_indices, sorted_belief_pieces = zip(*sorted_indexed)
            result = self.assign_types_backtracking(list(sorted_belief_pieces), pieces_left, 0, [], do_sort=False, start_time=start_time, timeout=timeout)
            if result is not None:
                reordered = [None] * len(result)
                for idx, val in zip(sorted_indices, result):
                    reordered[idx] = val
                return reordered
            return None

        if i == len(belief_pieces):
            return assignment  

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
            result = self.assign_types_backtracking(
                belief_pieces, pieces_left, i+1, assignment + [t], do_sort=False, start_time=start_time, timeout=timeout
            )
            pieces_left[t] += 1  
            if result is not None:
                return result

        return None
    

    def assign_types_random(self, belief_pieces, pieces_left):
        """
        Assign types to belief pieces using a greedy/randomized approach.

        For each belief piece, selects the most probable available type, falling back to random selection if necessary.
        This method does not guarantee a valid or optimal assignment but is fast and simple.

        Args:
            belief_pieces (list): List of BeliefPiece objects to assign types to.
            pieces_left (dict): Dictionary of remaining piece types to assign (type -> count).

        Returns:
            list: List of assigned types for each belief piece.
        """
        pieces_left_copy = pieces_left.copy()
        assignment = []
        for bp in belief_pieces:
            available_types = [t for t in bp.probabilities if bp.probabilities[t] > 0 and pieces_left_copy.get(t, 0) > 0]
            if not available_types:
                available_types = [t for t in bp.probabilities if bp.probabilities[t] > 0]
            if not available_types:
                available_types = list(bp.probabilities.keys())
            best_type = max(available_types, key=lambda t: bp.probabilities.get(t, 0))
            assignment.append(best_type)
            if pieces_left_copy.get(best_type, 0) > 0:
                pieces_left_copy[best_type] -= 1
        return assignment


    

# Add a small test that sets up one revealed enemy piece plus several hidden belief pieces and verifies MCTS only samples the hidden ones.
# Refactor InfoSet further so it can be built from a pure knowledge snapshot without depending on a copied board at all, if you want a cleaner imperfect-information model.