from copy import copy
import math
import random

class Node:
    """
    Node in the Monte Carlo Tree Search (MCTS) tree.
    Stores game state, statistics, and child nodes.
    """
    def __init__(self, parent, move, player_turn):
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
        self.player_turn = player_turn

    def get_filtered_untried_moves(self, possible_moves):
        """
        Filter candidate moves to those not yet expanded from this node.

        Args:
            possible_moves (list): All legal moves available from the current state.

        Returns:
            list: Moves that have not yet been recorded in `self.tried_moves`.
        """
        return [move for move in possible_moves if move not in self.tried_moves]


    def select_best_child(self, maximize=True, excluded_children=None):
        """
        Return the best child during tree traversal.

        Child values are stored from the AI's perspective, so tree traversal
        maximizes on AI turns and minimizes on opponent turns.

        Args:
            maximize: When true, prefer larger average values; otherwise prefer
            smaller average values.
            excluded_children: Optional set of child nodes to ignore for the
            current traversal attempt.

        Returns:
            Node | None: Best child when available, else ``None``.
        """
        if excluded_children is None:
            excluded_children = set()

        best_score = -float('inf')
        best_child = None

        for child in self.children:
            if child in excluded_children:
                continue

            Q = child.value / child.visit_count
            if not maximize:
                Q = -Q
            U = child.prior * math.sqrt(self.visit_count + 1) / (1 + child.visit_count)

            score = Q + self.c_param * U

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def get_best_move_child(self):
        """
        Return the child to play from this node after search.

        Children are ranked first by visit count, then by average value.

        Returns:
            Node | None: The chosen child, or ``None`` when no children exist.
        """
        if not self.children:
            return None

        return max(
            self.children,
            key=lambda child: (
                child.visit_count,
                child.value / child.visit_count if child.visit_count else float('-inf'),
            ),
        )