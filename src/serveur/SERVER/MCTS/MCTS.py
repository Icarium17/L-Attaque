import random
from MCTS.infoSet import InfoSet
from MCTS.node import Node

class MCTS:
    def __init__(self, ai, game_rules, players):
        self.ai = ai
        self.infoSet = InfoSet(ai.known_board, ai.player_to_move, game_rules)
        self.game_rules = game_rules
        self.player_to_move = self.ai.player_to_move
        self.players = players

        self.total_iterations = 10
        self.node_0 = Node(None, self.infoSet)
        self.current_node = self.node_0
        self.current_iteration = 0

        self.heuristic_evaluation = {
            0: self.heuristic_evaluation_easy,
            1: self.heuristic_evaluation_medium,
            2: self.heuristic_evaluation_hard
        }
        self.difficulty = self.ai.difficulty


    def algo(self):
        for i in range(self.total_iterations):
            self.current_iteration = i
            self.selection()
            self.expansion()
            win_score = self.simulation()
            self.backpropagation(win_score)
        print(self.node_0.children)

        return self.get_best_child_node()

    def selection(self):
        while True:
            next_node = self.current_node.selection()
            if next_node is not None:
                self.current_node = next_node
            else:
                break

    def expansion(self):
        next_node = self.current_node.expand()
        if next_node is not None:
            self.current_node = next_node
            self.player_to_move = self.current_node.infoSet.player_turn
            self.infoSet = self.current_node.infoSet

    def simulation(self):  
        game_over = 0
        while not game_over:
            self.heuristic_evaluation[self.difficulty]()
            game_over = self.game_over()

        return game_over

    def backpropagation(self, win_score):
        node = self.current_node
        while node is not None:
            node.visit_count += 1
            if node.infoSet.player_turn == self.player_to_move:
                node.win_score += win_score
            else:
                node.win_score -= win_score
            node = node.parent
        

    def heuristic_evaluation_easy(self): ## TODO : right now, entirely random
        possible_moves = self.infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            return 
        self.infoSet.update_infoSet(random.choice(possible_moves))

    def heuristic_evaluation_medium(self):
        # TODO : implement a better heuristic evaluation for the medium difficulty
        self.heuristic_evaluation_easy()

    def heuristic_evaluation_hard(self):
        # TODO : implement a perfect heuristic evaluation for the hard difficulty
        self.heuristic_evaluation_easy()
        

    def game_over(self):
        for player in self.players:
            ended, _ = self.game_rules.check_player_end_state(player, self.players)
            if ended:
                return 1
        return 0
    
    def get_best_child_node(self):
        best_child = max(self.node_0.children, key=lambda x: x.win_score)
        return best_child

    
