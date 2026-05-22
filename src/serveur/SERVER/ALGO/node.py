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
        self.value = 0
        self.children = []
        self.tried_moves = set()
        self.c_param = 1.4
        self.move = move
        self.prior = 0.0

    def get_filtered_untried_moves(self, possible_moves):
        """
        Filter candidate moves to those not yet expanded from this node.

        Args:
            possible_moves (list): All legal moves available from the current state.

        Returns:
            list: Moves that have not yet been recorded in `self.tried_moves`.
        """
        return [move for move in possible_moves if move not in self.tried_moves]


    def select_best_child(self):
        best_score = -float('inf')
        best_child = None

        for child in self.children:
            Q = child.value / child.visit_count
            U = child.prior * math.sqrt(self.visit_count + 1) / (1 + child.visit_count)

            score = Q + self.c_param * U

            if score > best_score:
                best_score = score
                best_child = child

        return best_child
        
    