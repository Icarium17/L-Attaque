import copy
import random
import time
from GAME.board import Board
from GAME.piece import BeliefPiece, Piece, PieceType


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
        self._possible_moves_cache = {
            0: {},
            1: {},
        }

    @staticmethod
    def _clone_piece_for_rollout(piece):
        if piece is None:
            return None

        cloned_piece = piece.clone()
        return cloned_piece

    def clone_for_rollout(self):
        """
        Clone only the state required for one MCTS rollout.

        Returns:
            InfoSet: Independent rollout copy with a fresh move cache.
        """
        cloned_board = Board(self.board_state.game_type)

        for row in self.board_state.tiles:
            for tile in row:
                if tile.piece is None:
                    continue

                cloned_board.tiles[tile.y][tile.x].piece = self._clone_piece_for_rollout(tile.piece)

        return InfoSet(cloned_board, self.player_turn, self.game_rules)

    def invalidate_possible_moves_cache(self, player_turn=None):
        """
        Mark cached move lists as stale.

        Args:
            player_turn: Optional player whose cache should be invalidated.

        Returns:
            None
        """
        if player_turn is None:
            for order in self._possible_moves_cache:
                self._possible_moves_cache[order].clear()
            return

        self._possible_moves_cache[player_turn].clear()

    def _get_piece_possible_moves(self, piece, player_turn):
        """
        Compute legal moves for a single piece.

        Args:
            piece: The piece whose moves should be generated.
            player_turn: Owner of the piece.

        Returns:
            list: Legal moves for the provided piece.
        """
        if piece.type in (PieceType.Drapeau, PieceType.Bombe):
            return []

        return self.game_rules.get_remaining_moves(
            {piece.id: piece},
            player_turn,
            self.board_state,
        )

    def _invalidate_piece_moves(self, piece):
        """
        Remove cached moves for one piece if present.

        Args:
            piece: Piece whose cached moves should be discarded.

        Returns:
            None
        """
        if piece is None:
            return

        self._possible_moves_cache[piece.owner].pop(piece.id, None)

    def _invalidate_local_possible_moves_cache(self, positions, touched_pieces=()):
        """
        Invalidate only move caches affected by local board changes.

        Args:
            positions: Coordinates whose occupancy changed.
            touched_pieces: Pieces directly moved, removed, or restored.

        Returns:
            None
        """
        normalized_positions = [
            (x, y)
            for x, y in positions
            if x is not None and y is not None
        ]

        for piece in touched_pieces:
            self._invalidate_piece_moves(piece)

        for row in self.board_state.tiles:
            for tile in row:
                piece = tile.piece
                if piece is None:
                    continue

                px, py = piece.position

                for x, y in normalized_positions:
                    if (px, py) == (x, y) or abs(px - x) + abs(py - y) == 1:
                        self._invalidate_piece_moves(piece)
                        break

                    if piece.type == PieceType.Eclaireur and (px == x or py == y):
                        self._invalidate_piece_moves(piece)
                        break

    def get_all_possible_moves(self, player_turn = None):
        """
        Get all possible moves for the current player.

        Args:
            player_turn: Optional player override. Uses `self.player_turn` when omitted.
        
        Returns:
            list: List of possible moves for the current player.
        """
        if player_turn is None:
            player_turn = self.player_turn

        pieces = self.board_state.get_pieces(player_turn)
        cached_moves = self._possible_moves_cache[player_turn]
        current_piece_ids = set(pieces)

        for cached_piece_id in list(cached_moves):
            if cached_piece_id not in current_piece_ids:
                del cached_moves[cached_piece_id]

        possible_moves = []
        for piece_id, piece in pieces.items():
            if piece_id not in cached_moves:
                cached_moves[piece_id] = self._get_piece_possible_moves(piece, player_turn)

            possible_moves.extend(cached_moves[piece_id])

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

    def apply_move(self, move, confidence = 1.0):
        """
        Apply a move to the current InfoSet and return the data required to undo it.

        Args:
            move: The move to apply.
            confidence: Confidence multiplier used when evaluating uncertain combat.

        Returns:
            tuple: ``(summary, undo_record)`` when the move is valid, otherwise
            ``(None, None)``.
        """
        valid = self.validate_move(move)
        if not valid:
            return None, None

        encounter_score = 0

        x_0, y_0, x_1, y_1 = move.get_params()
        tile_from = self.board_state.tiles[y_0][x_0]
        tile_to = self.board_state.tiles[y_1][x_1]

        attacker = tile_from.piece
        defender = tile_to.piece

        undo_record = {
            "prev_player_turn": self.player_turn,
            "x_0": x_0,
            "y_0": y_0,
            "x_1": x_1,
            "y_1": y_1,
            "attacker": attacker,
            "defender": defender,
            "attacker_old_position": attacker.position,
            "attacker_old_mcts_revealed": attacker.mcts_revealed,
            "defender_old_mcts_revealed": defender.mcts_revealed if defender is not None else None,
        }

        if defender is None:
            tile_from.piece = None
            tile_to.piece = attacker
            attacker.position = move.moveTo
        else:
            if not attacker.revealed :
                attacker.mcts_revealed = True

            if not defender.revealed : 
                defender.mcts_revealed = True
                
            encounter_score = self.encounter_score(attacker, defender, confidence) 

            winner = self.game_rules.combat(attacker, defender)
            tile_from.piece = None

            if winner is None:
                tile_to.piece = None
            elif winner is attacker:
                tile_to.piece = attacker
                attacker.position = move.moveTo

        self.player_turn = 1 - self.player_turn
        self._invalidate_local_possible_moves_cache(
            [move.moveFrom, move.moveTo],
            (attacker, defender),
        )
        return {
            "encounter_score": encounter_score,
            "had_combat": defender is not None
        }, undo_record

    def undo_move(self, undo_record):
        """
        Restore the board state saved by ``apply_move()``.

        Args:
            undo_record: State snapshot returned by ``apply_move()``.

        Returns:
            None
        """
        x_0 = undo_record["x_0"]
        y_0 = undo_record["y_0"]
        x_1 = undo_record["x_1"]
        y_1 = undo_record["y_1"]

        tile_from = self.board_state.tiles[y_0][x_0]
        tile_to = self.board_state.tiles[y_1][x_1]

        attacker = undo_record["attacker"]
        defender = undo_record["defender"]

        tile_from.piece = attacker
        tile_to.piece = defender

        attacker.position = undo_record["attacker_old_position"]
        attacker.mcts_revealed = undo_record["attacker_old_mcts_revealed"]

        if defender is not None:
            defender.mcts_revealed = undo_record["defender_old_mcts_revealed"]

        self.player_turn = undo_record["prev_player_turn"]
        self._invalidate_local_possible_moves_cache(
            [attacker.position, (x_1, y_1)],
            (attacker, defender),
        )

    def update_infoSet(self, move, confidence = 1.0):
        """
        Backward-compatible wrapper around ``apply_move()``.

        Args:
            move: The move to apply.
            confidence: Confidence multiplier used when evaluating uncertain combat.

        Returns:
            None if move is invalid, otherwise a summary dict describing the move result.
        """
        summary, _ = self.apply_move(move, confidence)
        return summary

    def encounter_score(self, attacker, defender, confidence = 1.0):
        """
        Estimate the value swing of one combat from the AI perspective.

        Args:
            attacker: The attacking piece in the simulated combat.
            defender: The defending piece in the simulated combat.
            confidence: Confidence multiplier applied to uncertain opponent value.

        Returns:
            float: Positive when the exchange favors the AI, negative when it does not.
        """
        if attacker.owner == 1:
            my_piece = attacker
            their_piece = defender

        else :
            my_piece = defender
            their_piece = attacker

        if their_piece is None:
            return 0

        winner = self.game_rules.combat(attacker, defender)

        my_value = my_piece.type.score
        their_value = their_piece.type.score

        confidence = 1.0 if their_piece.revealed else confidence

        adjusted_their_value = their_value * confidence

        if winner is my_piece:
            return adjusted_their_value - my_value * 0.5

        elif winner is None:
            return 0

        else:
            return -my_value
        
    def closest_piece_to_flag(self):
        """
        Measure how close player 0 is to player 1's flag.

        Returns:
            float: Euclidean distance from the nearest player 0 piece to player 1's
            flag, or `0` when the relevant pieces are missing.
        """
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
        """
        Copy known opponent pieces into the local board state.

        Args:
            hidden_belief_pieces: Hidden opponent belief pieces to clone onto the board.
            revealed_opponent_pieces: Revealed opponent pieces to clone onto the board.

        Returns:
            None
        """
        for piece in hidden_belief_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

        for piece in revealed_opponent_pieces:
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece.clone()

        self.invalidate_possible_moves_cache()

    def return_pieces(self, move):
        """
        Return the source and destination pieces involved in a move.

        Args:
            move: The move whose endpoints should be inspected.

        Returns:
            tuple: A pair `(my_piece, their_piece)` from the move source and destination.
        """
        x_0, y_0, x_1, y_1 = move.get_params()
        my_piece = self.board_state.tiles[y_0][x_0].piece
        their_piece = self.board_state.tiles[y_1][x_1].piece

        return my_piece, their_piece

    def actualize_belief_pieces(self, hidden_belief_pieces, pieces_left):
        """
        Determinize hidden belief pieces into concrete pieces on the board.

        The method attempts a constrained backtracking assignment when the hidden
        board state matches expectations, and falls back to a greedy randomized
        assignment when mismatches or search failure occur. It also records summary
        statistics about the actualization attempt in `self.actualize_stats`.

        Args:
            hidden_belief_pieces: Belief pieces representing currently hidden opponents.
            pieces_left: Remaining piece inventory keyed by `PieceType`.

        Returns:
            None
        """
        belief_piece_ids = {piece.id for piece in hidden_belief_pieces}
        board_belief_pieces = [
            tile.piece
            for row in self.board_state.tiles
            for tile in row
            if tile.piece is not None and isinstance(tile.piece, BeliefPiece)
        ]
        belief_pieces = [
            belief_piece
            for belief_piece in board_belief_pieces
            if belief_piece.id in belief_piece_ids
        ]

        used_mismatch_recovery = (
            len(belief_pieces) != len(belief_piece_ids)
            or len(belief_pieces) != len(board_belief_pieces)
        )
        if used_mismatch_recovery:
            belief_pieces = board_belief_pieces

        self.actualize_stats = {
            "hidden_belief_pieces": len(belief_pieces),
            "recursive_calls": 0,
            "backtracking_ns": 0,
            "used_random_fallback": False,
            "assignment_completed": False,
            "timed_out": False,
            "used_mismatch_recovery": used_mismatch_recovery,
        }

        if used_mismatch_recovery:
            self.actualize_stats["used_random_fallback"] = True
            possible_setup = self.assign_types_random(belief_pieces, pieces_left)
        else:
            possible_setup = self.assign_types_backtracking(belief_pieces, pieces_left)

        if possible_setup in (None, []):
            self.actualize_stats["used_random_fallback"] = True
            possible_setup = self.assign_types_random(belief_pieces, pieces_left)

        for belief_piece, type in zip(belief_pieces, possible_setup):
            piece = Piece(belief_piece.id, type, belief_piece.position, belief_piece.owner, False)
            self.board_state.tiles[piece.position[1]][piece.position[0]].piece = piece

        self.invalidate_possible_moves_cache()

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
