class Board():
    """
    Represents the game board as a 2D grid of tiles.
    Handles initialization, piece placement, movement, and retrieval.
    """
    def __init__(self, game_type = "original"):
        """
        Initialize the board with the specified game type.
        Args:
            game_type: The type of game/board to use (default: "original").
        """
        self.tiles = [] ## Liste 2D. Il faut faire self.tiles[y][x] pour bien y accéder
        self.size = {
            "original" : (10, 10)
        }
        self.rows = 0
        self.cols = 0
        self.game_type = game_type

        self.initialise_tiles()

    def initialise_tiles(self, type = "original"):
        """
        Initialize the board's tiles for the given type.
        Args:
            type: The board type (default: "original").
        """
        self.rows, self.cols = self.size[type]
        self.tiles = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        id_tile = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if i in (4, 5) and j in (2, 3, 6, 7): ##TODO : modify if we have different sized boards
                    state = 1
                else:
                    state = 0
                            
                self.tiles[i][j] = Tile(id_tile, j, i, state)
                id_tile += 1
                

    def set_pieces(self, pieces):
        """
        Place the given pieces on the board according to their positions.
        Args:
            pieces: Iterable of piece objects with a position attribute.
        """
        for piece in pieces:
            self.tiles[piece.position[1]][piece.position[0]].piece = piece
    
    def move(self, move):
        """
        Move a piece from its source tile to its destination tile.
        Args:
            move: Move object with get_params() and moveTo attributes.
        """
        x_0, y_0, x_1, y_1 = move.get_params()

        tileFrom = self.tiles[y_0][x_0]
        tileTo = self.tiles[y_1][x_1]

        if tileFrom.piece is None:
            print(f"ERROR: No piece at source tile {x_0},{y_0} for move {move}")
        piece = tileFrom.piece

        tileFrom.piece = None
        tileTo.piece = piece
        if piece is not None:
            piece.position = (move.moveTo)
        else:
            raise ValueError(f"Move failed: piece is None for move {move}")

    def get_pieces(self, player_order):
        """
        Get all pieces belonging to the specified player.
        Args:
            player_order: The player identifier (e.g., 0 or 1).
        Returns:
            Dictionary of piece_id: piece for the player.
        """
        pieces = {}
        for row in self.tiles:
            for tile in row:
                if tile.piece is not None and tile.piece.owner == player_order:
                    pieces[tile.piece.id] = tile.piece
        return pieces
    
    def return_pieces(self):
        """
        Return a list of all pieces' data (via their send() method) on the board.
        Returns:
            List of data returned by each piece's send() method.
        """
        list_pieces = []
        for row in self.tiles:
            for tile in row:
                if tile.piece is not None:
                    list_pieces.append(tile.piece.send())

        return list_pieces

    def _find_piece_tile(self, piece, position=None):
        if position is not None:
            x, y = position
            if 0 <= x < self.cols and 0 <= y < self.rows:
                tile = self.tiles[y][x]
                if tile.piece is piece or (
                    tile.piece is not None
                    and tile.piece.id == piece.id
                    and tile.piece.owner == piece.owner
                ):
                    return tile

        for row in self.tiles:
            for tile in row:
                if tile.piece is piece or (
                    tile.piece is not None
                    and tile.piece.id == piece.id
                    and tile.piece.owner == piece.owner
                ):
                    return tile

        return None
    
    def remove_piece(self, piece, player=None):
        """
        Remove the piece from the given tile and from the player's pieces dict if provided.
        Args:
            piece: The piece object to remove.
            player: (optional) The player object whose pieces dict should be updated.
        """
        tile = self._find_piece_tile(piece, piece.position)
        if tile:
            print(piece.type, tile.x, tile.y)
        else:
            print("no tile found")

        if tile is not None:
            tile.piece = None

    def move_post_combat(self, piece, y, x, source_position=None):
        # Remove any existing instance of this piece from the board
        for row in self.tiles:
            for tile in row:
                if tile.piece and tile.piece.id == piece.id and tile.piece.owner == piece.owner:
                    tile.piece = None

        print("move_post_combat", x, y)
        print("piece", piece)

        destination_tile = self.tiles[y][x]
        destination_tile.piece = piece

        piece.position = (x, y)

class Tile():
    """
    Represents a single tile on the board, with position, state, and an optional piece.
    """
    def __init__(self, id, x, y, state):
        """
        Initialize a Tile.
        Args:
            id: Unique identifier for the tile.
            x: X-coordinate (column).
            y: Y-coordinate (row).
            state: State of the tile (e.g., 0 for normal, 1 for special).
        """
        self.id = id
        self.x = x
        self.y = y
        self.state = state
        self.piece = None
    
    def get_distance(self, tileTo):
        return abs(self.x - tileTo.x) + abs(self.y - tileTo.y)