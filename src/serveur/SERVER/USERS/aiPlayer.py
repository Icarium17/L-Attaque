import random
import time

from USERS.player import Player
from GAME.piece import Piece, PieceType
from ALGO.mcts import MCTS

class AIPlayer(Player):
    def __init__(self, user_instance, order, difficulty, time_remaining = (60*15)):
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

        self.rows = {
            0: (6, 10), 
            1: (0, 4) 
        }

        self.move_timers = { ## TODO : tinker with the times, this doesnt look right
            0:3,
            1:3,
            2:3
        }

        self.game_rules = None
        self.players = None
        self.set_types = None
        self.last_moves = []

    def initialize_game(self):
        return super().initialize_game()

    def generate_piece_list_easy(self):
        pieces_types = [
            piece_type 
            for piece_type, count in self.pieces_left.items()
            for _ in range(count)
            if piece_type not in self.set_types ## Voir si ça fonctionne
        ]
        return self.random(pieces_types)
    
    def generate_piece_list_medium(self):
        # TODO : implement a better setup for the medium difficulty
        return self.generate_piece_list_easy()
    
    def generate_piece_list_hard(self):
        # TODO : implement a perfect setup for the hard difficulty
        return self.generate_piece_list_easy()
    
    def set_up_random_pieces(self):
        pieces = []
        piece_types = self.generate_pieces[self.difficulty]()
        rows = self.rows[self.order]

        idx = 0
        for row in range(rows[0], rows[1]):
            for col in range(10):
                if idx < 40:
                    pieces.append(Piece(idx, piece_types[idx], (col, row), self.order))
                    idx += 1
        return pieces
    
    def choose_move(self):
        mcts = MCTS(self, self.game_rules, self.players)
        move_time = self.move_timers[self.difficulty]
        start = time.time()

        while time.time() - start < move_time:
            mcts.algo()
            print("choosing")

        move = mcts.get_best_move()
        return move
    
    ##Setup strategies
    def random(self, piece_types = None):
        random.shuffle(piece_types)
        return piece_types

    def spread_out_bomb_clusters_flag(self): ##check if this works
        pass
        
    def spread_out_bomb_clusters(self):
        pieces = []
        rows = self.rows[self.order]
        id = 0

        r1, r2 = random.choices(range(rows[0], rows[1]), k=2)

        col1 = random.randint(0, 9)
        possible = [i for i in range(0, 10) if abs(i - col1) >= 3]
        col2 = random.choice(possible)

        bomb_clusters_centers = [(col1, r1), (col2, r2)]
        bomb_positions = []
        for center in bomb_clusters_centers:
            possible = [
                (c, r)
                for dc in range(-2, 3)
                for dr in range(-2, 3)
                if abs(dc) + abs(dr) <= 2
                and 0 <= (c := center[0] + dc) < 10
                and rows[0] <= (r := center[1] + dr) < rows[1]
            ]
            
            if center in possible:
                possible.remove(center)
            bomb_positions.append(random.sample(possible, min(2, len(possible))))

        for position in bomb_positions:
            pieces.append(Piece(id, PieceType.Bomb, position, self.order))
            id+=1

        self.set_types = PieceType.Bombe

        self.setup_pieces(pieces=pieces)
        
    def setup_pieces(self, pieces = None):
        piece_types = self.generate_pieces[self.difficulty]()
        rows = self.rows[self.order]

        idx = 0
        for row in range(rows[0], rows[1]):
            for col in range(10):
                if idx < 40:
                    pieces.append(Piece(idx, piece_types[idx], (col, row), self.order))
                    idx += 1
        return pieces

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

