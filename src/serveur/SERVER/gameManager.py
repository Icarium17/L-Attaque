import time
import threading
import json

from GAME.board import Board
from GAME.gameRules import GameRules
from GAME.piece import BeliefPiece, PieceType
from USERS.aiPlayer import AIPlayer

class GameManager():
    """
    Coordinate one live game, including setup, move resolution, timers, and end-state handling.
    """
    def __init__(self, lobbyManager, players, status = None, game_type = "original"):
        """
        Initialize a new GameManager instance.
        Args:
            lobbyManager: The LobbyManager instance managing this game.
            players: List of Player and/or AIPlayer objects.
            status: Optional initial status string.
            game_type: The type of game (default: "original").
        """
        self.lobbyManager = lobbyManager
        self.game_type = game_type
        self.board = Board(self.game_type)
        self.game_rules = GameRules(self.game_type)
        self.players = players 
        self.player_to_move = 0
        self.players_ready = set()
        self.winner = None
        self.loser = None
        self.end_reason = None
        self.status = status if status else ("WAITING" if len(players) == 1 else "PLAYING")
        self.battle = None
        self.timers = None
        self.wait_timer_handle = None
        self.turn_change_timer = None
        self.set_player_boards()
        if len(players) == 2:
            self.timers = PlayerTimer(self.players, [player.time_remaining for player in self.players], self.timer_expired)
        else:
            self.wait_timer()

    @classmethod
    def load(cls, lobbyManager, players, player_to_move, board):
        """
        Load a game from saved state.
        Args:
            lobbyManager: The LobbyManager instance.
            players: List of Player and/or AIPlayer objects.
            player_to_move: The index/order of the player whose turn it is.
            board: List of Piece objects representing the board state.
        Returns:
            GameManager: The loaded game instance.
        """
        
        game = cls(
            lobbyManager,
            players,
            status="PLAYING",
            game_type="original"
        )

        game.board.set_pieces(board)
        game.player_to_move = player_to_move
        game.timers.start(player_to_move)

        return game

        

    def wait_timer(self):
        """
        Start a timer for waiting for a second player to join.
        """
        self.wait_timer_duration = 100
        self.wait_timer_start = time.time()
        self.wait_timer_handle = threading.Timer(self.wait_timer_duration, self.remove_game)
        self.wait_timer_handle.start()

    def cancel_wait_timer(self):
        """
        Cancel the wait timer if it is running.
        """
        if self.wait_timer_handle is not None:
            self.wait_timer_handle.cancel()
            self.wait_timer_handle = None


    def add_second_player(self, player):
        """
        Add a second player to the game and start setup.
        Args:
            player: The Player object to add.
        """
        self.cancel_wait_timer()
        self.players.append(player)
        self.set_player_boards()
        self.timers = PlayerTimer(self.players, [player.time_remaining for player in self.players], self.timer_expired) 
        self.status = "SETTING_UP"
        

    def remove_game(self):
        """
        Remove the game from the lobby if the wait timer expires.
        """
        self.lobbyManager.too_long_wait(self.players[0].key)

    ###### Start and Setup ###### 

    def get_player(self, key):
        """
        Get a player by their session key.
        Args:
            key: The session key to search for.
        Returns:
            Player or AIPlayer object, or None if not found.
        """
        for player in self.players:
            if hasattr(player, "key") and player.key == key:
                return player
            if hasattr(player, "user") and hasattr(player.user, "key") and player.user.key == key:
                return player
        return None
    
    def set_player_boards(self):
        """
        Initialize known boards for all players if not already set.
        """
        for player in self.players:
            if player.known_board is None:
                player.known_board = Board(self.game_type)
                if hasattr(player, "user"):
                    player.user.status = "SETTING_UP"

    def clone_pieces(self, pieces):
        """
        Clone a list of pieces.
        Args:
            pieces: List of Piece objects.
        Returns:
            List of cloned Piece objects.
        """
        return [piece.clone() for piece in pieces]

    def check_valid_setup(self, player_id, pieces) -> str:
        """
        Check if a player's piece setup is valid and update the game state.
        Args:
            player_id: The session key of the player.
            pieces: List of Piece objects to place.
        Returns:
            str: Status message or error.
        """
        player_order = self.get_order(player_id)
        if player_order == -1:
            return ("Le joueur n'est pas valide")
        
        pieces = self.invert_positions_if_needed(player_order, pieces)
        positions = self.game_rules.validate_placement(player_order, pieces)

        if positions[0] == 0:
            return positions
        
        self.board.set_pieces(pieces)
        player_pieces = self.clone_pieces(pieces)
        self.players[player_order].position_pieces(player_pieces)
        self.players[player_order].sync_owned_pieces()
        self.players_ready.add(player_id)
        for player in self.players:
            if isinstance(player, AIPlayer):
                self.setup_ai_player(player.order)
        if len(self.players) == 2 and all(p.key in self.players_ready for p in self.players):
            print("setup")
            self.finish_set_up()
        else:
            self.players[player_order].user.status = "WAITING_FOR_OPPONENT"
        return ("SETUP_SUCCESS")

    def setup_ai_player(self, order):
        """
        Set up the AI player's pieces and state.
        Args:
            order: The order/index of the AI player.
        """
        ai_player = self.players[order]
        ai_pieces = ai_player.setup_pieces()
        self.board.set_pieces(ai_pieces) ##ok
        ai_player.position_pieces(self.clone_pieces(ai_pieces))
        ai_player.sync_owned_pieces()
        self.players_ready.add(ai_player.key)
        ai_player.game_rules = self.game_rules
        ai_player.players = self.players

    def finish_set_up(self):
        """
        Finalize setup for all players and start the game.
        """
        print("setup_called")
        for order, p in enumerate(self.players):
                print("order:", order)
                p_pieces = p.known_board.get_pieces(order)
                self.set_unknowns_pieces(int(order), p_pieces)
        for p in self.players:
            if hasattr(p, "user"):
                p.user.status = "PLAYING"

        self.status = "PLAYING"

        if self.timers:
            self.timers.start(0)


    def set_unknowns_pieces(self, player_order, pieces):
        """
        Set belief pieces for opponents based on unknown pieces.
        Args:
            player_order: The order/index of the player.
            pieces: Dict of Piece objects.
        """
        for opponent in self.players[:player_order] + self.players[player_order + 1:]:
            belief_pieces = []
            for piece in pieces.values():
                belief = BeliefPiece(piece.id, piece.position, player_order)
                belief_pieces.append(belief)

            opponent.position_pieces(belief_pieces)
            opponent.add_belief_pieces(belief_pieces)
        
    def check_board(self):
        """
        Print the current board state for debugging.
        """
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                tile = self.board.tiles[y][x]
                if tile.piece:
                    print(f"Tile ({x}, {y}) has piece owned by player {tile.piece.owner} at position {tile.piece.position}")
                else:
                    print(f"Tile ({x}, {y}) is empty")


    ###### Game Logic ######
    
    def get_order(self, player_id) -> int:
        """
        Get the order/index of a player by their session key.
        Args:
            player_id: The session key.
        Returns:
            int: The player's order, or -1 if not found.
        """
        player_order = next((i for i, obj in enumerate(self.players) if obj.key == player_id), -1)
        return player_order
    
    def make_move(self, player_id, move):
        """
        Make a move for a player if the game is in PLAYING status.
        Args:
            player_id: The session key of the player.
            move: The Move object representing the move.
        Returns:
            Tuple[int, str]: (status, message)
        """
        if self.status == "PLAYING":
            player = self.players[self.get_order(player_id)]
            if player.order == -1:
                return (0, "INVALID_KEY")
            
            if player.order == 1 and not isinstance(player, AIPlayer):
                move.invert()
                
            valid_move = self.game_rules.validate_move(player.order, move, self.board)
            if valid_move[0] == 0:
                return valid_move
            
            player.last_moves.append(move)

            tileFrom = self.board.tiles[move.moveFrom[1]][move.moveFrom[0]]
            pieceFrom = tileFrom.piece
            tileTo = self.board.tiles[move.moveTo[1]][move.moveTo[0]]

            if tileTo.piece and tileTo.piece.owner != player.order:
                self.battle = [pieceFrom.send(), tileTo.piece.send()]
                self.combat(pieceFrom, tileTo.piece, tileTo)
                self.status = "BATTLE"
                self.timers.stop(6)
                self.turn_change_timer = threading.Timer(4, self.change_turn)
                self.turn_change_timer.start()
            else:
                distance = tileFrom.get_distance(tileTo)
                self.board.move(move)
                for player in self.players:
                    if player.order != self.player_to_move:
                        player.update_belief_state_move(tileFrom.x, tileFrom.y, distance) ## TODO : check if this works
                    player.move(move)
                    player.sync_owned_pieces()
                self.change_turn()
                return (1, "MOVE_SUCCESS")
            
        return (0, "BATTLE_HAPPENING")
    
    def change_turn(self):
        """
        Change the turn to the next player, or end the game if finished.
        """
        self.status = "PLAYING"
        if not self.check_end_state(): 
            self.player_to_move = (self.player_to_move + 1) % len(self.players)
            self.timers.switch_player(self.player_to_move)
            player = self.players[self.player_to_move]
            if isinstance(player, AIPlayer):
                threading.Thread(target=self.ai_move_thread, args=(player,), daemon=True).start()

        else:
            print("GAME OVER")

    def ai_move_thread(self, ai_player):
        """
        Threaded function for AI player to make a move.
        Args:
            ai_player: The AIPlayer object.
        """
        ai_player.player_to_move = self.player_to_move
        move = ai_player.choose_move()
        self.make_move(self.player_to_move, move)

    def combat(self, attacker, defender, defender_tile):
        """
        Resolve combat between two pieces and update the board.
        Args:
            attacker: The attacking Piece object.
            defender: The defending Piece object.
            defender_tile: The tile where the defender is located.
        """
        winner = self.game_rules.combat(attacker, defender)
        if winner is None:
            # Draw: both lose
            losers = [attacker, defender]
        elif winner is attacker:
            losers = [defender]
        else:
            losers = [attacker]
        ##Score
        if winner is not None:
            self.players[winner.owner].score += losers[0].type.score

        self.set_boards_post_combat(winner, losers, defender_tile)

    def set_boards_post_combat(self, winner, losers, tileTo):
        """
        Update boards after combat, removing defeated pieces and moving the winner.
        Args:
            winner: The winning Piece object, or None.
            losers: List of defeated Piece objects.
            tileTo: The destination tile.
        """
        for loser in losers:
            for player in self.players:
                player.remove_piece_everywhere(loser)
                player.known_board.remove_piece(loser)
            self.board.remove_piece(loser)

        if winner is not None and winner.type != PieceType.Bombe:
            winner_source_position = winner.position
            for player in self.players:
                player.known_board.remove_piece(winner)
            self.board.remove_piece(winner)
            
            for player in self.players:
                player.known_board.move_post_combat(winner.clone(), tileTo.y, tileTo.x, winner_source_position)
            self.board.move_post_combat(winner, tileTo.y, tileTo.x, winner_source_position)

        for player in self.players:
            if winner is not None and winner.type != PieceType.Bombe:
                player.update_belief_state_winner(winner)
            for loser in losers:
                player.update_belief_state_loser(loser)
            player.sync_owned_pieces()

    def pause(self, my_key):
        """
        Pause or resume the game for a player.
        Args:
            my_key: The session key of the player.
        Returns:
            Tuple[int, str]: (status, message)
        """
        player = self.get_player(my_key)
        opponent = self.players[1 - player.order]
        if not isinstance(opponent, AIPlayer):
            return (0, "CANNOT_PAUSE_VS_PLAYER")
        
        if self.status != "PAUSED":
            self.status = "PAUSED"
            self.timers.stop()
            return (1, "GAME_PAUSED")
        
        else :
            self.status = "PLAYING"
            self.timers.start(player.order)
            return (1, "GAME_RESTARTED") 
        
    def invert_positions_if_needed(self, player_order, pieces):
        """
        Mirror setup coordinates for the second player's board perspective.

        Args:
            player_order: The order/index of the player.
            pieces: List of Piece objects.

        Returns:
            List of Piece objects with updated positions.
        """
        if player_order == 1:
            for piece in pieces:
                x, y = piece.position
                piece.position = (9 - x, 9 - y)
        return pieces
    
    def invert_piece_dicts_y(self, list_pieces):
        """
        Invert the y positions in a list of piece dicts for the second player.
        Args:
            list_pieces: List of piece dicts.
        Returns:
            List of piece dicts with updated positions.
        """
        for piece in list_pieces:
            x, y = piece['position']
            piece['position'] = (9 - x, 9 - y)
        return list_pieces
        
    def get_status(self, player_id):
        """
        Get the current status of a player and the game.
        Args:
            player_id: The session key of the player.
        Returns:
            dict: Status information for the player/game.
        """
        player = self.players[self.get_order(player_id)]
        if player.order == -1:
            return {"status": "INVALID_KEY"} ##TODO : change for the player only
        
        list_pieces = player.known_board.return_pieces()

        if player.order == 1:
            list_pieces = self.invert_piece_dicts_y(list_pieces)

        opponent = self.players[self.get_order(1 - player.order)].user.username

        if opponent is None:
            opponent = ""

        status = {
                "status": self.status, 
                "opponent" : opponent,
                "board": list_pieces,
                "turn": "blue" if self.player_to_move == 0 else "red",
                "order" : player.order}
        
        if self.status != "WAITING":
            times_remaining = [player.time_remaining for player in self.players]
            status["battle"] = None,
            scores = [self.players[0].score, self.players[1].score] 
            
            if self.status == "BATTLE":
                status["battle"] = self.battle ##TODO : à rajouter dans le front end
            
        else:
            elapsed = time.time() - self.wait_timer_start
            time_left = max(0, self.wait_timer_duration - elapsed)
            times_remaining = [time_left, time_left]
            scores = [0, 0]
            status["battle"] = None 

        status["scores"] = scores
        status["time_remaining"] = times_remaining
        return status

    

    ###### End Game ######

    ## TODO : Check the end game conditions after each moves
    def check_end_state(self):
        """
        Check if the game has ended for any player.
        Returns:
            bool: True if the game ended, False otherwise.
        """
        for player in self.players:
            ended, result = self.game_rules.check_player_end_state(player, self.players, self.board)
            if ended:
                self.timers.stop()
                winner, loser, reason = result
                self.declare_winner(winner, loser, reason)
                return True
        return False
            

    def declare_winner(self, winner, loser, reason):
        """
        Declare the winner and loser of the game and end it.
        Args:
            winner: The Player or AIPlayer who won.
            loser: The Player or AIPlayer who lost.
            reason: The reason for the game's end.
        """
        self.winner = winner
        self.loser = loser
        self.end_reason = reason
        self.end_game()

    def end_game(self):
        """
        End the game, update scores, and notify the lobby manager.
        """
        print(f"Game ended! Winner: {self.winner.username}, Loser: {self.loser.username}, Reason: {self.end_reason}")
        for player in self.players:
            player.user.score += self.game_rules.calc_score(player)
        self.lobbyManager.end_game(self.winner, self.loser, self.end_reason)

    def cleanup(self):
        """
        Clean up game resources and timers after the game ends.
        """
        self.cancel_wait_timer()

        if self.turn_change_timer is not None:
            self.turn_change_timer.cancel()
            self.turn_change_timer = None

        if self.timers is not None:
            self.timers.shutdown()
            self.timers = None

        self.players_ready.clear()
        self.players = []
        self.board = None
        self.game_rules = None
        self.battle = None
        self.winner = None
        self.loser = None
        self.end_reason = None

    def timer_expired(self, player):
        """
        Handle timer expiration for a player, declaring the other as winner.
        Args:
            player: The index of the player whose timer expired.
        """
        self.declare_winner(self.players[(player + 1) % len(self.players)], self.players[player], f"{self.players[player].username}'s timer expired")

    def surrender(self, my_key):
        """
        Handle a player surrendering the game.
        Args:
            my_key: The session key of the surrendering player.
        """
        self.status = "SURRENDER"
        self.timers.stop()
        surrenderer = self.get_player(my_key)
        winner = self.players[1 - surrenderer.order]
        print(f"Game surrendered! Winner: {winner.username}, Loser: {surrenderer.username}, Reason: {"Surrender"}")
        winner.score += self.game_rules.calc_score_surrender()
        threading.Timer(10, self.lobbyManager.end_game, args=(winner, surrenderer, "Surrender")).start()

    def save(self, my_key):
        """
        Save the current game state for a player.
        Args:
            my_key: The session key of the player.
        Returns:
            Tuple: (user_id, ai_difficulty, player_to_move, game_state_json)
        """
        player = self.get_player(my_key)
        my_order = player.order

        opponent = self.players[1-my_order]
        
        if not isinstance(opponent, AIPlayer):
            return (0, "CANNOT_PAUSE_VS_PLAYER")
        
        self.status = "SAVING"
        self.timers.stop()
        
        user_id = player.user.account_id
        ai_difficulty = opponent.difficulty
        player_to_move = self.player_to_move

        # Gather all game state into a single dict
        game_state = {
            "player_boards": [player.known_board.save_board() for player in self.players],
            "board": self.board.return_pieces(),
            "scores": [player.score for player in self.players],
            "times": [player.time_remaining for player in self.players],
            "last_moves": [player.last_moves for player in self.players]
        }
        # Serialize to a single JSON string
        game_state_json = json.dumps(game_state)
        return user_id, ai_difficulty, player_to_move, game_state_json
        

    

class PlayerTimer:
    """
    Manages individual timers for each player in a game.
    Handles timing logic, switching between players, and triggers a callback when a player's timer expires.
    Args:
        players: List of Player or AIPlayer objects.
        times: List of initial time values for each player (in seconds).
        timer_expired_callback: Function to call when a player's timer expires.
    """
    def __init__(self, players, times, timer_expired_callback):
        """
        Initialize a PlayerTimer instance.
        Args:
            players: List of Player or AIPlayer objects.
            times: List of initial time values for each player (in seconds).
            timer_expired_callback: Function to call when a player's timer expires.
        """
        self.players = players
        self.times = times  
        self.current_player = 0
        self.delay = 1
        self.running = False
        self.closed = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.timer_expired_callback = timer_expired_callback
        self.last_switch_time = None

    def start(self, player):
        """
        Start the timer for the specified player.
        Args:
            player: The index of the player whose timer to start.
        """
        with self.lock:
            if self.closed:
                return
            self.current_player = player
            self.running = True
            self.last_switch_time = time.time()
            if not self.thread.is_alive():
                self.thread.start()

    def switch_player(self, next_player):
        """
        Switch the timer to the next player, updating time spent.
        Args:
            next_player: The index of the next player.
        """
        with self.lock:
            if self.closed:
                return
            now = time.time()
            if self.running and self.last_switch_time is not None:
                elapsed = now - self.last_switch_time
                self.times[self.current_player] -= elapsed
            self.current_player = next_player
            self.last_switch_time = now

    def stop(self, duration = None):
        """
        Stop the timer for the current player. Optionally resume after a delay.
        Args:
            duration: Optional delay in seconds before resuming the timer.
        """
        def resume_after_delay(player_idx, delay):
            """
            Resume the timer for a player after a fixed delay.

            Args:
                player_idx: Index of the player whose timer should resume.
                delay: Number of seconds to wait before resuming.

            Returns:
                None
            """
            time.sleep(delay)
            self.start(player_idx)

        with self.lock:
            if self.closed:
                return
            if self.running and self.last_switch_time is not None:
                elapsed = time.time() - self.last_switch_time
                self.times[self.current_player] -= elapsed
            self.running = False
            self.last_switch_time = None

            if duration is not None:
                threading.Thread(target=resume_after_delay, args=(self.current_player, duration), daemon=True).start()

    def shutdown(self):
        """
        Shut down the timer and clean up resources.
        """
        with self.lock:
            self.closed = True
            self.running = False
            self.last_switch_time = None
            self.players = []
            self.times = []
            self.timer_expired_callback = None

    def _run(self):
        """
        Internal thread loop to decrement player timers and trigger expiration callback.
        """
        while True:
            time.sleep(self.delay)
            with self.lock:
                if self.closed:
                    return
                if self.running and self.last_switch_time is not None:
                    self.players[self.current_player].time_remaining -= self.delay
                    if self.players[self.current_player].time_remaining <= 0:
                        self.players[self.current_player].time_remaining = 0
                        self.running = False
                        self.timer_expired_callback(self.current_player)
                        self.last_switch_time = None

    def get_times(self):
        """
        Get a copy of the current times for all players.
        Returns:
            List of remaining times for each player.
        """
        with self.lock:
            if self.closed:
                return []
            times_copy = self.times[:]
            if self.running and self.last_switch_time is not None:
                elapsed = time.time() - self.last_switch_time
                times_copy[self.current_player] -= elapsed
                if times_copy[self.current_player] < 0:
                    times_copy[self.current_player] = 0
            return times_copy
    
