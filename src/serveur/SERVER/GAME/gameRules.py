from USERS.player import Player
from GAME.move import Move
from GAME.board import Board
from GAME.piece import PieceType

class GameRules():
    def __init__(self, board, game_type):
        self.max_pieces = {
            "original" : 40
        }

        self.zones = {
            "original" : ((0, 4), (6, 10))
        }

        self.board = board
        self.game_type = game_type
        self.last_moves = [] ##liste contenant la liste des derniers moves de chaque joueur pour éviter les répétitions de mouvements
        
    ##Positionnement initial
    def validate_placement(self, player_order, pieces) -> tuple[int, str] :
        piece_counts = {ptype: 0 for ptype in PieceType}
        for piece in pieces:
            piece_counts[piece.type] += 1
        for ptype, count in piece_counts.items():
            if count != ptype.count:
                print(ptype, count, ptype.count)
                return (0, f"INVALID_PIECE_COUNT_{ptype}")

        start, end = self.zones[self.game_type][player_order]        
        valid_rows = range(start, end)

        if not self._check_positions(valid_rows, pieces):
            return (0, "INVALID_PIECE_POSITIONS")

        else:
            return (1, "SETUP_SUCCESS")
        
    def _check_positions(self, valid_rows, pieces) -> bool:
        for piece in pieces:
            if piece.position[1] not in valid_rows:
                return False
        return True

    def validate_move(self, player, move) -> tuple[int, str]:
        x_0, y_0, x_1, y_1 = move.getParams()

        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)
        
        tileFrom = self.board.tiles[y_0][x_0]
        tileTo = self.board.tiles[y_1][x_1]
       
        piece = tileFrom.piece

        if d_x == 0 and d_y == 0: ## if the mouvement is null
            return (0, "NO_MOVE")
        
        if piece is None: ## if there`s no piece on the tile the player wants to move
            return (0, "NO_PIECE")
        
        if piece.owner != player.order: ## if a player is trying to move another`s piece
            return (0, "INVALID_OWNER")
        
        if d_x > 0 and d_y > 0: ## if the move is diagonal
            return (0, "INVALID_MOVE_DIAGONAL")

        if not (0 <= x_1 < self.board.cols) or not (0 <= y_1 < self.board.rows): ## if the move makes the piece fall off the edge of the battlefield
            return (0, "OUT_OF_BOUNDS")
        
        if tileTo.piece and tileTo.piece.owner == player.order : ## if the piece stops on a tile where theres a piece belonging to the same player 
            return (0, "TILE_OCCUPIED_BY_OWN_PIECE")

        if piece.type == "Drapeau" or piece.type == "Bombe": ## if the player is trying to mvoe a bomb or a flag
            if d_x != 0 or d_y != 0:
                return (0, "IMMOBILE_PIECE")
            
        if not self._check_last_moves(player.order, move): ## if the move is identical to the last 4 moves
            return (0, "REPEATED_MOVE")
        
        if tileTo.state == 1:
            return (0, "IMPASSABLE_TILE")
        
        if piece.type != "Éclaireur": ## is a piece that`s not a scout tries to move more than 1 tile
                if d_x > 1 or d_y > 1:
                    return (0, "INVALID_MOVE_DISTANCE")
                
        elif d_x > 1 or d_y > 1: ## if the scout jumps over another piece
            if y_0 == y_1:
                step = 1 if x_1 > x_0 else -1
                for x in range(x_0 + step, x_1, step):
                    if self.board.tiles[y_0][x].piece is not None:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_PIECE")
                    
                    if self.board.tiles[y_0][x].state == 1:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_IMPASSABLE_TILE")
            
            elif x_0 == x_1:
                step = 1 if y_1 > y_0 else -1
                for y in range(y_0 + step, y_1, step):
                    if self.board.tiles[y][x_0].piece is not None:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_PIECE")
                
                    if self.board.tiles[y][x_0].state == 1:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_IMPASSABLE_TILE")
        return (1, "MOVE_SUCCESS")

    def _check_last_moves(self, player_order, move) -> bool:
        
        if len(self.last_moves) <= player_order:
            self.last_moves.append([])

        last_moves = self.last_moves[player_order]
        if len(last_moves) == 0: 
            last_moves.append(move)
            return True
        
        if last_moves[0] == move: 
            if len(last_moves) == 4: 
                return False
            last_moves.append(move) 
        
        else: 
            last_moves.clear() 
            last_moves.append(move)

        return True
    
    

    def check_impassable_bomb_wall(self, player, opponent):
        if player.pieces[PieceType.Démineur] == 0:
            if opponent.pieces_left[PieceType.Bombe] > 0:
                x_flag, y_flag = opponent.pieces[PieceType.Drapeau].position
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dx, dy in directions:
                    nx, ny = x_flag + dx, y_flag + dy
                    if 0 <= nx < self.board.cols and 0 <= ny < self.board.rows:
                        tile = self.board.tiles[ny][nx]
                        if not (tile.piece and tile.piece.type == PieceType.Bombe and tile.piece.owner == opponent.order):
                            return False  # Found a non-bomb or empty tile
                return True  # All adjacent tiles are bombs
        return False  
    
    def check_no_mobile_pieces(self, player):
        for type in PieceType:
            if type != PieceType.Drapeau and type != PieceType.Bombe:
                if player.pieces_left[type] > 0:
                    return False
        return True
                               
    def check_flag_captured(self, player):
        if player.pieces_left[PieceType.Drapeau] == 0:
            return True
        return False
    
    def get_remaining_moves(self, player): ## TODO : add a check for _check_last_moves to avoid returning moves that would be rejected for being repetitions of the last moves
        possible_moves = []
        for piece in player.pieces.values():
            if piece.type == "Drapeau" or piece.type == "Bombe":
                continue
            if piece.type != "Éclaireur":
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = piece.position[0] + dx, piece.position[1] + dy
                    move = Move(piece.position, (new_x, new_y))
                    if self.validate_move(player, move)[0] == 1:
                        possible_moves.append(move)
            else:  # piece.type == "Éclaireur"
                for i in range(1, max(self.board.rows, self.board.cols)):
                    for dx, dy in [(0, i), (i, 0), (0, -i), (-i, 0)]:
                        new_x, new_y = piece.position[0] + dx, piece.position[1] + dy
                        move = Move(piece.position, (new_x, new_y))
                        if self.validate_move(player, move)[0] == 1:
                            possible_moves.append(move)

        return possible_moves
    
    def check_remaining_moves(self, player):
        if len(player.pieces) == 0:
            return True

        possible_moves = self.get_remaining_moves(player)
        return len(possible_moves) == 0
    
    ## TODO : Add an actual scoring system
    def calc_score(self, player):
        score = 0
        for piece_type, count in player.pieces_left.items():
            score += piece_type.score * count
            
        return score

    def check_player_end_state(self, player, players):
        if self.check_flag_captured(player):
            return (True, (players[(player.order + 1) % len(players)], player, f"{player.username}'s flag was captured"))
        if not self.check_remaining_moves(player):
            return (True, (players[(player.order + 1) % len(players)], player, f"{player.username} has no moves left"))
        if self.check_impassable_bomb_wall(player, players[(player.order + 1) % len(players)]):
            return (True, (players[(player.order + 1) % len(players)], player, f"{player.username} has no way to win"))
        if not self.check_no_mobile_pieces(player):
            return (True, (players[(player.order + 1) % len(players)], player, f"{player.username} has no mobile pieces left"))
        return (False, None)


