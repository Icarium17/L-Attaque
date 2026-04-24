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
        self.setup = {
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
        self.last_moves = []

        self.exclude_types = set()

    def initialize_game(self):
        return super().initialize_game()
    
    def setup_pieces(self):
        return self.setup[self.difficulty]
    
    def generate_pieces(self, piece_types, pieces = None):
        if pieces is None:
                pieces = []

        used_positions = {p.position for p in pieces}
        rows = self.rows[self.order]

        idx = 0
        for row in range(rows[0], rows[1]):
            for col in range(10):
                if idx < len(piece_types):
                    pos = (col, row)
                    if pos in used_positions:
                        continue  # Skip already-placed positions
                    pieces.append(Piece(idx, piece_types[idx], pos, self.order))
                    idx += 1
        return pieces
    
    def generate_rest_of_types(self):
        pieces_types = [
            piece_type
            for piece_type, count in self.pieces_left.items()
            for _ in range(count)
            if piece_type not in self.exclude_types 
        ]
        return self.random(pieces_types)

    def generate_piece_list_easy(self):
        piece_types = self.generate_rest_of_types()
        return self.generate_pieces(piece_types)
    
    def generate_piece_list_medium(self):
        pieces = self.spread_out_bomb_clusters_flag()
        piece_types = self.generate_rest_of_types()
        return self.generate_pieces(piece_types, pieces)

    def generate_piece_list_hard(self):
        # TODO : implement a perfect setup for the hard difficulty
        return self.generate_piece_list_easy()
    
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
    
    def single_bomb_cluster(self):
        return self.bomb_clusters(1)
    
    def spread_out_bomb_clusters(self):
        return self.bomb_clusters(2)

    def spread_out_bomb_clusters_flag(self): 
        pieces = self.spread_out_bomb_clusters()

        bomb_piece = random.choice(pieces)
        bomb_pos = bomb_piece.position

        adjacent = [
            (bomb_pos[0] + dx, bomb_pos[1] + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]

        used_positions = {p.position for p in pieces}
        rows = self.rows[self.order]
        valid_adjacent = [
            pos for pos in adjacent
            if 0 <= pos[0] < 10 and rows[0] <= pos[1] < rows[1] and pos not in used_positions
        ]

        if valid_adjacent:
            flag_pos = random.choice(valid_adjacent)
            pieces.append(Piece(len(pieces), PieceType.Drapeau, flag_pos, self.order))
            self.exclude_types.add(PieceType.Drapeau)
 
        return pieces
        
    def bomb_clusters(self, cluster_nb, min_dist = 3):
        pieces = []
        rows = self.rows[self.order]

        def is_far_enough(new_center, centers, min_dist=3):
            for c in centers:
                if abs(new_center[0] - c[0]) + abs(new_center[1] - c[1]) < min_dist:
                    return False
            return True

        centers = []
        while len(centers) < cluster_nb:
            row = random.choice(range(rows[0], rows[1]))
            col = random.randint(0, 9)
            candidate = (col, row)
            if all(candidate != c for c in centers) and is_far_enough(candidate, centers, min_dist):
                centers.append(candidate)


        bomb_positions = []
        if cluster_nb < 6:
            id = 0
            for center in centers:
                possible = [
                    (c, r)
                    for dc in range(-2, 3)
                    for dr in range(-2, 3)
                    if abs(dc) + abs(dr) <= 2
                    and 0 <= (c := center[0] + dc) < 10
                    and rows[0] <= (r := center[1] + dr) < rows[1]
                    and (c, r) != center
                ]
                bomb_positions.extend(random.sample(possible, min(2, len(possible))))

        
        for pos in centers + bomb_positions:
            pieces.append(Piece(id, PieceType.Bombe, pos, self.order))
            id += 1

        self.exclude_types = {PieceType.Bombe}
        return pieces
        
    def spread_out_bombs(self):
        self.bomb_clusters(6, 2)

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

