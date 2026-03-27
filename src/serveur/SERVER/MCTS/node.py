from copy import copy
import math
import random

class Node:
    def __init__(self, parent, infoSet):
        self.parent = parent
        self.visit_count = 0
        self.win_score = 0
        self.children = []
        self.infoSet = infoSet
        self.untried_moves = self.infoSet.get_all_possible_moves()
        self.c_param = 1.4

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0
    
    def UCB1(self):
        return (self.win_score / self.visit_count) + self.c_param * math.sqrt(2 * math.log(self.parent.visit_count) / self.visit_count)
    
    def selection(self):
        if (len(self.untried_moves) > 0):
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
        if (len(self.untried_moves) == 0):
            return None
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        new_infoSet = self.infoSet.new_infoSet(move)
        child_node = Node(self, new_infoSet)
        self.children.append(child_node)
        return child_node
    