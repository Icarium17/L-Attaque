from tile import Tile

class Board():
    def __init__(self):
        self.tiles = [] ## Liste 2D. Il faut faire self.tiles[y][x] pur bien y accéder
        self.size = {
            "original" : (10, 10)
        }
        self.rows = 0
        self.columns = 0

    def initialise_tiles(self, type = "original"):
        self.rows, self.cols = self.size[type]
        self.tiles = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        id_tile = 0
        for i in range(self.rows):
            for j in range(self.cols):
                self.tiles[i][j] = Tile(id_tile, j, i) ## Ajouter le state = 1 pour les tuiles impraticables
                id_tile += 1