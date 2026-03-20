from GAME.tile import Tile

class Board():
    def __init__(self, game_type = "original"):
        self.tiles = [] ## Liste 2D. Il faut faire self.tiles[y][x] pur bien y accéder
        self.size = {
            "original" : (10, 10)
        }
        self.rows = 0
        self.cols = 0
        self.game_type = game_type

        self.initialise_tiles()

    def initialise_tiles(self, type = "original"):
        self.rows, self.cols = self.size[type]
        self.tiles = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        id_tile = 0
        for i in range(self.rows):
            for j in range(self.cols):
                self.tiles[i][j] = Tile(id_tile, j, i) ## Ajouter le state = 1 pour les tuiles impraticables
                id_tile += 1

    def set_pieces(self, pieces):
        for piece in pieces:
            self.tiles[piece.position[1]][piece.position[0]].piece = piece
    
    def move(self, move):
        x_0, y_0, x_1, y_1 = move.getParams()

        tileFrom = self.tiles[y_0][x_0]
        tileTo = self.tiles[y_1][x_1]

        piece = tileFrom.piece

        tileFrom.piece = None
        tileTo.piece = piece
        piece.position = (move.moveTo)

    

        
