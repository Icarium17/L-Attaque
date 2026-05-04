from USERS.player import Player
from GAME.move import Move
from GAME.board import Board
from GAME.piece import PieceType

class GameRules():
    """
    Encapsulate setup, movement, combat, scoring, and end-state rules for a game.

    This class centralizes the rule checks used by the live game, AI search,
    and end-state evaluation. It validates setup and moves, resolves combat,
    tracks repeated-move restrictions, and exposes helpers for checking whether
    a position is effectively lost.
    """

    def __init__(self, game_type):
        """
        Initialize a GameRules instance for the given game type.

        Args:
            game_type (str): The ruleset or board variant to use.
        """
        self.max_pieces = {
            "original" : 40
        }

        self.zones = {
            "original" : ((6, 10), (0, 4))
        }

        ##self.board = board
        self.game_type = game_type
        self.last_moves = [] ##liste contenant la liste des derniers moves de chaque joueur pour éviter les répétitions de mouvements
        
    ##Positionnement initial
    def validate_placement(self, player_order, pieces) -> tuple[int, str] :
        """
        Validate a player's initial placement.

        This checks both the required number of each piece type and whether all
        pieces are inside the allowed setup rows for that player.

        Args:
            player_order (int): The player's board-side index.
            pieces (list): The placed pieces to validate.

        Returns:
            tuple[int, str]: A success flag and a status code describing the result.
        """
        piece_counts = {ptype: 0 for ptype in PieceType}
        for piece in pieces:
            piece_counts[piece.type] += 1
        for ptype, count in piece_counts.items():
            if count != ptype.count:
                return (0, f"INVALID_PIECE_COUNT_{ptype}")

        start, end = self.zones[self.game_type][player_order]        
        valid_rows = range(start, end)

        if not self._check_positions(valid_rows, pieces):
            return (0, "INVALID_PIECE_POSITIONS")

        else:
            return (1, "SETUP_SUCCESS")
        
    def _check_positions(self, valid_rows, pieces) -> bool:
        """
        Check whether every piece is inside the allowed setup rows.

        Args:
            valid_rows (range): The rows the player is allowed to use.
            pieces (list): The pieces to inspect.

        Returns:
            bool: True if every piece is in a valid row, otherwise False.
        """
        for piece in pieces:
            if piece.position[1] not in valid_rows:
                return False
        return True

    def validate_move(self, player_order, move, board, update_history=True) -> tuple[int, str]:
        """
        Validate a move against the current board and rule set.

        The validation covers ownership, bounds, diagonal movement, blocked
        terrain, repeated moves, immobile pieces, and special scout movement.

        Args:
            player_order (int): The player attempting the move.
            move (Move): The move to validate.
            board (Board): The board state to validate against.
            update_history (bool): Whether repeated-move tracking should be updated.

        Returns:
            tuple[int, str]: A success flag and a status code describing the result.
        """
        x_0, y_0, x_1, y_1 = move.get_params()

        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)

        if d_x == 0 and d_y == 0: ## if the mouvement is null
            return (0, "NO_MOVE")
        
        if not (0 <= x_1 < board.cols) or not (0 <= y_1 < board.rows): ## if the move makes the piece fall off the edge of the battlefield
            return (0, "OUT_OF_BOUNDS")
        
        tileFrom = board.tiles[y_0][x_0]
        tileTo = board.tiles[y_1][x_1]
       
        piece = tileFrom.piece

        
        if piece is None: ## if there`s no piece on the tile the player wants to move
            return (0, "NO_PIECE")
        
        if piece.owner != player_order: ## if a player is trying to move another`s piece
            return (0, "INVALID_OWNER")
        
        if d_x > 0 and d_y > 0: ## if the move is diagonal
            return (0, "INVALID_MOVE_DIAGONAL")
        
        if tileTo.piece and tileTo.piece.owner == player_order : ## if the piece stops on a tile where theres a piece belonging to the same player 
            return (0, "TILE_OCCUPIED_BY_OWN_PIECE")

        if piece.type == PieceType.Drapeau or piece.type == PieceType.Bombe: ## if the player is trying to mvoe a bomb or a flag
            if d_x != 0 or d_y != 0:
                return (0, "IMMOBILE_PIECE")
            
        if not self._check_last_moves(player_order, move, update_history): ## if the move is identical to the last 4 moves
            return (0, "REPEATED_MOVE")
        
        if tileTo.state == 1:
            return (0, "IMPASSABLE_TILE")
        
        if piece.type != PieceType.Eclaireur: ## is a piece that`s not a scout tries to move more than 1 tile
                if d_x > 1 or d_y > 1:
                    return (0, "INVALID_MOVE_DISTANCE")
                
        elif d_x > 1 or d_y > 1: ## if the scout jumps over another piece
            if y_0 == y_1:
                step = 1 if x_1 > x_0 else -1
                for x in range(x_0 + step, x_1, step):
                    if board.tiles[y_0][x].piece is not None:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_PIECE")
                    
                    if board.tiles[y_0][x].state == 1:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_IMPASSABLE_TILE")
            
            elif x_0 == x_1:
                step = 1 if y_1 > y_0 else -1
                for y in range(y_0 + step, y_1, step):
                    if board.tiles[y][x_0].piece is not None:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_PIECE")
                
                    if board.tiles[y][x_0].state == 1:
                        return (0, "SCOUT_CANNOT_JUMP_OVER_IMPASSABLE_TILE")
        return (1, "MOVE_SUCCESS")
    
    def combat(self, attacker, defender):
        """
        Resolve combat between an attacking piece and a defending piece.

        Special Stratego-style rules such as bombs, flags, and spies are handled
        before falling back to the standard power comparison.

        Args:
            attacker (Piece): The attacking piece.
            defender (Piece): The defending piece.

        Returns:
            Piece or None: The winning piece, or None when both pieces are eliminated.
        """
        at = attacker.type
        dt = defender.type

        # Bomb first
        if dt == PieceType.Bombe:
            return attacker if at == PieceType.Demineur else defender

        # Flag
        if dt == PieceType.Drapeau:
            return attacker

        # Spy special case: Espion attacks Marechal
        if at == PieceType.Espion and dt == PieceType.Marechal:
            return attacker

        # Spy loses otherwise (unless both are Espion)
        if at == PieceType.Espion and dt != PieceType.Espion:
            return defender
        if dt == PieceType.Espion and at != PieceType.Espion:
            return attacker

        # Power comparison (includes Espion vs Espion, which is a draw)
        ap = at.power
        dp = dt.power

        if ap == dp:
            return None
        return attacker if ap > dp else defender

    def _check_last_moves(self, player_order, move, update_history=True) -> bool:
        """
        Check whether a move violates the repeated-move restriction.

        When history tracking is enabled, this method also records or resets the
        recent move sequence for the player.

        Args:
            player_order (int): The player whose move history is checked.
            move (Move): The move to test.
            update_history (bool): Whether to mutate the stored history.

        Returns:
            bool: True if the move is allowed, otherwise False.
        """
        if len(self.last_moves) <= player_order:
            if not update_history:
                return True
            while len(self.last_moves) <= player_order:
                self.last_moves.append([])

        last_moves = self.last_moves[player_order]
        if len(last_moves) == 0: 
            if update_history:
                last_moves.append(move)
            return True
        
        if last_moves[-1] == move: 
            if len(last_moves) == 4: 
                return False
            if update_history:
                last_moves.append(move) 
        
        else: 
            if update_history:
                last_moves.clear() 
                last_moves.append(move)

        return True

    def get_piece_counts(self, pieces=None, counts=None):
        """
        Return a per-piece-type count map for a position.

        This helper reuses a cached count map when one is already available,
        otherwise it builds the counts from the provided pieces.

        Args:
            pieces (dict, optional): Mapping of piece ids to piece objects.
            counts (dict, optional): Precomputed count map to reuse.

        Returns:
            dict: A mapping from PieceType to the number of remaining pieces.
        """
        if counts is not None:
            return counts

        piece_counts = {piece_type: 0 for piece_type in PieceType}
        if pieces is None:
            return piece_counts

        for piece in pieces.values():
            if piece.type is not None:
                piece_counts[piece.type] += 1

        return piece_counts

    def get_flag_position(self, pieces=None, flag_position=None):
        """
        Return the flag position for a position.

        This helper prefers a cached flag position when one is available and
        falls back to scanning the provided pieces when necessary.

        Args:
            pieces (dict, optional): Mapping of piece ids to piece objects.
            flag_position (tuple, optional): Cached flag position to reuse.

        Returns:
            tuple or None: The flag coordinates, or None if no flag is present.
        """
        if flag_position is not None:
            return flag_position

        if pieces is None:
            return None

        for piece in pieces.values():
            if piece.type == PieceType.Drapeau:
                return piece.position

        return None

    def check_impassable_bomb_wall(self, my_pieces, opponent_pieces, opponent_order, board, my_piece_counts=None, opponent_piece_counts=None, opponent_flag_position=None):
        """
        Detect whether the opponent flag is sealed behind an impassable bomb wall.

        The condition is considered true when the current player has no miners,
        the opponent still has bombs, and the opponent flag is surrounded on all
        orthogonal sides by opponent bombs.

        Args:
            my_pieces (dict): The current player's pieces.
            opponent_pieces (dict): The opponent's pieces.
            opponent_order (int): The opponent's player index.
            board (Board): The board state to inspect.
            my_piece_counts (dict, optional): Cached counts for the current player.
            opponent_piece_counts (dict, optional): Cached counts for the opponent.
            opponent_flag_position (tuple, optional): Cached opponent flag position.

        Returns:
            bool: True if the bomb-wall condition is met, otherwise False.
        """
        my_piece_counts = self.get_piece_counts(my_pieces, my_piece_counts)
        opponent_piece_counts = self.get_piece_counts(opponent_pieces, opponent_piece_counts)
        opponent_flag_position = self.get_flag_position(opponent_pieces, opponent_flag_position)

        demineur_count = my_piece_counts[PieceType.Demineur]
        bomb_count = opponent_piece_counts[PieceType.Bombe]
        if demineur_count == 0:
            if bomb_count > 0 and opponent_flag_position is not None:
                x_flag, y_flag = opponent_flag_position
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dx, dy in directions:
                    nx, ny = x_flag + dx, y_flag + dy
                    if 0 <= nx < board.cols and 0 <= ny < board.rows:
                        tile = board.tiles[ny][nx]
                        if not (tile.piece and tile.piece.type == PieceType.Bombe and tile.piece.owner == opponent_order):
                            return False  # Found a non-bomb or empty tile
                return True  # All adjacent tiles are bombs
        return False
    
    def check_no_mobile_pieces(self, my_pieces=None, piece_counts=None):
        """
        Check whether a player has any mobile pieces left.

        Args:
            my_pieces (dict, optional): Mapping of piece ids to piece objects.
            piece_counts (dict, optional): Cached count map for the same position.

        Returns:
            bool: True if only bombs and the flag remain, otherwise False.
        """
        piece_counts = self.get_piece_counts(my_pieces, piece_counts)
        mobile_pieces = sum(
            count for piece_type, count in piece_counts.items()
            if piece_type not in (PieceType.Drapeau, PieceType.Bombe)
        )
        return mobile_pieces == 0
                               
    def check_flag_captured(self, pieces=None, piece_counts=None):
        """
        Check whether the flag is missing from a position.

        Args:
            pieces (dict, optional): Mapping of piece ids to piece objects.
            piece_counts (dict, optional): Cached count map for the same position.

        Returns:
            bool: True if no flag remains, otherwise False.
        """
        piece_counts = self.get_piece_counts(pieces, piece_counts)
        flag_captured = piece_counts[PieceType.Drapeau] == 0
        return flag_captured

    def has_remaining_moves(self, player_order, pieces, board):
        """
        Check whether at least one legal move exists for the player.

        This is the fast path used by end-state checks. It stops as soon as it
        finds a legal move instead of enumerating the full move list.

        Args:
            player_order (int): The player whose mobility is being tested.
            pieces (dict): Mapping of piece ids to piece objects.
            board (Board): The board state to inspect.

        Returns:
            bool: True if at least one legal move exists, otherwise False.
        """
        if not pieces:
            return False

        tiles = board.tiles
        rows = board.rows
        cols = board.cols
        check_last = self._check_last_moves

        directions = ((0, 1), (1, 0), (0, -1), (-1, 0))

        for piece in pieces.values():
            if piece.type == PieceType.Drapeau or piece.type == PieceType.Bombe:
                continue

            start_x, start_y = piece.position

            if piece.type == PieceType.Eclaireur:
                for dx, dy in directions:
                    next_x = start_x + dx
                    next_y = start_y + dy

                    while 0 <= next_x < cols and 0 <= next_y < rows:
                        tile = tiles[next_y][next_x]
                        piece_on_tile = tile.piece

                        if tile.state == 1 or (piece_on_tile and piece_on_tile.owner == player_order):
                            break

                        if check_last(player_order, (start_x, start_y, next_x, next_y), update_history=False):
                            return True

                        if piece_on_tile:
                            break

                        next_x += dx
                        next_y += dy

                continue

            for dx, dy in directions:
                next_x = start_x + dx
                next_y = start_y + dy

                if not (0 <= next_x < cols and 0 <= next_y < rows):
                    continue

                tile = tiles[next_y][next_x]
                piece_on_tile = tile.piece

                if tile.state == 1 or (piece_on_tile and piece_on_tile.owner == player_order):
                    continue

                if check_last(player_order, (start_x, start_y, next_x, next_y), update_history=False):
                    return True

        return False
    
    def get_remaining_moves(self, pieces, player_order, board, reason = 0):
        """
        Enumerate legal moves for a position, returning only valid moves.

        Args:
            pieces (dict): Mapping of piece ids to piece objects.
            player_order (int): The player whose moves are being generated.
            board (Board): The board state to inspect.
            reason (int): Optional mode flag used by existing callers.

        Returns:
            list: A list of legal moves.
        """
        possible_moves = []
        DIRECTIONS = [(0,1), (1,0), (0,-1), (-1,0)]
        rows, cols = board.rows, board.cols

        for piece in pieces.values():
            if piece.type in (PieceType.Drapeau, PieceType.Bombe):
                continue
            x, y = piece.position
            if piece.type != PieceType.Eclaireur:
                for dx, dy in DIRECTIONS:
                    new_x, new_y = x + dx, y + dy
                    # Pre-filter: out of bounds
                    if not (0 <= new_x < cols and 0 <= new_y < rows):
                        continue
                    target = board.tiles[new_y][new_x]
                    # Pre-filter: impassable tile or own piece
                    if target.state == 1 or (target.piece is not None and target.piece.owner == piece.owner):
                        continue
                    move = Move((x, y), (new_x, new_y))
                    # Call validate_move for final check
                    valid, _ = self.validate_move(player_order, move, board, update_history=False)
                    if valid:
                        possible_moves.append(move)
            else:
                for dx, dy in DIRECTIONS:
                    new_x, new_y = x + dx, y + dy
                    while 0 <= new_x < cols and 0 <= new_y < rows:
                        target = board.tiles[new_y][new_x]
                        # Pre-filter: impassable tile or own piece
                        if target.state == 1 or (target.piece is not None and target.piece.owner == piece.owner):
                            break
                        move = Move((x, y), (new_x, new_y))
                        valid, _ = self.validate_move(player_order, move, board, update_history=False)
                        if valid:
                            possible_moves.append(move)
                        # Stop if there's a piece (can't go further)
                        if target.piece is not None:
                            break
                        new_x += dx
                        new_y += dy
        return possible_moves
    
    def check_remaining_moves(self, player_order, pieces, board = None, reason = 0):
        """
        Check whether a player still has legal moves.

        Args:
            player_order (int): The player whose mobility is being tested.
            pieces (dict): Mapping of piece ids to piece objects.
            board (Board, optional): The board state to inspect.
            reason (int): Optional mode flag used by existing callers.

        Returns:
            bool: True if at least one legal move remains, otherwise False.
        """
        if len(pieces) == 0:
            return False

        if reason == 1:
            return self.has_remaining_moves(player_order, pieces, board)

        possible_moves = self.get_remaining_moves(pieces, player_order, board, reason)
        return len(possible_moves) != 0
    
    ## TODO : Add an actual scoring system
    def calc_score(self, player):
        """
        Compute a player's score from the remaining pieces.

        Args:
            player (Player): The player whose score should be computed.

        Returns:
            int: The total score contributed by the remaining piece counts.
        """
        score = 0
        for piece_type, count in self.get_piece_counts(counts=player.pieces_left).items():
            score += piece_type.score * count
            
        return score
    
    def calc_score_surrender(self):
        return PieceType.Drapeau.score
        


    def check_player_end_state(self, player, players, board, my_pieces=None, opponent_pieces = None, reason = 0):
        """
        Evaluate whether a player has reached a losing end state.

        The method checks, in order, whether the player's flag is gone, whether
        only immobile pieces remain, whether no legal moves are available, and
        whether the opponent flag is unreachable behind a bomb wall.

        Args:
            player (Player): The player being evaluated.
            players (list): The full player list for winner/loser resolution.
            board (Board): The board state to inspect.
            my_pieces (dict, optional): Override piece mapping for the player.
            opponent_pieces (dict, optional): Override piece mapping for the opponent.
            reason (int): Optional mode flag used by existing callers.

        Returns:
            tuple[bool, tuple | None]: Whether the game is over for the player and,
            if so, the winner/loser/reason payload.
        """
        player_order = player.order
        my_pieces = my_pieces if my_pieces is not None else player.pieces
        opponent_pieces = opponent_pieces if opponent_pieces is not None else players[1 - player_order].pieces
        my_end_state_cache = player.end_state_cache if my_pieces is player.pieces else None
        my_piece_counts = my_end_state_cache["piece_counts"] if my_end_state_cache is not None else None
        opponent = players[1 - player_order]
        opponent_end_state_cache = opponent.end_state_cache if opponent_pieces is opponent.pieces else None
        opponent_piece_counts = opponent_end_state_cache["piece_counts"] if opponent_end_state_cache is not None else None
        opponent_flag_position = opponent_end_state_cache["flag_position"] if opponent_end_state_cache is not None else None

        if self.check_flag_captured(my_pieces, my_piece_counts):
            return (True, (players[(player_order + 1) % len(players)], player, f"{player.username}'s flag was captured"))

        if self.check_no_mobile_pieces(my_pieces, my_piece_counts):
            return (True, (players[(player_order + 1) % len(players)], player, f"{player.username} has no mobile pieces left"))
        
        if not self.check_remaining_moves(player_order, my_pieces, board, reason):
            return (True, (players[(player_order + 1) % len(players)], player, f"{player.username} has no moves left"))
        
        if self.check_impassable_bomb_wall(my_pieces, opponent_pieces, (1-player_order), board, my_piece_counts, opponent_piece_counts, opponent_flag_position):
            return (True, (players[(player_order + 1) % len(players)], player, f"{player.username} has no way to win"))

        return (False, None)


