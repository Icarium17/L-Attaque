import random
from ALGO.infoSet import InfoSet
from ALGO.node import Node
import copy

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
        self.infoSet_main = InfoSet(copy.deepcopy(ai.known_board), ai.order, game_rules)
        self.player_to_move = self.ai.order
        self.players = players

        self.root_node = Node(None, None)
        self.current_node = self.root_node

        self.heuristic_evaluation = {
            0: self.heuristic_evaluation_easy,
            1: self.heuristic_evaluation_medium,
            2: self.heuristic_evaluation_hard
        }
        self.difficulty = self.ai.difficulty

        self.opp_pieces_copy = self.ai.opponent_belief_pieces_left.copy()
        

    def algo(self):
        self.algo_infoSet = InfoSet(copy.deepcopy(self.ai.known_board), self.ai.order, self.game_rules)
        self.algo_infoSet.actualize_belief_pieces(self.opp_pieces_copy)
        self.current_node = self.root_node

        filtered_untried_moves = self.selection()
        if filtered_untried_moves is not None:
            self.expansion(filtered_untried_moves)
            win_score = self.simulation()

        else :
            win_score = self.game_over

        self.backpropagation(win_score)

    
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
            self.heuristic_evaluation[self.difficulty]()
            game_over = self.game_over()
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

    def heuristic_evaluation_easy(self):
        """
        Perform a random move for easy difficulty.
        """
        possible_moves = self.algo_infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            raise ValueError("MCTS : possible_moves is empty")
        move = random.choice(possible_moves)
        self.algo_infoSet.update_infoSet(move)

    def heuristic_evaluation_medium(self):
        """
        Placeholder for a better heuristic for medium difficulty. Currently random.
        """
        self.heuristic_evaluation_easy()

    def heuristic_evaluation_hard(self):
        """
        Placeholder for a perfect heuristic for hard difficulty. Currently random.
        """
        self.heuristic_evaluation_easy()


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
    

        

    
