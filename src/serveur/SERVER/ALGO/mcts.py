import random
from ALGO.infoSet import InfoSet
from ALGO.node import Node
import collections
import copy
import time

from GAME.piece import PieceType

class MCTS:
    """
    Monte Carlo Tree Search (MCTS) implementation for game AI.
    Handles selection, expansion, simulation, and backpropagation phases.
    """
    def __init__(self, ai, game_rules, players):
        """
        Initialize the MCTS algorithm.

        Args:
            ai: The AI player object controlling the search.
            game_rules: The rules object governing game logic and move validation.
            players: List of player objects participating in the game.
        """
        self.ai = ai
        self.game_rules = game_rules
        self.player_to_move = self.ai.order
        self.players = players

        self.order = self.ai.order
        self.difficulty = self.ai.difficulty
        self.previous_moves = collections.deque(
            self.ai.last_moves,
            maxlen=self.ai.last_moves.maxlen
        )

        self.simulation_by_level = {
            0: self.simulation_easy,
            1: self.simulation_medium,
            2: self.simulation_hard
        }

        self.confidence_by_level = {
            0 : 1.0,
            1 : 0.5,
            2: 0.75
        }

        self.heuristics_weights_by_level = {
            0 : {
                "material": 1.0
            },
            1 : {
                "material": 1.0,
                "mobility": 0.5,
                "flag": 1.0,
                "info": 1.0,
                "trades": 1.0
            },
            2 : {
                "material": 1.0,
                "mobility": 0.3,
                "flag": 2.0,
                "info": 3.0,
                "trades": 2.0,
                "opp_confidence_material": 1.5,
                "reveal_bonus": 2.0,
                "self_reveal_penalty": 1.0
            }
        }

        self._setup(ai)

    def _setup(self, ai):
        """
        Initialize or reset the persistent search state for a new root search.

        Args:
            ai: The AI player owning this search instance.
        """
        self.root_node = Node(None, None)
        self.current_node = self.root_node

        self.hidden_belief_pieces = self.ai.get_hidden_belief_pieces()
        self.algo_infoSet = None
        self.infoSet_main = InfoSet(copy.deepcopy(ai.known_board), ai.order, self.game_rules)
        self.infoSet_main.sync_opponent_knowledge(self.hidden_belief_pieces, self.ai.get_revealed_opponent_pieces())
        self.initial_possible_moves = len(self.infoSet_main.get_all_possible_moves())

        self.rollout_index = 0
        self.closest_dist = self.infoSet_main.closest_piece_to_flag()
        
    def _reset_rollout_state(self):
        """
        Reset rollout-local state before one MCTS iteration.

        Returns:
            dict: Metadata about whether the rollout reused a cached determinization
            or rebuilt opponent hidden information from scratch.
        """
        self.current_node = self.root_node
        self.previous_moves_algo = collections.deque(self.previous_moves, maxlen=self.previous_moves)
        self.score_revealed_opponent_pieces = 0
        self.lost_combats = 0

        if self.rollout_index % 5 == 0:
            actualize_start_ns = time.perf_counter_ns()
            self.algo_infoSet = copy.deepcopy(self.infoSet_main)
            self.algo_infoSet.actualize_belief_pieces(
                self.hidden_belief_pieces,
                self.ai.opponent_belief_pieces_left.copy(),
            )
            self.determinized_root = copy.deepcopy(self.algo_infoSet)
            return {
                "mode": "redeterminized",
                "actualize_ns": time.perf_counter_ns() - actualize_start_ns,
                "actualize_stats": self.algo_infoSet.actualize_stats or {},
            }
        else:
            self.algo_infoSet = copy.deepcopy(self.determinized_root)
            return {
                "mode": "cached-root",
                "actualize_ns": 0,
                "actualize_stats": {},
            }
        


    def algo(self):
        """
        Execute one full MCTS iteration.

        The iteration resets rollout state, performs selection and optional
        expansion, simulates forward from the chosen node, evaluates terminal
        status, then backpropagates the resulting score.
        """
        self._reset_rollout_state()
        filtered_untried_moves = self.selection()

        if filtered_untried_moves is not None:
            self.expansion(filtered_untried_moves)

            self.simulation()

        game_won = self.game_over()

        self.backpropagation(game_won)

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

            next_node = self.current_node.select_best_child()
            if next_node is not None:
                self.current_node = next_node
            else:
                return None
            
    def update_infoSet(self, move):
        """
        Apply a simulated move to the current rollout information set.

        Args:
            move: The move to apply inside the rollout state.

        Returns:
            None
        """
        result = self.algo_infoSet.update_infoSet(move, self.confidence_by_level[self.difficulty])

        if result is None:
            return

        self.score_revealed_opponent_pieces += result["encounter_score"]
        self.lost_combats += int(result["encounter_score"] < 0)
        self.previous_move.append(move)


    def expansion(self, filtered_untried_moves):
        """
        Expand the current node by adding a new child node if possible.

        Args:
            filtered_untried_moves (list): Candidate moves not yet expanded from
            the current node.
        """
        next_move = random.choice(filtered_untried_moves)
        
        self.update_infoSet(next_move)

        self.current_node.tried_moves.add(next_move)

        next_node = Node(self.current_node, next_move)
        self.current_node.children.append(next_node)
        self.current_node = next_node
            

    def simulation(self):
        """
        Simulate a playout from the current node to a terminal state or step limit.

        Returns:
            None
        """
        game_over = 0
        s = 0
        while game_over == 0 and s < 25:
            if not self.simulation_by_level[self.difficulty]():
                return game_over

            game_over = self.game_over()
           
            s += 1
    

    def backpropagation(self, win_score):
        """
        Backpropagate the simulation result up the tree, updating visit and win counts.

        Args:
            win_score: The result of the simulation to propagate.
        """
        node = self.current_node
        while node is not None:
            node.visit_count += 1
            node.win_score += win_score
            node = node.parent

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
    
    def _revisiting_count(self, move, weight):
        count = 0
        for prev in self.previous_moves_algo:
            if move == prev:
                count += 1
        return weight * (1 - 0.5 ** count)
    
    def _resolve_combat(self, attacker, defender):
        """
        Classify the likely combat outcome between two concrete pieces.

        Args:
            attacker: Attacking piece in the simulated combat.
            defender: Defending piece in the simulated combat.

        Returns:
            str: One of `"win"`, `"loss"`, `"draw"`, `"unknown"`, or `"invalid"`
            from the AI perspective of the attacker/defender comparison logic.
        """
        if attacker is None or defender is None:
            return "invalid"

        a = attacker.type
        d = defender.type

        if d == PieceType.Drapeau:
            return "win"

        if d == PieceType.Bombe:
            return "win" if a == PieceType.Demineur else "loss"

        if a == PieceType.Espion and d == PieceType.Marechal:
            return "win"

        # --- fallback rules ---
        if a.power is None or d.power is None:
            return "unknown"

        if a.power > d.power:
            return "win"
        elif a.power < d.power:
            return "loss"
        else:
            return "draw"
            
    def _piece_value(self, piece):
        """
        Return the heuristic score value of a piece.

        Args:
            piece: Piece to evaluate.

        Returns:
            int: Piece score value, or `-1` when no piece is present.
        """
        if piece is None:
            return -1

        return piece.type.score
    
    def _common_priors(self, move, my_piece, their_piece, my_val, their_val, eclaireur_bonus=0.1, espion_bonus=0.7):
        """
        Compute shared tactical priors used by medium and hard move scoring.

        Args:
            move: Candidate move being scored.
            my_piece: Moving piece.
            their_piece: Target piece, if any.
            my_val: Numeric power of the moving piece.
            their_val: Numeric power of the target piece.
            eclaireur_bonus: Bonus applied to scout moves.
            espion_bonus: Bonus applied to favorable spy attacks.

        Returns:
            float: Base prior score before difficulty-specific adjustments.
        """
        score = 0.0

        if their_piece is not None:
            combat_result = self._resolve_combat(my_piece, their_piece)

            if combat_result == "win":
                score += 0.8

            elif combat_result == "loss":
                score -= 0.8

            else:
                score -= 0.1 

            if their_piece.type == PieceType.Drapeau:
                score += 1.5

            if my_piece.type == PieceType.Espion and their_piece.type == PieceType.Marechal:
                score += espion_bonus

        if my_piece.type == PieceType.Eclaireur:
            score += eclaireur_bonus

        x, y = move.moveTo
        center_x, center_y = 4.5, 4.5

        dist_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        score -= 0.03 * dist_to_center

        if x == 0 or x == 9 or y == 0 or y == 9:
            score -= 0.2

        board = self.algo_infoSet.board_state.tiles

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx <= 9 and 0 <= ny <= 9:
                neighbor = board[ny][nx].piece

                if neighbor and neighbor.revealed:

                    neighbor_power = self._piece_value(neighbor)
                    my_power = self._piece_value(my_piece)

                    if my_power < neighbor_power:
                        score -= 0.4

        return score

    def prior_evaluate_medium_move(self, move):
        """
        Evaluate one candidate move with medium-difficulty priors.

        Args:
            move: Candidate move to score.

        Returns:
            float: Desirability score for the move.
        """
        my_piece, their_piece = self.algo_infoSet.return_pieces(move)

        my_val = self._piece_value(my_piece)
        their_val = self._piece_value(their_piece)

        confidence = (
            1.0
            if their_piece is not None and their_piece.revealed
            else self.confidence_by_level[1]
        )

        score = self._common_priors(
            move,
            my_piece,
            their_piece,
            my_val,
            their_val,
            eclaireur_bonus=0.1,
            espion_bonus=0.7,
        )

        score -= self._revisiting_count(move, 0.5)   

        score *= confidence

        return score
    
    def prior_evaluate_difficult_move(self, move):
        """
        Evaluate one candidate move with hard-difficulty priors.

        Args:
            move: Candidate move to score.

        Returns:
            float: Desirability score for the move.
        """
        start_row = self.ai.rows[self.order][0]
        direction = -1 if start_row > 4 else 1

        my_piece, their_piece = self.algo_infoSet.return_pieces(move)

        my_val = self._piece_value(my_piece)
        their_val = self._piece_value(their_piece)

        confidence = (
            1.0
            if their_piece is not None and their_piece.revealed
            else self.confidence_by_level[2]
        )

        score = self._common_priors(
            move,
            my_piece,
            their_piece,
            my_val,
            their_val,
            eclaireur_bonus=0.15,
            espion_bonus=0.9,
        )

        if their_piece is not None and their_piece.type == PieceType.Drapeau:
            return 1.5 * confidence

        if their_piece is not None and their_piece.type == PieceType.Bombe:
            if my_piece.type == PieceType.Demineur:
                score += 0.7
            else:
                score -= 0.6

        diff = my_val - their_val

        if diff > 0:
            score += 0.6 * (diff / 10)
        elif diff < 0:
            score -= 0.5 * (-diff / 10)

        if their_piece is None or not their_piece.revealed:
            score += 0.1

            if my_val >= 7:
                score -= 0.25

        score += 0.05 * direction * (move.moveTo[1] - move.moveFrom[1])

        score -= self._revisiting_count(move, 0.8)

        score *= confidence

        return score
    
    def _extract_features_heuristics(self):
        """
        Compute heuristic features from the current rollout board state.

        Returns:
            dict: Named feature values used by heuristic evaluation.
        """
        my_pieces = self.algo_infoSet.board_state.get_pieces(self.order)
        opp_pieces = self.algo_infoSet.board_state.get_pieces(1 - self.order)

        features = {}

        features["material"] = (
            sum(p.type.score for p in my_pieces.values())
            - sum(p.type.score for p in opp_pieces.values())
        )

        features["mobility"] = (
            len(self.algo_infoSet.get_all_possible_moves(self.order))
            - len(self.algo_infoSet.get_all_possible_moves(1 - self.order))
        )

        features["flag"] = -self.algo_infoSet.closest_piece_to_flag()

        features["info"] = self.score_revealed_opponent_pieces

        features["trades"] = self.lost_combats

        features["opp_confidence_material"] = sum(
            -p.type.score * (1.0 if p.revealed else self.confidence_by_level[self.difficulty])
            for p in opp_pieces.values()
        )

        features["reveal_bonus"] = sum(
            p.type.score * 2
            for p in opp_pieces.values()
            if p.mcts_revealed
        )

        features["self_reveal_penalty"] = sum(
            -p.type.score
            for p in my_pieces.values()
            if p.mcts_revealed
        )

        return features
    
    def _evaluate_heuristics(self, features, weights):
        """
        Combine extracted heuristic features with a difficulty-specific weight map.

        Args:
            features (dict): Feature values to aggregate.
            weights (dict): Per-feature weights to apply.

        Returns:
            float: The weighted heuristic score.
        """
        return sum(
            features[k] * weights.get(k, 0)
            for k in features
        )
    
    def heuristic_evaluation(self, ai_won, opp_won):
        """
        Evaluate the current rollout state from the AI perspective.

        Args:
            ai_won: Truthy when the rollout already ended in an AI win.
            opp_won: Truthy when the rollout already ended in an AI loss.

        Returns:
            float: A terminal bonus or weighted heuristic score.
        """
        if ai_won:
            return 10000
        if opp_won:
            return -10000

        features = self._extract_features_heuristics()

        weights = self.heuristics_weights_by_level[self.difficulty]

        return self._evaluate_heuristics(features, weights)

    def game_over(self):
        """
        Evaluate whether the simulated state is terminal for either side.

        Returns:
            float: Heuristic terminal evaluation from the AI perspective.
        """
        ai_won = 0
        opp_won = 0
        for player in self.players:
            my_pieces = self.algo_infoSet.board_state.get_pieces(player.order)
            opponent_pieces = self.algo_infoSet.board_state.get_pieces(1- player.order)

            ended, _ = self.game_rules.check_player_end_state(player, self.players, self.algo_infoSet.board_state, my_pieces, opponent_pieces, 1)
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
        if self.root_node.children:
            best_child = max(self.root_node.children, key=lambda x: x.win_score)
        else:
            best_child = self.root_node.get_random_child()

        self.ai.last_moves.append(best_child.move)
        return best_child.move
    

        

    
