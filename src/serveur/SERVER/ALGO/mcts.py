import random
from ALGO.infoSet import InfoSet
from ALGO.node import Node
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
        self.previous_move = self.ai.last_move

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
        self._reset_rollout_state()
        filtered_untried_moves = self.selection()

        if filtered_untried_moves is not None:
            self.expansion(filtered_untried_moves)

            win_score = self.simulation()

        else:
            win_score = self.game_over()

        self.backpropagation(win_score)

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
        game_over = 0
        s = 0
        while not game_over and s < 25:
            if not self.simulation_by_level[self.difficulty]():
                return game_over

            game_over = self.game_over() ## TODO : find a way to make it lighter so its not such a bottleneck
           
            s += 1

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
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        print(possible_moves)
        if len(possible_moves) == 0:
            return 0

        move = random.choice(possible_moves)
        self.algo_infoSet.update_infoSet(move)

        return 1

    def simulation_medium(self):
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        print(possible_moves)
        if len(possible_moves) == 0:
           return 0
        
        move_priors = []
        for move in possible_moves:
            prior = self.prior_evaluate_medium_move(move)
            move_priors.append((move, prior))

       
        if random.random() < 0.5:
            move = random.choice(possible_moves)
        else:
            max_prior = max(move_priors, key=lambda x: x[1])[1]
            best_moves = [m for m, p in move_priors if p == max_prior]
            move = random.choice(best_moves)

        self.algo_infoSet.update_infoSet(move)

        return 1

    def simulation_hard(self):
        """
        Placeholder for a perfect heuristic for hard difficulty. Currently random.
        """
        return self.simulation_easy()

    def heuristic_evaluation_easy(self, move):
        if self.previous_move is not None:
            if move == self.previous_move:
                return 0
            
        return 1

    def heuristic_evaluation_medium(self, moves):
        pass

    def heuristic_evaluation_hard(self, moves):
        pass

    def prior_evaluate_medium_move(self, move):
        """
        Evaluate a move based on tactical, mobility, information, and strategy priors.
        Returns a score (float/int) representing the move's desirability.
        """
        score = 0
        my_piece, their_piece = self.algo_infoSet.return_pieces(move)

        if their_piece and their_piece.type == PieceType.Drapeau:
            score += 1000000  
        elif their_piece:
            if their_piece.type.value > my_piece.type.value:
                score += 100  
            elif their_piece.type.value < my_piece.type.value:
                score -= 100  
            if their_piece.type.value >= 8:
                score += 50  
            if my_piece.type.value < their_piece.type.value:
                score -= 200  
            else:
                score += 20 
        
        if their_piece and not their_piece.revealed:
            score += 30  
        if my_piece.type == PieceType.Eclaireur and their_piece:
            score += 10  

        if self.previous_move is not None and move == self.previous_move:
            score -= 50  

        print(score)

        return score

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

        self.ai.last_move = best_child.move
        return best_child.move
    

        

    
