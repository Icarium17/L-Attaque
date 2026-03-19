from USERS.player import Player
from GAME.move import Move
from GAME.board import Board

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
        self.last_moves = [] ##liste contenant la liste des derniers moves de chaque joueur, juste
        
    ##Positionnement initial
    def validate_placement(self, player_order, pieces) -> tuple[int, str] :
                
        if len(pieces) != self.max_pieces[self.game_type]:
            if len(pieces) < self.max_pieces[self.game_type]:
                return (0, "Pas assez de pièces")
            else:
                return (0, "Trop de pièces")
            

        ##Ajouter un check que tous les types de pièces sont présents en bon nombre
        
        start, end = self.zones[self.game_type][player_order]        
        valid_rows = range(start, end)

        if not self.check_positions(valid_rows, pieces):
            return (0, "Les pièces ne sont pas positionnées correctement")

        else:
            return (1, "Les pièces sont positionnées correctement")
        
    def check_positions(self, valid_rows, pieces) -> bool:
        for piece in pieces:
            if piece.position[1] not in valid_rows:
                return False
        return True
    

    def validate_move(self, player, move):
        x_0, y_0, x_1, y_1 = move.getParams()

        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)
        
        tileFrom = self.board.tiles[y_0][x_0]
        tileTo = self.board.tiles[y_1][x_1]
       
        piece = tileFrom.piece

        if d_x == 0 and d_y == 0: ## if the mouvement is null
            return (0, "Pas de mouvement")
        
        if piece is None: ## if there`s no piece on the tile the player wants to move
            return (0, "Il n'y a pas de pièce sur cette tuile")
        
        if piece.owner != player.order: ## if a player is trying to move another`s piece
            return (0, "Cette pièce n'appartient pas à ce joueur")
        
        if d_x > 0 and d_y > 0: ## if the move is diagonal
            return (0, "Les pièces ne peuvent pas bouger diagonalement")

        if not (0 <= x_1 < self.board.cols) or not (0 <= y_1 < self.board.rows): ## if the move makes the piece fall off the edge of the battlefield
            return (0, "Piece a été bougée hors du plateau de jeu")
        
        if tileTo.piece and tileTo.piece.owner == player.order : ## if the piece stops on a tile where theres a piece belonging to the same player 
            return (0, "Cette tuile est occuppée par une pièce appartenant à ce joueur")

        if piece.type == "Drapeau" or piece.type == "Bombe": ## if the player is trying to mvoe a bomb or a flag
            if d_x != 0 or d_y != 0:
                return (0, "Cette pièce ne peut pas bouger")
            
        #if not self.check_last_moves(player.order, move): ## if the move is identical to the last 4 moves
        #    return (0, "La même pièce ne peut pas faire le même mouvement plus de 4 fois")
        
        if tileTo.state == 1:
            return (0, "Cette tuile n'est pas praticable")
        
        if piece.type != "Éclaireur": ## is a piece that`s not a scout tries to move more than 1 tile
                if d_x > 1 or d_y > 1:
                    return (0, "Cette pièce ne peut pas bouger d'autant de tuile")
                
        elif d_x > 1 or d_y > 1: ## if the scout jumps over another piece
            if y_0 == y_1:
                step = 1 if x_1 > x_0 else -1
                for x in range(x_0 + step, x_1, step):
                    if self.board.tiles[y_0][x].piece is not None:
                        return (0, "L'Éclaireur ne peut pas sauter par-dessus une pièce")
            
            elif x_0 == x_1:
                step = 1 if y_1 > y_0 else -1
                for y in range(y_0 + step, y_1, step):
                    if self.board.tiles[y][x_0].piece is not None:
                        return (0, "L'Éclaireur ne peut pas sauter par-dessus une pièce")
                
        return (1, "Ce mouvement est légal")
        


    def check_last_moves(self, player_order, move):
        
        last_moves = self.last_moves[player_order]
        if len(last_moves) == 0: ## on the first move, it will always be a legal move
            last_moves.append(move)
            return True
        
        if last_moves[0] == move: ## if the list contains at least 1 move that`s identical to the current move
            if len(last_moves) == 4: ## if there`s already 4 identical moves (this move would be the fifth) = not legal move
                return False
            last_moves.append(move) ## else, append the current move
        
        else: ## if the move(s) in the list arent identical to the current move
            last_moves.clear() ## erases the list and adds the current move instead
            last_moves.append(move)

        return True
    


