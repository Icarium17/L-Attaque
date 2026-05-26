import itertools
import random
import time

from USERS.player import Player
from GAME.piece import Piece, PieceType
from ALGO.mcts import MCTS


class AIPlayer(Player):
    """
    Represents an AI-controlled player with setup-generation and move-selection logic.

    This class owns the high-level gameplay entry points for the AI, including setup selection
    by difficulty and move choice during the game. Setup construction is delegated to helper
    setup classes so the game-facing AI logic stays separate from board-placement details.
    """
    def __init__(self, user_instance, order, difficulty, score = 0, time_remaining = (60*20)):
        """
        Initialize an AIPlayer.

        Args:
            user_instance: The base user/player object to copy state from.
            order: The player order on the board.
            difficulty: The AI difficulty level.
            time_remaining: Remaining clock time for the player.
        """
        super().__init__(user_instance, order, score, time_remaining)
        self.difficulty = difficulty
        self.player_to_move = 0

        self.rows = {
            0: (6, 10), 
            1: (0, 4) 
        }

        self.move_timers = { ## TODO : tinker with the times, this doesnt look right
            0:6,
            1:6,
            2:6
        }

        self.game_rules = None
        self.players = None

        self.exclude_types = set()
        self.setup_library = AISetupLibrary(self)
        self.setup = self.setup_library.full_builders

    def initialize_game(self):
        """
        Initialize the AI player for a new game.

        Returns:
            The initialized player state from the parent Player implementation.
        """
        return super().initialize_game()
    
    def setup_pieces(self):
        """
        Build and return the starting setup for the current difficulty.

        Returns:
            list: List of Piece objects representing the AI starting setup.
        """
        return self.setup[self.difficulty]()
    
    def choose_move(self, search_snapshot):
        """
        Select a move for the AI by running MCTS for a detached snapshot.

        Returns:
            The move selected by the MCTS search.
        """
        iteration_nb = 0
        mcts = MCTS(search_snapshot)
        move_time = search_snapshot.move_time
        start = time.time()

        while time.time() - start < move_time:
            mcts.algo()
            iteration_nb += 1

        elapsed = time.time() - start
        root_visit_summary = mcts.get_root_visit_summary()
        print(
            "MCTS root visits: "
            + (" | ".join(root_visit_summary) if root_visit_summary else "no expanded root children")
        )
        move = mcts.get_best_move()
        iterations_per_second = iteration_nb / elapsed if elapsed > 0 else 0
        average_phase_times_ms = mcts.get_average_phase_times_ms()
        phase_summary = ", ".join(
            f"{phase}_avg_ms={duration:.3f}"
            for phase, duration in average_phase_times_ms.items()
        )
        # print(
        #     "AI debug: "
        #     f"difficulty={search_snapshot.difficulty}, "
        #     f"budget={move_time:.2f}s, "
        #     f"elapsed={elapsed:.2f}s, "
        #     f"initial_possible_moves={mcts.initial_possible_moves}, "
        #     f"iterations={iteration_nb}, "
        #     f"iter_per_sec={iterations_per_second:.2f}, "
        #     f"move={move}, "
        #     f"{phase_summary}"
        # )
        return move


class AISetupBuilder:
    """
    Builds concrete AI piece setups and setup motifs for a specific AI player.

    This class contains the low-level placement logic used to create partial motifs and full
    board setups. It mutates the owning AI player's exclude_types state as pieces are reserved
    so the remaining fill logic can avoid duplicating already-placed piece types.
    """
    def __init__(self, ai_player):
        """
        Initialize an AISetupBuilder.

        Args:
            ai_player: The AIPlayer instance whose setup state is being built.
        """
        self.ai_player = ai_player

    def _player_rows(self):
        return self.ai_player.rows[self.ai_player.order]

    def _is_top_side(self):
        row_start, _ = self._player_rows()
        return row_start == 0

    def _front_row_range(self):
        row_start, row_end = self._player_rows()
        if self._is_top_side():
            return (row_end - 2, row_end)
        return (row_start, row_start + 2)

    def _front_rows(self):
        row_start, row_end = self._player_rows()
        if self._is_top_side():
            return [row_end - 1, row_end - 2]
        return [row_start, row_start + 1]

    def _back_rows(self):
        row_start, row_end = self._player_rows()
        if self._is_top_side():
            return [row_start + 1, row_start]
        return [row_end - 2, row_end - 1]

    def generate_pieces(self, piece_types, pieces=None):
        """
        Fill the remaining setup rows with the provided piece types.

        Args:
            piece_types (list): Ordered list of remaining piece types to place.
            pieces (list): Optional list of pre-placed Piece objects.

        Returns:
            list: Full list of Piece objects after filling empty setup squares.
        """
        if pieces is None:
            pieces = []

        used_positions = {piece.position for piece in pieces}
        rows = self.ai_player.rows[self.ai_player.order]

        piece_index = 0
        board_index = len(pieces)
        for row in range(rows[0], rows[1]):
            for col in range(10):
                if board_index < 40:
                    pos = (col, row)
                    if pos in used_positions:
                        continue
                    pieces.append(Piece(board_index, piece_types[piece_index], pos, self.ai_player.order))
                    board_index += 1
                    piece_index += 1
        return pieces

    def generate_rest_of_types(self):
        """
        Generate the remaining piece types not excluded by already-placed motifs.

        Returns:
            list: Shuffled list of remaining PieceType values to place.
        """
        return self.generate_remaining_types()

    def generate_remaining_types(self, pieces=None):
        """
        Generate the remaining piece types after accounting for already-placed pieces.

        Args:
            pieces (list): Optional list of pre-placed Piece objects.

        Returns:
            list: Shuffled list of remaining PieceType values to place.
        """
        if pieces is None:
            pieces_types = [
                piece_type
                for piece_type, count in self.ai_player.pieces_left.items()
                for _ in range(count)
                if piece_type not in self.ai_player.exclude_types
            ]
        else:
            placed_counts = {piece_type: 0 for piece_type in PieceType}
            for piece in pieces:
                if piece.type is not None:
                    placed_counts[piece.type] += 1

            pieces_types = []
            for piece_type, count in self.ai_player.pieces_left.items():
                remaining = count - placed_counts[piece_type]
                if remaining < 0:
                    raise ValueError(f"Too many pre-placed pieces of type {piece_type.name}")
                pieces_types.extend([piece_type] * remaining)

        random.shuffle(pieces_types)
        return pieces_types

    def compose_motifs(self, motifs):
        """
        Compose multiple motif callables into one partial setup.

        Later motifs only contribute pieces that fit on free squares and do not exceed the
        allowed inventory for each piece type.

        Args:
            motifs (list): Ordered list of motif callables.

        Returns:
            list: Combined list of pre-placed Piece objects.
        """
        pieces = []
        used_positions = set()
        placed_counts = {piece_type: 0 for piece_type in PieceType}

        for motif in motifs:
            for piece in motif():
                if piece.position in used_positions:
                    continue
                if piece.type is not None and placed_counts[piece.type] >= piece.type.count:
                    continue

                pieces.append(Piece(len(pieces), piece.type, piece.position, self.ai_player.order))
                used_positions.add(piece.position)
                if piece.type is not None:
                    placed_counts[piece.type] += 1

        return pieces

    def spread_out_bombs(self):
        """
        Create a bomb motif with bombs spread across many clusters.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        return self._bomb_clusters(6, min_dist=2)

    def single_bomb_cluster(self):
        """
        Create a bomb motif with a single bomb cluster.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        return self._bomb_clusters(1)

    def spread_out_bomb_clusters(self):
        """
        Create a bomb motif with bombs distributed across two clusters.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        return self._bomb_clusters(2)

    def bomb_side(self):
        """
        Create a bomb motif concentrated on a random side band of the board.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        start = random.randint(0, 7)
        nums = (start, min(9, start + 3))
        return self._bomb_clusters(6, range_cols=nums, min_dist=1)

    def x_bomb(self):
        """
        Create an X-shaped bomb motif around a central position.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        pieces, _, _ = self._x_bomb_positions()
        return pieces

    def diagonal_bombs(self, *, nb_bombes=PieceType.Bombe.count, pivot=None):
        """
        Create a diagonal bomb motif anchored at a back-corner pivot.

        Args:
            nb_bombes (int): Number of bombs to place using the motif before random fill.
            pivot (tuple): Optional pivot coordinate to anchor the motif.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        pieces = []
        piece_id = 0
        row_start, row_end = self.ai_player.rows[self.ai_player.order]
        all_rows = list(range(row_start, row_end))
        all_cols = list(range(10))
        used_pos = set()
        if pivot is None:
            back_row = row_end - 1 if self.ai_player.order == 0 else row_start
            pivot = random.choice([(0, back_row), (9, back_row)])

        delta_pos = None

        match pivot:
            case (0, 0):
                delta_pos = [(1, 0), (0, 1), (3, 0), (2, 1), (1, 2), (0, 3)]
            case (9, 0):
                delta_pos = [(-1, 0), (0, 1), (-3, 0), (-2, 1), (-1, 2), (0, 3)]
            case (0, 9):
                delta_pos = [(1, 0), (0, -1), (3, 0), (2, -1), (1, -2), (0, -3)]
            case (9, 9):
                delta_pos = [(-1, 0), (0, -1), (-3, 0), (-2, -1), (-1, -2), (0, -3)]

        if delta_pos is None:
            raise ValueError(f"Invalid pivot: {pivot}")

        for index in range(nb_bombes):
            dx, dy = delta_pos[index]
            x = pivot[0] + dx
            y = pivot[1] + dy
            used_pos.add((x, y))

        for _ in range(PieceType.Bombe.count - nb_bombes):
            possible = [
                (col, row)
                for col in all_cols
                for row in all_rows
                if (col, row) not in used_pos
            ]

            final_pos = random.choice(possible)
            used_pos.add(final_pos)

        for pos in used_pos:
            pieces.append(Piece(piece_id, PieceType.Bombe, pos, self.ai_player.order))
            piece_id += 1

        self.ai_player.exclude_types.add(PieceType.Bombe)
        return pieces

    def front_line_bombs(self):
        """
        Create a bomb motif concentrated near the front line.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        return self._bomb_clusters(3, rows=self._front_row_range(), min_dist=2)

    def front_line_flag(self):
        """
        Place the flag using the front-line flag motif.

        Returns:
            list: List containing the pre-placed flag Piece.
        """
        return self.place_flag()

    def safe_flag(self):
        """
        Place the flag using the safer backline flag motif.

        Returns:
            list: List containing the pre-placed flag Piece.
        """
        return self.place_flag("safe")

    def corner_flag(self):
        """
        Place the flag in a back corner.

        Returns:
            list: List containing the pre-placed flag Piece.
        """
        return self.place_flag("corner")

    def place_flag(self, mode="front_line"):
        """
        Place a flag according to the selected flag-placement mode.

        Args:
            mode (str): Flag placement mode.

        Returns:
            list: List containing the pre-placed flag Piece.
        """
        if mode == "front_line":
            cols = [2, 3, 6, 7]
            row = self._front_rows()[0]
            pos = (random.choice(cols), row)
        elif mode == "safe":
            rows = self._back_rows()
            row = random.choices(rows, weights=[1, 3])[0]
            pos = (random.randrange(10), row)
        elif mode == "corner":
            row = self._back_rows()[1]
            pos = (random.choice([0, 9]), row)
        else:
            raise ValueError(f"Unknown flag mode: {mode}")

        self.ai_player.exclude_types.add(PieceType.Drapeau)
        return [Piece(0, PieceType.Drapeau, pos, self.ai_player.order)]

    def scouts_front(self, rows=None):
        """
        Place scouts near the front to create early probing pressure.

        Args:
            rows: Optional row range override for scout placement.

        Returns:
            list: List of pre-placed scout Piece objects.
        """
        piece_id = 0
        pieces = []
        if rows is None:
            target_rows = self._front_rows()
        else:
            target_rows = list(rows)
        columns = random.sample(range(10), PieceType.Eclaireur.count)
        for col in columns:
            row = random.choices(target_rows, weights=[3, 1])[0]
            pieces.append(Piece(piece_id, PieceType.Eclaireur, (col, row), self.ai_player.order))
            piece_id += 1

        self.ai_player.exclude_types.add(PieceType.Eclaireur)
        return pieces

    def spread_out_bomb_clusters_flag(self):
        """
        Create a spread bomb-cluster motif with an adjacent flag placement.

        Returns:
            list: List of pre-placed bomb and flag Piece objects.
        """
        pieces = self.spread_out_bomb_clusters()

        bomb_piece = random.choice(pieces)
        bomb_pos = bomb_piece.position
        adjacent = [
            (bomb_pos[0] + dx, bomb_pos[1] + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]

        used_positions = {piece.position for piece in pieces}
        rows = self.ai_player.rows[self.ai_player.order]
        valid_adjacent = [
            pos
            for pos in adjacent
            if 0 <= pos[0] < 10 and rows[0] <= pos[1] < rows[1] and pos not in used_positions
        ]

        if valid_adjacent:
            flag_pos = random.choice(valid_adjacent)
            pieces.append(Piece(len(pieces), PieceType.Drapeau, flag_pos, self.ai_player.order))
            self.ai_player.exclude_types.add(PieceType.Drapeau)

        return pieces

    def bottle_neck_lakes(self):
        """
        Create a setup motif that emphasizes lake bottlenecks.

        Returns:
            list: List of pre-placed Piece objects for the motif.
        """
        return self._bottle_necks()

    def strong_center(self):
        """
        Create a setup motif that emphasizes stronger central control.

        Returns:
            list: List of pre-placed Piece objects for the motif.
        """
        row_start, _ = self._player_rows()
        rows = (row_start + 1, row_start + 2)
        cols = [(index, index + 1) for index in range(0, 10, 2)]
        return self._bottle_necks(row=rows, cols=cols)

    def x_bomb_flag(self):
        """
        Create an X-shaped bomb motif with a nearby flag placement.

        Returns:
            list: List of pre-placed bomb and flag Piece objects.
        """
        pieces, used_pos, center_pos = self._x_bomb_positions()

        cx, cy = center_pos
        row_start, row_end = self.ai_player.rows[self.ai_player.order]
        possible = [
            (x, y)
            for x in range(cx - 1, cx + 2)
            for y in range(cy - 1, cy + 2)
            if (x, y) not in used_pos and 0 <= x < 10 and row_start <= y < row_end
        ]

        piece_id = len(pieces)
        pos = random.choice(possible)
        pieces.append(Piece(piece_id, PieceType.Drapeau, pos, self.ai_player.order))
        self.ai_player.exclude_types.add(PieceType.Drapeau)
        return pieces

    def _x_bomb_positions(self):
        """
        Build the underlying X-bomb positions used by x_bomb and x_bomb_flag.

        Returns:
            tuple: Tuple containing placed bomb pieces, used positions, and the center position.
        """
        pieces = []
        piece_id = 0
        used_pos = set()
        row_start, row_end = self.ai_player.rows[self.ai_player.order]
        all_rows = list(range(row_start, row_end))
        center_rows = all_rows[1:3]
        all_cols = list(range(10))
        center_cols = all_cols[1:9]

        center_pos = (random.choice(center_cols), random.choice(center_rows))
        used_pos.add(center_pos)

        for dx in (-1, 1):
            for dy in (-1, 1):
                used_pos.add((center_pos[0] + dx, center_pos[1] + dy))

        possible = [
            (col, row)
            for col in all_cols
            for row in all_rows
            if (col, row) not in used_pos
        ]

        final_pos = random.choice(possible)
        used_pos.add(final_pos)

        for pos in used_pos:
            pieces.append(Piece(piece_id, PieceType.Bombe, pos, self.ai_player.order))
            piece_id += 1

        self.ai_player.exclude_types.add(PieceType.Bombe)
        return pieces, used_pos, center_pos

    def _bomb_clusters(self, cluster_nb, *, rows=None, range_cols=(0, 9), min_dist=3):
        """
        Create clustered bomb placements under spacing constraints.

        Args:
            cluster_nb (int): Number of cluster centers to create.
            rows: Optional row range override for placement.
            range_cols (tuple): Inclusive column range for cluster centers.
            min_dist (int): Minimum Manhattan distance between cluster centers.

        Returns:
            list: List of pre-placed bomb Piece objects.
        """
        pieces = []

        if rows is None:
            rows = self.ai_player.rows[self.ai_player.order]

        used = set()

        def is_far_enough(candidate, centers):
            for center in centers:
                if abs(candidate[0] - center[0]) + abs(candidate[1] - center[1]) < min_dist:
                    return False
            return True

        centers = []
        while len(centers) < cluster_nb:
            row = random.randint(rows[0], rows[1] - 1)
            col = random.randint(range_cols[0], range_cols[1])
            candidate = (col, row)

            if candidate in used:
                continue

            if is_far_enough(candidate, centers):
                centers.append(candidate)
                used.add(candidate)

        bomb_positions = []
        bombs_per_cluster = (PieceType.Bombe.count - cluster_nb) // cluster_nb

        for center in centers:
            possible = []
            for dc in range(-2, 3):
                for dr in range(-2, 3):
                    if abs(dc) + abs(dr) > 2:
                        continue

                    col = center[0] + dc
                    row = center[1] + dr

                    if not (0 <= col <= range_cols[1]):
                        continue
                    if not (rows[0] <= row < rows[1]):
                        continue

                    pos = (col, row)
                    if pos == center or pos in used:
                        continue

                    possible.append(pos)

            chosen = random.sample(possible, min(bombs_per_cluster, len(possible)))
            bomb_positions.extend(chosen)
            used.update(chosen)

        piece_id = 0
        for pos in centers + bomb_positions:
            pieces.append(Piece(piece_id, PieceType.Bombe, pos, self.ai_player.order))
            piece_id += 1

        self.ai_player.exclude_types.add(PieceType.Bombe)
        return pieces

    def _bottle_necks(self, *, row=None, cols=None):
        """
        Build a bottleneck-oriented setup motif with mixed strong pieces and bombs.

        Args:
            row: Optional row selection used for emphasized lanes.
            cols: Optional grouped column bands used for bottleneck placement.

        Returns:
            list: List of pre-placed Piece objects for the motif.
        """
        pieces = []
        all_rows = list(range(self.ai_player.rows[self.ai_player.order][0], self.ai_player.rows[self.ai_player.order][1]))
        if row is None:
            row = tuple(self._front_rows())
        all_cols = list(range(10))
        if cols is None:
            cols = [(0, 1), (4, 5), (8, 9)]
        used_pos = set()
        bomb_cluster_count = len(cols) // 2

        excluded = {
            PieceType.Bombe,
            PieceType.Drapeau,
            PieceType.Demineur,
            PieceType.Sergent,
            PieceType.Lieutenant,
        }
        types = [
            piece_type
            for piece_type in PieceType
            if piece_type not in excluded
            for _ in range(piece_type.count)
        ]

        piece_id = 0
        for _ in range(2):
            piece_count = random.randint(2, 3)
            selected_cols = random.choice(cols)
            cols.remove(selected_cols)

            all_pos = list(itertools.product(row, selected_cols))
            pieces_bottleneck = random.sample(types, piece_count)
            for piece_type in pieces_bottleneck:
                pos = all_pos.pop(random.randrange(len(all_pos)))
                used_pos.add(pos)
                pieces.append(Piece(piece_id, piece_type, pos, self.ai_player.order))
                types.remove(piece_type)
                piece_id += 1

        bomb_count = 0
        for _ in range(bomb_cluster_count):
            piece_count = random.randint(2, 3)
            bomb_count += piece_count
            selected_cols = cols.pop()
            all_pos = [(r, col) for r in row for col in selected_cols]

            for _ in range(piece_count):
                pos = all_pos.pop(random.randrange(len(all_pos)))
                used_pos.add(pos)
                pieces.append(Piece(piece_id, PieceType.Bombe, pos, self.ai_player.order))
                piece_id += 1

        all_pos = [(r, c) for r in all_rows for c in all_cols]
        free_pos = [pos for pos in all_pos if pos not in used_pos]

        for piece_type in types:
            pos = free_pos.pop(random.randrange(len(free_pos)))
            pieces.append(Piece(piece_id, piece_type, pos, self.ai_player.order))
            piece_id += 1

        remaining_bombs = max(0, PieceType.Bombe.count - bomb_count)
        for _ in range(remaining_bombs):
            pos = free_pos.pop(random.randrange(len(free_pos)))
            pieces.append(Piece(piece_id, PieceType.Bombe, pos, self.ai_player.order))
            piece_id += 1

        self.ai_player.exclude_types.update([
            PieceType.Marechal,
            PieceType.General,
            PieceType.Colonel,
            PieceType.Major,
            PieceType.Capitaine,
            PieceType.Eclaireur,
            PieceType.Espion,
            PieceType.Bombe,
        ])
        return pieces


class AISetupLibrary:
    """
    Stores setup presets and selects which setup motif to use for a given AI difficulty.

    This class groups setup motifs into broader preset families and exposes the high-level
    setup builders used by AIPlayer. It relies on AISetupBuilder for the concrete placement work.
    """
    def __init__(self, ai_player):
        """
        Initialize an AISetupLibrary.

        Args:
            ai_player: The AIPlayer instance whose setup options are being managed.
        """
        self.ai_player = ai_player
        self.setup_builder = AISetupBuilder(ai_player)
        self.medium_preset_builders = {
            0: [
                self.build_medium_bomb_pressure_setup,
                self.build_medium_frontline_setup,
                self.build_medium_probe_setup,
            ],
            1: [
                self.build_medium_bomb_pressure_setup,
                self.build_medium_backline_setup,
                self.build_medium_probe_setup,
            ],
        }
        self.full_builders = {
            0: self.generate_piece_list_easy,
            1: self.generate_piece_list_medium,
            2: self.generate_piece_list_hard,
        }

    def generate_piece_list_easy(self):
        """
        Generate a easy-difficulty, random setup.

        Returns:
            list: List of Piece objects for the easy setup.
        """
        piece_types = self.setup_builder.generate_remaining_types()
        return self.setup_builder.generate_pieces(piece_types)
    
    def generate_piece_list_medium(self):
        """
        Build a medium setup by selecting a random preset builder for the current player order.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        motif = self.medium_preset_builders.get(self.ai_player.order, self.medium_preset_builders[0])
        return random.choice(motif)()

    def generate_piece_list_hard(self):
        """
        Generate a hard-difficulty setup by combining multiple motifs.

        This method selects several motif functions (e.g., bomb, frontline, probe motifs),
        composes their pre-placed pieces using compose_motifs, and then fills the rest of the board.

        Returns:
            list: List of Piece objects for the hard setup, combining multiple motif strategies.
        """
        motifs = [
            random.choice(self._bomb_pressure_motifs()),
            random.choice(self._frontline_motifs()),
            random.choice(self._probe_motifs())
        ]

        pieces = self.setup_builder.compose_motifs(motifs)
        
        piece_types = self.setup_builder.generate_remaining_types(pieces)
        return self.setup_builder.generate_pieces(piece_types, pieces)

    def _bomb_pressure_motifs(self):
        """
        Return medium motifs focused on bomb pressure and bomb structure.

        Returns:
            list: List of callable bomb-pressure motifs.
        """
        return [
            self.setup_builder.spread_out_bombs,
            self.setup_builder.single_bomb_cluster,
            self.setup_builder.spread_out_bomb_clusters,
            self.setup_builder.bomb_side,
            self.setup_builder.spread_out_bomb_clusters_flag,
            self.setup_builder.x_bomb,
            self.setup_builder.x_bomb_flag,
            self.setup_builder.diagonal_bombs,
        ]

    def _frontline_motifs(self):
        """
        Return medium motifs focused on front-line pressure and forward posture.

        Returns:
            list: List of callable frontline motifs.
        """
        return [
            self.setup_builder.front_line_bombs,
            self.setup_builder.front_line_flag,
            self.setup_builder.place_flag,
            self.setup_builder.scouts_front,
        ]

    def _backline_motifs(self):
        """
        Return medium motifs focused on safer backline flag placements.

        Returns:
            list: List of callable backline motifs.
        """
        return [
            self.setup_builder.safe_flag,
            self.setup_builder.corner_flag,
        ]

    def _probe_motifs(self):
        """
        Return medium motifs focused on probing and early information pressure.

        Returns:
            list: List of callable probe motifs.
        """
        return [
            self.setup_builder.x_bomb,
            self.setup_builder.diagonal_bombs,
        ]

    def build_medium_bomb_pressure_setup(self):
        """
        Build a medium setup by choosing a random bomb-pressure motif.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        return self.build_from_motif(random.choice(self._bomb_pressure_motifs()))

    def build_medium_frontline_setup(self):
        """
        Build a medium setup by choosing a random frontline motif.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        return self.build_from_motif(random.choice(self._frontline_motifs()))

    def build_medium_backline_setup(self):
        """
        Build a medium setup by choosing a random backline motif.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        return self.build_from_motif(random.choice(self._backline_motifs()))

    def build_medium_probe_setup(self):
        """
        Build a medium setup by choosing a random probe motif.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        return self.build_from_motif(random.choice(self._probe_motifs()))

    def build_from_motif(self, motif):
        """
        Build a full setup from a single pre-placement motif.

        Args:
            motif: Callable motif that returns a partial setup.

        Returns:
            list: Full setup as a list of Piece objects.
        """
        self.ai_player.exclude_types.clear()

        if isinstance(motif, (list, tuple)):
            pieces = self.setup_builder.compose_motifs(motif)
        else:
            pieces = motif()

        piece_types = self.setup_builder.generate_remaining_types(pieces)
        return self.setup_builder.generate_pieces(piece_types, pieces)
