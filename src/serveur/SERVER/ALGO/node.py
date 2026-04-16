from copy import copy
import math
import random

class Node:
    """
    Node in the Monte Carlo Tree Search (MCTS) tree.
    Stores game state, statistics, and child nodes.
    """
    def __init__(self, parent, infoSet, move):
        """
        Initialize a Node.
        Args:
            parent: The parent Node (or None for root).
            infoSet: The InfoSet representing the game state at this node.
            move: The move that led to this node (None for root).
        """
        self.parent = parent
        self.visit_count = 0
        self.win_score = 0
        self.children = []
        self.infoSet = infoSet
        self.untried_moves = self.infoSet.get_all_possible_moves()
        self.c_param = 1.4
        self.move = move

    ##Proposition:
    # class Node:
    #     def __init__(self, parent, infoSet, move):
    #         self.parent = parent
    #         self.infoSet = infoSet   # ONLY observable state
    #         self.move = move

    #         self.children = []
    #         self.untried_moves = infoSet.get_all_possible_moves()

    #         self.visit_count = 0
    #         self.win_score = 0

    #         self.P = {}  # priors per action

    def is_fully_expanded(self):
        """
        Return True if all possible moves have been tried from this node.
        """
        return len(self.untried_moves) == 0
    
    def UCB1(self):
        """
        Calculate the Upper Confidence Bound (UCB1) value for this node.
        Returns float('inf') if node has not been visited.
        """
        if self.visit_count == 0:
            return float('inf')
        return (self.win_score / self.visit_count) + self.c_param * math.sqrt(2 * math.log(self.parent.visit_count) / self.visit_count)


    # def ucb_score(self):
    #     if self.visit_count == 0:
    #         return float('inf')

    #     exploit = self.win_score / self.visit_count

    #     explore = self.c_param * self.P.get(self.move, 0) * (
    #         (self.parent.visit_count ** 0.5) / (1 + self.visit_count)
    #     )

    # return exploit + explore
    def selection(self):
        """
        Select the best child node using UCB1, or return None if untried moves remain.
        """
        if len(self.untried_moves) > 0:
            return None
        best_score = -float('inf')
        best_child = None
        for child in self.children:
            score = child.UCB1()
            if score > best_score:
                best_score = score
                best_child = child
        return best_child
    
    def expand(self):
        """
        Expand the node by creating a new child for an untried move.
        Returns the new child node, or None if fully expanded.
        """
        if len(self.untried_moves) == 0:
            return None
        return self.get_random_child()
    
    # def expand(self):
    #     if not self.untried_moves:
    #         return None

    #     move = self.untried_moves.pop()

    #     # ONLY observable update
    #     new_obs = copy.deepcopy(self.infoSet.board_state)
    #     new_obs.move(move)

    #     new_infoSet = InfoSet(
    #         new_obs,
    #         1 - self.infoSet.player_turn,
    #         self.infoSet.game_rules
    #     )

    #     child = Node(self, new_infoSet, move)

    #     # 🔥 P(s,a) computed HERE
    #     child.P[move] = self.heuristic(new_infoSet, move)

    #     self.children.append(child)
    #     return child
    
    def get_random_child(self):
        """
        Create and return a new child node for a random untried move.
        Returns the new child node, or None if no untried moves remain or move is invalid.
        """
        if not self.untried_moves:
            return None
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        new_infoSet = self.infoSet.new_infoSet(move)
        if new_infoSet is not None:
            child_node = Node(self, new_infoSet, move)
            self.children.append(child_node)
            return child_node
        return None
    
    
    