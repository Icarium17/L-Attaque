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
        self.infoSet = InfoSet(copy.deepcopy(ai.known_board), ai.order, game_rules)
        self.game_rules = game_rules
        self.player_to_move = self.ai.order
        self.players = players

        self.root_node = Node(None, self.infoSet, None)
        self.current_node = self.root_node

        self.heuristic_evaluation = {
            0: self.heuristic_evaluation_easy,
            1: self.heuristic_evaluation_medium,
            2: self.heuristic_evaluation_hard
        }
        self.difficulty = self.ai.difficulty


    def algo(self):
        """
        Run one iteration of the MCTS algorithm: selection, expansion, simulation, and backpropagation.
        """
        self.root_node.infoSet.board_state = copy.deepcopy(self.ai.known_board)
        self.root_node.infoSet.actualize_belief_pieces(self.ai.opponent_pieces_left.copy())
        self.current_node = self.root_node
        
        self.selection()
        self.expansion()

        win_score = self.simulation()
        self.backpropagation(win_score)
    

    def selection(self):
        """
        Traverse the tree from the root, selecting child nodes until a leaf is reached.
        Updates self.current_node to the selected leaf node.
        """
        while True:
            next_node = self.current_node.selection()
            if next_node is not None:
                self.current_node = next_node
            else:
                break

    # def selection(self):
    #     while self.current_node.untried_moves == []:
    #         self.current_node = max(
    #             self.current_node.children,
    #             key=lambda c: c.ucb_score()
    #         )
        

    def expansion(self):
        """
        Expand the current node by adding a new child node if possible.
        Updates self.current_node and self.infoSet if expansion occurs.
        """
        next_node = self.current_node.expand()
        if next_node is not None:
            self.current_node = next_node
            
        self.infoSet = copy.deepcopy(self.current_node.infoSet)
            

    def simulation(self):
        """
        Simulate a random playout from the current node to a terminal state or step limit.
        Returns the result of the simulation (game outcome).
        """
        game_over = 0
        s = 0
        while not game_over:
            self.heuristic_evaluation[self.difficulty]()
            game_over = self.game_over()
            s += 1


        return game_over
    
    # def simulation(self):
    #     world = copy.deepcopy(self.root_node.infoSet.board_state)

    #     # 🔥 sample hidden Stratego setup HERE
    #     world = self.sample_hidden_pieces(world)

    #     current_player = self.root_node.infoSet.player_turn

    #     while not self.is_terminal(world):
    #         moves = self.get_legal_moves(world, current_player)
    #         move = random.choice(moves)
    #         world.move(move)

    #         current_player = 1 - current_player

    #     return self.evaluate(world)

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
        possible_moves = self.infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            raise ValueError("MCTS : possible_moves is empty")
        move = random.choice(possible_moves)
        self.infoSet.update_infoSet(move)

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

    # def heuristic(self, infoSet, move):
    #     board = infoSet.board_state  # ONLY observable

    #     score = 0

    #     if move.attacks_unknown():
    #         score += 1.0

    #     if move.moves_to_center():
    #         score += 0.3

    #     if move.exposes_high_value_piece():
    #         score -= 1.0

    #     return score

    def game_over(self):
        """
        Check if the game is over for any player.
        Returns 1 if the game has ended, otherwise 0.
        """
        for player in self.players:
            my_pieces = self.infoSet.board_state.get_pieces(player.order)
            opponent_pieces = self.infoSet.board_state.get_pieces(1- player.order)

            ended, _ = self.game_rules.check_player_end_state(player, self.players, self.infoSet.board_state, my_pieces, opponent_pieces, 1)
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
    

        

    
