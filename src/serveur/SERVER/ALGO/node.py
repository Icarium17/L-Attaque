from copy import copy
import math
import random

class Node:
    """
    Node in the Monte Carlo Tree Search (MCTS) tree.
    Stores game state, statistics, and child nodes.
    """
    def __init__(self, parent, move):
        """
        Initialize a Node.
        Args:
            parent: The parent Node (or None for root).
            move: The move that led to this node (None for root).
        """
        self.parent = parent
        self.visit_count = 0
        self.win_score = 0
        self.children = []
        self.tried_moves = set()
        self.c_param = 1.4
        self.move = move

    def get_filtered_untried_moves(self, possible_moves):
        return [move for move in possible_moves if move not in self.tried_moves]

    
    def UCB1(self):
        """
        Calculate the Upper Confidence Bound (UCB1) value for this node.
        Returns float('inf') if node has not been visited.
        """
        if self.visit_count == 0:
            return float('inf')
        return (self.win_score / self.visit_count) + self.c_param * math.sqrt(2 * math.log(self.parent.visit_count) / self.visit_count)


    def select_best_child(self):
        """
        Select the best child node using UCB1.
        """
        best_score = -float('inf')
        best_child = None
        for child in self.children:
            score = child.UCB1()
            if score > best_score:
                best_score = score
                best_child = child
        return best_child
    
    
    
 
    # def get_random_child(self, filtered_untried_moves):
    #     """
    #     Create and return a new child node for a random untried move.
    #     Returns the new child node, or None if no untried moves remain or move is invalid.
    #     """
    #     if not filtered_untried_moves:
    #         return None
    #     move = random.choice(filtered_untried_moves)
        
    #     return move
    
    
    