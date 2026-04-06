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
        x_0, y_0, x_1, y_1 = move.get_params()

        tileFrom = self.tiles[y_0][x_0]
        tileTo = self.tiles[y_1][x_1]

        print(f"Attempting move: {move.moveFrom} -> {move.moveTo}")
        print(f"tileFrom ({x_0},{y_0}) piece: {tileFrom.piece}")
        if tileFrom.piece is None:
            print(f"ERROR: No piece at source tile {x_0},{y_0} for move {move}")
        piece = tileFrom.piece

        tileFrom.piece = None
        tileTo.piece = piece
        if piece is not None:
            piece.position = (move.moveTo)
        else:
            print(f"Move failed: piece is None for move {move}")

    def get_pieces(self, player_order):
        pieces = {}
        for row in self.tiles:
            for tile in row:
                if tile.piece is not None and tile.piece.owner == player_order:
                    pieces[tile.piece.id] = tile.piece
        return pieces
    
    def return_pieces(self):
        list_pieces = []
        for row in self.tiles:
            for tile in row:
                if tile.piece is not None:
                    list_pieces.append(tile.piece.send())

        return list_pieces
    
        def remove_piece(self, tile):
            tile.piece = None



class Tile():
    def __init__(self, id, x, y, state = 0):
        self.id = id
        self.x = x
        self.y = y
        self.state = state
        self.piece = None