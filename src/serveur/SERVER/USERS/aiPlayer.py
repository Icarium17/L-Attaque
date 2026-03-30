import random

from USERS.player import Player
from GAME.piece import Piece
from MCTS import MCTS

class AIPlayer(Player):
    def __init__(self, user_instance, order, difficulty, time_remaining = (1*15)):
        super().__init__(user_instance, order, time_remaining)
        self.difficulty = difficulty
        self.player_to_move = 0
        self.generate_pieces = {
            0: self.generate_piece_list_easy, ## easy difficulty : random setup
            1: self.generate_piece_list_medium, ## medium difficulty : TODO : implement a better setup for the medium difficulty
            2 : self.generate_piece_list_hard ## hard difficulty : TODO : implement a perfect setup for the hard difficulty
        }

        self.placement_strategy = [
            self.random,
            self.spread_out_bomb_clusters_flag,
            self.spread_out_bomb_clusters,
            self.spread_out_bombs,
            self.single_bomb_cluster,
            self.bomb_side,
            self.front_line_flag,
            self.front_line_flag_lake,
            self.diagonal_bombs,
            self.front_line_bombs,
            self.x_bomb_flag,
            self.bottle_neck
        ]

        self.game_rules = None
        self.players = None

    def initialize_game(self):
        return super().initialize_game()

    def generate_piece_list_easy(self):
        return self.random()
    
    def generate_piece_list_medium(self):
        # TODO : implement a better setup for the medium difficulty
        return self.generate_piece_list_easy()
    
    def generate_piece_list_hard(self):
        # TODO : implement a perfect setup for the hard difficulty
        return self.generate_piece_list_easy()
    
    def set_up_random_pieces(self, rows):
        """
        Returns a list of 40 Piece objects for a player.
        player_order: 0 for player 1, 1 for player 2
        starting_row: the row where the player's pieces start (e.g., 0 or 6)
        """
        pieces = []
        piece_types = self.generate_pieces[self.difficulty]()

        idx = 0
        for row in range(rows[0], rows[1]):
            for col in range(10):
                if idx < 40:
                    pieces.append(Piece(idx, piece_types[idx], (col, row), self))
                    idx += 1
        return pieces
    
    def move(self):
        mcts = MCTS(self, self.game_rules, self.players)
        move = mcts.get_best_move()
        return move
    
    ##Setup strategies
    def random(self):
        piece_types = [
            piece_type
            for piece_type, count in self.pieces_left.items()
            for _ in range(count)
        ]
        random.shuffle(piece_types)
        return piece_types

    def spread_out_bomb_clusters_flag(self):
        pass

    def spread_out_bomb_clusters(self):
        pass

    def spread_out_bombs(self):
        pass

    def single_bomb_cluster(self):
        pass

    def bomb_side(self):
        pass

    def front_line_flag(self):
        pass

    def front_line_flag_lake(self):
        pass

    def diagonal_bombs(self):
        pass

    def front_line_bombs(self):
        pass

    def x_bomb_flag(self):
        pass

    def bottle_neck(self):
        pass

