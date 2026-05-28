import math
import random
from dataclasses import dataclass
from ALGO.infoSet import InfoSet
from ALGO.node import Node
import collections
import copy
import time

from ALGO.heuristics import CONFIDENCE_BY_LEVEL, HEURISTICS_WEIGHTS_BY_LEVEL, MCTSHeuristicMixin
from GAME.gameRules import GameRules
from GAME.piece import PieceType

REDETERMINIZE_FREQUENCY = 3
EXPANSION_TOP_MOVE_COUNT = 3
EXPANSION_PRIOR_EPSILON = 0.01
SIMULATION_MAX_STEPS = 25
@dataclass(frozen=True)
class MCTSPlayerIdentity:
    """
    Store immutable player metadata needed by detached MCTS searches.
    """
    order: int
    username: str


@dataclass
class MCTSPlayerState:
    """
    Store one player's board-dependent state for terminal evaluation.
    """
    order: int
    username: str
    pieces: dict
    end_state_cache: dict


@dataclass
class MCTSSnapshot:
    """
    Capture all AI state required to run search outside the live game thread.
    """
    game_type: str
    order: int
    difficulty: int
    rows: dict
    move_time: float
    last_moves: tuple
    last_moves_maxlen: int
    known_board: object
    hidden_belief_pieces: tuple
    revealed_opponent_pieces: tuple
    opponent_belief_pieces_left: dict
    player_identities: tuple

class MCTS(MCTSHeuristicMixin):
    """
    Monte Carlo Tree Search (MCTS) implementation for game AI.

     Search lifecycle:
          1. Build a detached snapshot from the live game state.
          2. Initialize the root node and the main information set.
          3. For each rollout, reset local state and periodically redeterminize
              hidden enemy information.
          4. Run selection down the tree until an unexpanded move or dead end is
              reached.
          5. Expand one new child node.
          6. Simulate forward with a rollout policy based on difficulty.
          7. Evaluate the final state with terminal checks and heuristics.
          8. Backpropagate the result up to the root.
          9. Undo simulated moves and repeat until the time budget expires.
         10. Play the root child with the strongest visit statistics.
    """
    @staticmethod
    def build_snapshot(ai, game_type, players):
        """
        Build a detached snapshot of the AI state for background search.

        Args:
            ai: AI player owning the search.
            game_type: Active game type.
            players: Live player objects for identity extraction.

        Returns:
            MCTSSnapshot: Immutable snapshot consumed by `MCTS`.
        """
        return MCTSSnapshot(
            game_type=game_type,
            order=ai.order,
            difficulty=ai.difficulty,
            rows=copy.deepcopy(ai.rows),
            move_time=ai.move_timers[ai.difficulty],
            last_moves=tuple(ai.last_moves),
            last_moves_maxlen=ai.last_moves.maxlen,
            known_board=copy.deepcopy(ai.known_board),
            hidden_belief_pieces=tuple(copy.deepcopy(ai.get_hidden_belief_pieces())),
            revealed_opponent_pieces=tuple(copy.deepcopy(ai.get_revealed_opponent_pieces())),
            opponent_belief_pieces_left=ai.opponent_belief_pieces_left.copy(),
            player_identities=tuple(
                MCTSPlayerIdentity(order=player.order, username=player.username)
                for player in players
            ),
        )

    def __init__(self, snapshot):
        """
        Initialize the MCTS algorithm.

        Args:
            snapshot: Detached AI search snapshot.
        """
        self.game_rules = GameRules(snapshot.game_type)
        self.player_to_move = snapshot.order
        self.player_identities = snapshot.player_identities

        self.order = snapshot.order
        self.difficulty = snapshot.difficulty
        self.rows = snapshot.rows
        self.opponent_belief_pieces_left = snapshot.opponent_belief_pieces_left.copy()
        self.previous_moves = collections.deque(
            snapshot.last_moves,
            maxlen=snapshot.last_moves_maxlen
        )

        self.simulation_by_level = {
            0: self.simulation_easy,
            1: self.simulation_medium,
            2: self.simulation_hard
        }

        self.confidence_by_level = CONFIDENCE_BY_LEVEL
        self.heuristics_weights_by_level = HEURISTICS_WEIGHTS_BY_LEVEL

        self._setup(snapshot)

    def _setup(self, snapshot):
        """
        Initialize or reset the persistent search state for a new root search.

        Args:
            snapshot: Detached AI search snapshot.
        """
        self.root_node = Node(None, None, self.order)
        self.current_node = self.root_node

        self.hidden_belief_pieces = copy.deepcopy(snapshot.hidden_belief_pieces)
        self.algo_infoSet = None
        self.infoSet_main = InfoSet(copy.deepcopy(snapshot.known_board), self.order, self.game_rules)
        self.infoSet_main.sync_opponent_knowledge(
            self.hidden_belief_pieces,
            copy.deepcopy(snapshot.revealed_opponent_pieces),
        )
        self.initial_possible_moves = len(self.infoSet_main.get_all_possible_moves())

        self.rollout_index = 0
        self.closest_dist_flag = self.infoSet_main.closest_piece_to_flag(
            self.order,
            1 - self.order,
        )
        self.undo_stack = []
        self.phase_time_totals = {
            "reset": 0.0,
            "redeterminize": 0.0,
            "selection": 0.0,
            "expansion": 0.0,
            "simulation": 0.0,
            "game_over": 0.0,
            "backpropagation": 0.0,
            "undo": 0.0,
        }
        self.phase_counts = {
            phase: 0
            for phase in self.phase_time_totals
        }

    def get_average_phase_times_ms(self):
        """
        Return average elapsed time per MCTS phase in milliseconds.

        Returns:
            dict: Average phase times keyed by phase name.
        """
        if self.rollout_index == 0:
            return {phase: 0.0 for phase in self.phase_time_totals}

        return {
            phase: (total / self.phase_counts[phase]) * 1000 if self.phase_counts[phase] else 0.0
            for phase, total in self.phase_time_totals.items()
        }
        
    def _reset_rollout_state(self):
        """
        Reset rollout-local state before one MCTS iteration.
        """
        reset_start = time.perf_counter()
        self.current_node = self.root_node
        self.previous_moves_algo = collections.deque(self.previous_moves, maxlen=self.previous_moves.maxlen)
        self.score_revealed_opponent_pieces = 0
        self.lost_combats = 0
        self.phase_time_totals["reset"] += time.perf_counter() - reset_start
        self.phase_counts["reset"] += 1

        if self.rollout_index % REDETERMINIZE_FREQUENCY == 0:
            redeterminize_start = time.perf_counter()
            self.determinized_root = self.infoSet_main.clone_for_rollout()
            self.determinized_root.actualize_belief_pieces(
                self.hidden_belief_pieces,
                self.opponent_belief_pieces_left.copy(),
            )
            self.phase_time_totals["redeterminize"] += time.perf_counter() - redeterminize_start
            self.phase_counts["redeterminize"] += 1
        self.algo_infoSet = self.determinized_root

    def _build_end_state_cache(self, pieces):
        """
        Precompute piece counts and flag location for end-state checks.

        Args:
            pieces: Mapping of piece ids to pieces.

        Returns:
            dict: Cached counts and flag position for one player.
        """
        piece_counts = {piece_type: 0 for piece_type in PieceType}
        flag_position = None

        for piece in pieces.values():
            if piece.type is None:
                continue

            piece_counts[piece.type] += 1
            if piece.type == PieceType.Drapeau:
                flag_position = piece.position

        return {
            "piece_counts": piece_counts,
            "flag_position": flag_position,
        }

    def _build_end_state_players(self):
        """
        Build lightweight player states for game-over evaluation.

        Returns:
            list: `MCTSPlayerState` objects for both sides.
        """
        players = []
        for identity in self.player_identities:
            pieces = self.algo_infoSet.board_state.get_pieces(identity.order)
            players.append(
                MCTSPlayerState(
                    order=identity.order,
                    username=identity.username,
                    pieces=pieces,
                    end_state_cache=self._build_end_state_cache(pieces),
                )
            )

        return players
        


    def algo(self):
        """
        Execute one full MCTS iteration.

        The iteration resets rollout state, performs selection and optional
        expansion, simulates forward from the chosen node, evaluates terminal
        status, then backpropagates the resulting score.
        """
        self._reset_rollout_state()

        phase_start = time.perf_counter()
        filtered_untried_moves = self.selection()
        self.phase_time_totals["selection"] += time.perf_counter() - phase_start
        self.phase_counts["selection"] += 1

        if filtered_untried_moves is not None:
            phase_start = time.perf_counter()
            self.expansion(filtered_untried_moves)
            self.phase_time_totals["expansion"] += time.perf_counter() - phase_start
            self.phase_counts["expansion"] += 1

            phase_start = time.perf_counter()
            self.simulation()
            self.phase_time_totals["simulation"] += time.perf_counter() - phase_start
            self.phase_counts["simulation"] += 1

        phase_start = time.perf_counter()
        game_won = self.game_over()
        self.phase_time_totals["game_over"] += time.perf_counter() - phase_start
        self.phase_counts["game_over"] += 1

        phase_start = time.perf_counter()
        self.backpropagation(game_won)
        self.phase_time_totals["backpropagation"] += time.perf_counter() - phase_start
        self.phase_counts["backpropagation"] += 1

        phase_start = time.perf_counter()
        while self.undo_stack:
            self.algo_infoSet.undo_move(self.undo_stack.pop())
        self.phase_time_totals["undo"] += time.perf_counter() - phase_start
        self.phase_counts["undo"] += 1

        self.rollout_index += 1

        

    def selection(self):
        """
        Traverse the tree from the root, selecting child nodes until a leaf is reached.

        Returns:
            list | None: The untried moves available at the selected node, or
            `None` when no child and no untried move remain.
        """
        while True:
            untried_moves = self.algo_infoSet.get_all_possible_moves()
            filtered_untried_moves = self.current_node.get_filtered_untried_moves(untried_moves)
            if len(filtered_untried_moves) > 0:
                return filtered_untried_moves

            skipped_children = set()
            while True:
                next_node = self.current_node.select_best_child(
                    maximize=self.current_node.player_turn == self.order,
                    excluded_children=skipped_children,
                )
                if next_node is None:
                    return None

                if self.update_infoSet(next_node.move):
                    self.current_node = next_node
                    break

                skipped_children.add(next_node)
            
    def update_infoSet(self, move):
        """
        Apply a simulated move to the current rollout information set.

        Args:
            move: The move to apply inside the rollout state.

        Returns:
            bool: ``True`` when the move was applied, else ``False``.
        """
        result, undo_record = self.algo_infoSet.apply_move(move, self.confidence_by_level[self.difficulty])

        if result is None:
            return False

        self.undo_stack.append(undo_record)
        self.score_revealed_opponent_pieces += result["encounter_score"]
        self.lost_combats += int(result["encounter_score"] < 0)
        self.previous_moves_algo.append(move)
        return True

    def expansion(self, filtered_untried_moves):
        """
        Expand the current node by adding a new child node if possible.

        Args:
            filtered_untried_moves (list): Candidate moves not yet expanded from
            the current node.
        """
        if not filtered_untried_moves:
            return

        skipped_moves = set()

        while True:
            remaining_moves = [
                move for move in filtered_untried_moves
                if move not in skipped_moves
            ]
            if not remaining_moves:
                return

            next_move, next_prior = self._choose_expansion_move(remaining_moves)

            if self.update_infoSet(next_move):
                self.current_node.tried_moves.add(next_move)

                next_node = Node(self.current_node, next_move, self.algo_infoSet.player_turn)
                next_node.prior = next_prior

                self.current_node.children.append(next_node)
                self.current_node = next_node
                return

            skipped_moves.add(next_move)
                

    def simulation(self):
        """
        Simulate a playout from the current node to a terminal state or step limit.

        Returns:
            None
        """
        game_over = 0
        s = 0
        while game_over == 0 and s < SIMULATION_MAX_STEPS:
            if not self.simulation_by_level[self.difficulty]():
                return game_over

            game_over = self.game_over()
           
            s += 1
    

    def backpropagation(self, value):
        """
        Backpropagate the simulation result up the tree, updating visit and win counts.

        Args:
            value: The result of the simulation to propagate.
        """
        node = self.current_node

        while node is not None:
            node.visit_count += 1
            node.value += value
            node = node.parent

    def _choose_expansion_move(self, candidate_moves):
        """
        Choose the next move to expand, using priors when available.

        Args:
            candidate_moves: Unexpanded legal moves from the current node.

        Returns:
            tuple: Selected move and its associated prior weight.
        """
        if not candidate_moves:
            return None, None

        if self.current_node.player_turn != self.order:
            return random.choice(candidate_moves), 1.0

        if self.difficulty == 0:
            return random.choice(candidate_moves), 1.0

        if self.difficulty == 1:
            scored_moves = [
                (move, self.prior_evaluate_medium_move(move))
                for move in candidate_moves
            ]
        else:
            scored_moves = [
                (move, self.prior_evaluate_difficult_move(move))
                for move in candidate_moves
            ]

        scored_moves.sort(key=lambda item: item[1], reverse=True)
        top_moves = scored_moves[:EXPANSION_TOP_MOVE_COUNT]

        min_score = min(score for _, score in top_moves)
        shifted_weights = [
            score - min_score + EXPANSION_PRIOR_EPSILON
            for _, score in top_moves
        ]

        chosen_move, chosen_prior = random.choices(
            top_moves,
            weights=shifted_weights,
            k=1,
        )[0]

        return chosen_move, chosen_prior


    def simulation_easy(self):
        """
        Perform a random move for easy difficulty.

        Returns:
            int: `1` when a move was applied, `0` when no legal move exists.
        """
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            return 0

        move = random.choice(possible_moves)
        self.update_infoSet(move)

        return 1

    def _simulation_with_priors(self, prior_func):
        """
        Perform one rollout step using a mix of random choice and move priors.

        Args:
            prior_func: Callable used to score candidate moves for the AI side.

        Returns:
            int: `1` when a move was applied, `0` when no legal move exists.
        """
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            return 0

        move_priors = []
        for move in possible_moves:
            if self.algo_infoSet.player_turn == self.order:
                prior = prior_func(move)
                move_priors.append((move, prior))
            else:
                move_priors.append((move, 1))

        if random.random() < 0.5:
            move = random.choice(possible_moves)
        else:
            max_prior = max(move_priors, key=lambda x: x[1])[1]
            best_moves = [m for m, p in move_priors if p == max_prior]
            move = random.choice(best_moves)

        self.update_infoSet(move)
        return 1

    def simulation_medium(self): 
        """
        Perform one medium-difficulty rollout step.

        Returns:
            int: `1` when a move was applied, `0` when no legal move exists.
        """
        return self._simulation_with_priors(self.prior_evaluate_medium_move)

    def simulation_hard(self): 
        """
        Perform one hard-difficulty rollout step.

        Returns:
            int: `1` when a move was applied, `0` when no legal move exists.
        """
        return self._simulation_with_priors(self.prior_evaluate_difficult_move)

    def game_over(self):
        """
        Evaluate whether the simulated state is terminal for either side.

        Returns:
            float: Heuristic terminal evaluation from the AI perspective.
        """
        ai_won = 0
        opp_won = 0
        players = self._build_end_state_players()
        for player in players:
            ended, _ = self.game_rules.check_player_end_state(
                player,
                players,
                self.algo_infoSet.board_state,
                reason=1,
            )
            if ended:
                ai_won = player.order != self.order
                opp_won = player.order == self.order
        
        return self.heuristic_evaluation(ai_won, opp_won) 

    def get_best_move(self):
        """
        Return the move from the best child of the root node after search.

        Returns:
            Move: The selected move to play.
        """
        best_child = self.root_node.get_best_move_child()
        if best_child is not None:
            best_move = best_child.move
        else:
            fallback_moves = self.infoSet_main.get_all_possible_moves()
            if not fallback_moves:
                return None
            best_move = random.choice(fallback_moves)

        return best_move

    def get_root_visit_summary(self):
        """
        Return visit statistics for each root child after search.

        Returns:
            list[str]: Root-child visit summaries sorted by visit count.
        """
        ranked_children = sorted(
            self.root_node.children,
            key=lambda child: (
                child.visit_count,
                child.value / child.visit_count if child.visit_count else float("-inf"),
            ),
            reverse=True,
        )

        return [
            (
                f"move={child.move}, visits={child.visit_count}, "
                f"value={child.value:.3f}"
            )
            for child in ranked_children
        ]
    

        

    
