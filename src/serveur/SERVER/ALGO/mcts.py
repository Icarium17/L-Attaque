import random
from ALGO.infoSet import InfoSet
from ALGO.node import Node
import copy
import time

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

        self.simulation_by_level = {
            0: self.simulation_easy,
            1: self.simulation_medium,
            2: self.simulation_hard
        }
        self.difficulty = self.ai.difficulty

        self._setup(ai)

    def _setup(self, ai):
        self.root_node = Node(None, None)
        self.current_node = self.root_node
        self.previous_move = None

        self.hidden_belief_pieces = self.ai.get_hidden_belief_pieces()
        self.algo_infoSet = None
        self.revealed_opponent_pieces = self.ai.get_revealed_opponent_pieces()
        self.infoSet_main = InfoSet(copy.deepcopy(ai.known_board), ai.order, self.game_rules)
        self.infoSet_main.sync_opponent_knowledge(self.hidden_belief_pieces, self.revealed_opponent_pieces)

        self.rollout_index = 0
        
    def _reset_rollout_state(self):
        self.current_node = self.root_node

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
        algo_start_ns = time.perf_counter_ns()

        step_start_ns = time.perf_counter_ns()
        reset_stats = self._reset_rollout_state()
        reset_ns = time.perf_counter_ns() - step_start_ns
        actualize_stats = reset_stats["actualize_stats"]
        print(
            "[MCTS] Reset rollout state: "
            f"{reset_ns}ns "
            f"(mode={reset_stats['mode']}, "
            f"actualize={reset_stats['actualize_ns']}ns, "
            f"hidden={actualize_stats.get('hidden_belief_pieces', 0)}, "
            f"recursive_calls={actualize_stats.get('recursive_calls', 0)}, "
            f"backtracking={actualize_stats.get('backtracking_ns', 0)}ns, "
            f"completed={actualize_stats.get('assignment_completed', False)}, "
            f"timed_out={actualize_stats.get('timed_out', False)}, "
            f"random_fallback={actualize_stats.get('used_random_fallback', False)})"
        )
        
        step_start_ns = time.perf_counter_ns()
        filtered_untried_moves = self.selection()
        print(f"[MCTS] Selection: {time.perf_counter_ns() - step_start_ns}ns")

        if filtered_untried_moves is not None:
            step_start_ns = time.perf_counter_ns()
            self.expansion(filtered_untried_moves)
            print(f"[MCTS] Expansion: {time.perf_counter_ns() - step_start_ns}ns")

            step_start_ns = time.perf_counter_ns()
            win_score = self.simulation()
            print(f"[MCTS] Simulation: {time.perf_counter_ns() - step_start_ns}ns")

        else:
            print("[MCTS] Expansion: skipped (no untried moves)")
            step_start_ns = time.perf_counter_ns()
            win_score = self.game_over()
            print(f"[MCTS] Game over fallback: {time.perf_counter_ns() - step_start_ns}ns")

        step_start_ns = time.perf_counter_ns()
        self.backpropagation(win_score)
        print(f"[MCTS] Backpropagation: {time.perf_counter_ns() - step_start_ns}ns")
        print(f"[MCTS] Total algo(): {time.perf_counter_ns() - algo_start_ns}ns")

        self.rollout_index += 1

        

    
    def selection(self):
        """
        Traverse the tree from the root, selecting child nodes until a leaf is reached.
        Updates self.current_node to the selected leaf node.
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


    def expansion(self, filtered_untried_moves):
        """
        Expand the current node by adding a new child node if possible.
        Updates self.current_node and self.infoSet if expansion occurs.
        """
        next_move = random.choice(filtered_untried_moves)
        self.algo_infoSet.update_infoSet(next_move)
        self.current_node.tried_moves.add(next_move)


        next_node = Node(self.current_node, next_move)
        self.current_node.children.append(next_node)
        self.current_node = next_node
            

    def simulation(self):
        """
        Simulate a random playout from the current node to a terminal state or step limit.
        Returns the result of the simulation (game outcome).
        """
        simulation_start_ns = time.perf_counter_ns()
        game_over = 0
        s = 0
        while not game_over and s < 25:
            step_start_ns = time.perf_counter_ns()
            self.simulation_by_level[self.difficulty]()
            rollout_step_ns = time.perf_counter_ns() - step_start_ns

            step_start_ns = time.perf_counter_ns()
            game_over = self.game_over() ## TODO : find a way to make it lighter so its not such a bottleneck
            game_over_ns = time.perf_counter_ns() - step_start_ns
            print(
                f"[MCTS] Simulation step {s}: "
                f"rollout={rollout_step_ns}ns, game_over={game_over_ns}ns"
            )
            s += 1

        print(f"[MCTS] Simulation total: {time.perf_counter_ns() - simulation_start_ns}ns")

        return game_over
    

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
        """
        step_start_ns = time.perf_counter_ns()
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        get_moves_ns = time.perf_counter_ns() - step_start_ns
        if len(possible_moves) == 0:
            raise ValueError("MCTS : possible_moves is empty")

        step_start_ns = time.perf_counter_ns()
        move = random.choice(possible_moves)
        choose_move_ns = time.perf_counter_ns() - step_start_ns

        step_start_ns = time.perf_counter_ns()
        self.algo_infoSet.update_infoSet(move)
        update_infoset_ns = time.perf_counter_ns() - step_start_ns
        print(
            "[MCTS] simulation_easy: "
            f"get_moves={get_moves_ns}ns, "
            f"choose_move={choose_move_ns}ns, "
            f"update_infoSet={update_infoset_ns}ns, "
            f"move_count={len(possible_moves)}"
        )

    def simulation_medium(self):
        """
        Placeholder for a better heuristic for medium difficulty. Currently random.
        """
        self.simulation_easy()

    def simulation_hard(self):
        """
        Placeholder for a perfect heuristic for hard difficulty. Currently random.
        """
        self.simulation_easy()

    def heuristic_evaluation_easy(self, move):
        if self.previous_move is not None:
            if move == self.previous_move:
                return 0
            
        return 1

    def heuristic_evaluatin_medium(self, moves):
        pass

    def heuristic_evaluation_hard(self, moves):
        pass

    def prior_evaluation(self, move):
        pass

    def game_over(self):
        """
        Check if the game is over for any player.
        Returns 1 if the game has ended, otherwise 0.
        """
        for player in self.players:
            my_pieces = self.algo_infoSet.board_state.get_pieces(player.order)
            opponent_pieces = self.algo_infoSet.board_state.get_pieces(1- player.order)

            ended, _ = self.game_rules.check_player_end_state(player, self.players, self.algo_infoSet.board_state, my_pieces, opponent_pieces, 1)
            if ended:
                return 1
        return 0

    def get_best_move(self):
        """
        Return the move from the best child of the root node after search.
        """
        if self.root_node.children:
            best_child = max(self.root_node.children, key=lambda x: x.win_score)
        else:
            best_child = self.root_node.get_random_child()
        return best_child.move
    

        

    
