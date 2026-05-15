import copy
import random
import time
from GAME.piece import BeliefPiece, Piece, PieceType


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
        self.actualize_stats = None

    def get_all_possible_moves(self, player_turn = None):
        """
        Get all possible moves for the current player.
        
        Returns:
            list: List of possible moves for the current player.
        """
        if player_turn is None:
            player_turn = self.player_turn
        pieces = self.board_state.get_pieces(player_turn)
        possible_moves = self.game_rules.get_remaining_moves(pieces, player_turn, self.board_state)
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

        encounter_score = 0

        x_0, y_0, x_1, y_1 = move.get_params()
        tile_from = self.board_state.tiles[y_0][x_0]
        tile_to = self.board_state.tiles[y_1][x_1]

        attacker = tile_from.piece
        defender = tile_to.piece

        if defender is None:
            self.board_state.move(move)
        else:
            encounter_score = self.encounter_score(attacker, defender)

            winner = self.game_rules.combat(attacker, defender)
            tile_from.piece = None

            if winner is None:
                tile_to.piece = None
            elif winner is attacker:
                tile_to.piece = attacker
                attacker.position = move.moveTo

        self.player_turn = 1 - self.player_turn
        return {
            "encounter_score": encounter_score,
            "had_combat": defender is not None
        }

    def encounter_score(self, my_piece, their_piece):
        if their_piece is None:
            return 0

        their_value = their_piece.type.score
        winner = self.game_rules.combat(my_piece, their_piece)

        if winner is my_piece:
            return 2 * their_value
        elif winner is None:
            return 0
        else:
            return -my_piece.type.score
        
    def closest_piece_to_flag(self):
        player_1_pieces = self.board_state.get_pieces(1)
        flag_piece = next(
            (piece for piece in player_1_pieces.values() if piece.type == PieceType.Drapeau),
            None,
        )

        flag_position = flag_piece.position if flag_piece is not None else None

        if flag_position is None:
            return 0

        opp_pieces = self.board_state.get_pieces(0)

        if not opp_pieces:
            return 0

        closest_piece = min(
            opp_pieces.values(),
            key=lambda piece: abs(piece.position[0] - flag_position[0]) + abs(piece.position[1] - flag_position[1]),
            default=None,
        )

        if closest_piece is None:
            return 0

        closest_dist = ((flag_position[0] - closest_piece.position[0]) ** 2 + (flag_position[1] - closest_piece.position[1]) ** 2) ** (1/2)

        return closest_dist

    def sync_opponent_knowledge(self, hidden_belief_pieces, revealed_opponent_pieces):
        for piece in hidden_belief_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

        for piece in revealed_opponent_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

    def return_pieces(self, move):
        x_0, y_0, x_1, y_1 = move.get_params()
        my_piece = self.board_state.tiles[y_0][x_0].piece
        their_piece = self.board_state.tiles[y_1][x_1].piece

        return my_piece, their_piece

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

        self.actualize_stats = {
            "hidden_belief_pieces": len(belief_pieces),
            "recursive_calls": 0,
            "backtracking_ns": 0,
            "used_random_fallback": False,
            "assignment_completed": False,
            "timed_out": False,
        }

        possible_setup = self.assign_types_backtracking(belief_pieces, pieces_left)

        if possible_setup == []:
            self.actualize_stats["used_random_fallback"] = True
            possible_setup = self.assign_types_random(belief_pieces, pieces_left)

        if possible_setup is not None:
            for belief_piece, type in zip(belief_pieces, possible_setup):
                piece = Piece(belief_piece.id, type, belief_piece.position, belief_piece.owner, False)
                self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece

    def assign_types_backtracking(self, belief_pieces, pieces_left, timeout=0.5):
        """
        Assign types to belief pieces using a sorted backtracking search.

        This wrapper sorts the belief pieces once, then delegates the recursive search
        to a helper focused only on backtracking. If the search times out after finding
        a partial assignment, the remaining belief pieces are assigned with the random
        fallback so the best partial result is not discarded. If no valid partial or
        complete assignment can be found, the function returns `None`.

        Args:
            belief_pieces (list): List of BeliefPiece objects to assign types to.
            pieces_left (dict): Dictionary of remaining piece types to assign (type -> count).
            timeout (float): Maximum allowed time in seconds for the search.

        Returns:
            list or None: List of assigned types for all belief pieces if a complete
            assignment is found or if a timed-out partial assignment can be completed
            with the random fallback, else `None` if no valid assignment is found.
        """
        if not belief_pieces:
            if self.actualize_stats is not None:
                self.actualize_stats["assignment_completed"] = True
            return []

        sorted_indices, sorted_belief_pieces = self._sort_belief_pieces_by_constraints(belief_pieces, pieces_left)
        start_ns = time.perf_counter_ns()
        result, completed, timed_out = self._assign_types_backtracking_recursive(
            list(sorted_belief_pieces), pieces_left, 0, [], time.monotonic(), timeout
        )
        if self.actualize_stats is not None:
            self.actualize_stats["backtracking_ns"] = time.perf_counter_ns() - start_ns
            self.actualize_stats["assignment_completed"] = completed
            self.actualize_stats["timed_out"] = timed_out
        if result is None:
            return None

        if timed_out and not completed:
            if self.actualize_stats is not None:
                self.actualize_stats["used_random_fallback"] = True
            remaining_pieces_left = pieces_left.copy()
            for assigned_type in result:
                remaining_pieces_left[assigned_type] -= 1

            remaining_belief_pieces = list(sorted_belief_pieces[len(result):])
            result = result + self.assign_types_random(remaining_belief_pieces, remaining_pieces_left)

        reordered = [None] * len(result)
        for idx, val in zip(sorted_indices, result):
            reordered[idx] = val
        return reordered

    def _sort_belief_pieces_by_constraints(self, belief_pieces, pieces_left):
        """
        Sort belief pieces by how constrained they are.

        Pieces with fewer currently valid types are placed first so the backtracking
        search hits dead ends earlier and explores fewer useless branches.

        Args:
            belief_pieces (list): List of BeliefPiece objects to sort.
            pieces_left (dict): Dictionary of remaining piece types to assign (type -> count).

        Returns:
            tuple: A pair `(sorted_indices, sorted_belief_pieces)` preserving the original
            positions and the reordered belief pieces.
        """
        def num_possible_types(bp):
            return sum(1 for t in bp.probabilities if bp.probabilities[t] > 0 and pieces_left[t] > 0)

        indexed_belief_pieces = list(enumerate(belief_pieces))
        return zip(*sorted(indexed_belief_pieces, key=lambda x: num_possible_types(x[1])))

    def _assign_types_backtracking_recursive(self, belief_pieces, pieces_left, i, assignment, start_time, timeout):
        """
        Recursively assign types to sorted belief pieces using backtracking.

        At each recursion level, the function selects one valid type for the current
        belief piece, updates `pieces_left`, and explores the next piece. If a branch
        fails, the change is undone and the next candidate type is tried. If the search
        times out, the deepest partial assignment found so far is returned so the caller
        can complete the remaining pieces with a fallback strategy.

        Args:
            belief_pieces (list): Sorted list of BeliefPiece objects to assign.
            pieces_left (dict): Dictionary of remaining piece types to assign (type -> count).
            i (int): Index of the current belief piece in the sorted list.
            assignment (list): Types chosen so far for earlier pieces.
            start_time (float): Monotonic timestamp marking the start of the search.
            timeout (float): Maximum allowed time in seconds for the search.

        Returns:
            tuple: `(assignment, completed, timed_out)` where `assignment` is the best
            assignment found for this branch, `completed` indicates whether all pieces
            were assigned, and `timed_out` indicates whether the search stopped because
            of the timeout. On timeout, `assignment` may be only a partial prefix of
            the full assignment; on branch failure without timeout, `assignment` is `None`.
        """
        if self.actualize_stats is not None:
            self.actualize_stats["recursive_calls"] += 1

        if time.monotonic() - start_time > timeout:
            return assignment, False, True

        if i == len(belief_pieces):
            return assignment, True, False

        bp = belief_pieces[i]
        possible_types = [t for t in bp.probabilities if bp.probabilities[t] > 0 and pieces_left[t] > 0]
        if not possible_types:
            return None, False, False

        sampled_types = self._weighted_shuffle_without_replacement(possible_types, bp.probabilities)
        best_partial_assignment = None

        for t in sampled_types:
            pieces_left[t] -= 1
            result, completed, timed_out = self._assign_types_backtracking_recursive(
                belief_pieces, pieces_left, i+1, assignment + [t], start_time, timeout
            )
            pieces_left[t] += 1
            if completed:
                return result, True, timed_out
            if timed_out and result is not None:
                if best_partial_assignment is None or len(result) > len(best_partial_assignment):
                    best_partial_assignment = result

        if best_partial_assignment is not None:
            return best_partial_assignment, False, True

        return None, False, False

    def _weighted_shuffle_without_replacement(self, possible_types, probabilities):
        """
        Build a random weighted ordering of candidate types without duplicates.

        Higher-probability types are more likely to appear earlier in the returned
        list, but each type appears at most once.

        Args:
            possible_types (list): Candidate types that may be assigned.
            probabilities (dict): Probability mapping for the current belief piece.

        Returns:
            list: A weighted random ordering of `possible_types` without replacement.
        """
        remaining_types = list(possible_types)
        ordered_types = []

        while remaining_types:
            weights = [probabilities[t] for t in remaining_types]
            total = sum(weights)
            if total <= 0:
                ordered_types.extend(random.sample(remaining_types, k=len(remaining_types)))
                break

            chosen_type = random.choices(remaining_types, weights=weights, k=1)[0]
            ordered_types.append(chosen_type)
            remaining_types.remove(chosen_type)

        return ordered_types

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
