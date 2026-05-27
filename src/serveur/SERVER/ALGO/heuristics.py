from typing import Any

from GAME.piece import PieceType

HEURISTIC_NORMALIZATION_DIVISOR = 75.0

CONFIDENCE_BY_LEVEL = {
    0: 1.0,
    1: 0.5,
    2: 0.75,
}

HEURISTICS_WEIGHTS_BY_LEVEL = {
    0: {
        "material": 1.0,
    },
    1: {
        "material": 1.0,
        "mobility": 0.5,
        "flag": 1.0,
        "info": 1.0,
        "trades": 1.0,
    },
    2: {
        "material": 1.0,
        "mobility": 0.3,
        "flag": 2.0,
        "info": 3.0,
        "trades": 2.0,
        "reveal_bonus": 2.0,
        "self_reveal_penalty": 1.0,
        "revealed_hunt": 1.2,
    },
}


class MCTSHeuristicMixin:
    def _revisiting_count(self, move, weight: float) -> float:
        count = 0
        for prev in self.previous_moves_algo:
            if move == prev:
                count += 1
        return weight * (1 - 0.5 ** count)

    def _resolve_combat(self, attacker, defender) -> str:
        """
        Classify the likely combat outcome between two concrete pieces.

        Args:
            attacker: Attacking piece in the simulated combat.
            defender: Defending piece in the simulated combat.

        Returns:
            str: One of "win", "loss", "draw", "unknown", or "invalid"
            from the AI perspective of the attacker/defender comparison logic.
        """
        if attacker is None or defender is None:
            return "invalid"

        a = attacker.type
        d = defender.type

        if d == PieceType.Drapeau:
            return "win"

        if d == PieceType.Bombe:
            return "win" if a == PieceType.Demineur else "loss"

        if a == PieceType.Espion and d == PieceType.Marechal:
            return "win"

        if a.power is None or d.power is None:
            return "unknown"

        if a.power > d.power:
            return "win"
        elif a.power < d.power:
            return "loss"
        else:
            return "draw"

    def _piece_value(self, piece) -> int:
        """
        Return the heuristic score value of a piece.

        Args:
            piece: Piece to evaluate.

        Returns:
            int: Piece score value, or -1 when no piece is present.
        """
        if piece is None:
            return -1

        return piece.type.score

    def _common_priors(
        self,
        move,
        my_piece,
        their_piece,
        eclaireur_bonus: float = 0.1,
        espion_bonus: float = 0.7,
    ) -> float:
        """
        Compute shared tactical priors used by medium and hard move scoring.
        """
        if my_piece is None:
            return -5.0

        score = 0.0

        if their_piece is not None:
            combat_result = self._resolve_combat(my_piece, their_piece)

            if combat_result == "win":
                score += 0.8
            elif combat_result == "loss":
                score -= 0.8
            else:
                score -= 0.1

            if their_piece.type == PieceType.Drapeau:
                score += 1.5

            if my_piece.type == PieceType.Espion and their_piece.type == PieceType.Marechal:
                score += espion_bonus

        if my_piece.type == PieceType.Eclaireur:
            score += eclaireur_bonus

        x, y = move.moveTo
        center_x, center_y = 4.5, 4.5

        dist_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        score -= 0.03 * dist_to_center

        if x == 0 or x == 9 or y == 0 or y == 9:
            score -= 0.2

        board = self.algo_infoSet.board_state.tiles

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx <= 9 and 0 <= ny <= 9:
                neighbor = board[ny][nx].piece

                if neighbor and neighbor.revealed:
                    neighbor_power = self._piece_value(neighbor)
                    my_power = self._piece_value(my_piece)

                    if my_power < neighbor_power:
                        score -= 0.4

        return score

    def prior_evaluate_medium_move(self, move) -> float:
        """
        Evaluate one candidate move with medium-difficulty priors.
        """
        my_piece, their_piece = self.algo_infoSet.return_pieces(move)

        if my_piece is None:
            return -5.0

        confidence = (
            1.0
            if their_piece is not None and their_piece.revealed
            else self.confidence_by_level[1]
        )

        score = self._common_priors(
            move,
            my_piece,
            their_piece,
            eclaireur_bonus=0.1,
            espion_bonus=0.7,
        )

        score -= self._revisiting_count(move, 0.5)
        score *= confidence

        return score

    def prior_evaluate_difficult_move(self, move) -> float:
        """
        Evaluate one candidate move with hard-difficulty priors.
        """
        start_row = self.rows[self.order][0]
        direction = -1 if start_row > 4 else 1

        my_piece, their_piece = self.algo_infoSet.return_pieces(move)

        if my_piece is None:
            return -5.0

        my_val = self._piece_value(my_piece)
        their_val = self._piece_value(their_piece)

        confidence = (
            1.0
            if their_piece is not None and their_piece.revealed
            else self.confidence_by_level[2]
        )

        score = self._common_priors(
            move,
            my_piece,
            their_piece,
            eclaireur_bonus=0.15,
            espion_bonus=0.9,
        )

        if their_piece is not None and their_piece.type == PieceType.Drapeau:
            return 1.5 * confidence

        if their_piece is not None and their_piece.type == PieceType.Bombe:
            if my_piece.type == PieceType.Demineur:
                score += 0.7
            else:
                score -= 0.6

        diff = my_val - their_val

        if diff > 0:
            score += 0.6 * (diff / 10)
        elif diff < 0:
            score -= 0.5 * (-diff / 10)

        if their_piece is None or not their_piece.revealed:
            score += 0.1

            if my_val >= 7:
                score -= 0.25

        score += 0.05 * direction * (move.moveTo[1] - move.moveFrom[1])

        score -= self._revisiting_count(move, 0.8)

        score *= confidence

        return score

    # ---- Heuristic Features ----

    def _extract_features_heuristics(self) -> dict[str, float]:
        my_pieces = self.algo_infoSet.board_state.get_pieces(self.order)
        opp_pieces = self.algo_infoSet.board_state.get_pieces(1 - self.order)

        return {
            "material": self._material_feature(my_pieces, opp_pieces),
            "mobility": self._mobility_feature(),
            "flag": self._flag_pressure_feature(),
            "info": self.score_revealed_opponent_pieces,
            "trades": self.lost_combats,
            "reveal_bonus": self._reveal_bonus_feature(opp_pieces),
            "self_reveal_penalty": self._self_reveal_penalty_feature(my_pieces),
            "revealed_hunt": self._revealed_high_rank_hunt_bonus(my_pieces, opp_pieces),
        }

    def _material_feature(self, my_pieces, opp_pieces) -> float:
        return (
            sum(p.type.score for p in my_pieces.values())
            - sum(p.type.score for p in opp_pieces.values())
        )

    def _mobility_feature(self) -> float:
        return (
            len(self.algo_infoSet.get_all_possible_moves(self.order))
            - len(self.algo_infoSet.get_all_possible_moves(1 - self.order))
        )

    def _flag_pressure_feature(self) -> float:
        return -self.algo_infoSet.closest_piece_to_flag()

    def _reveal_bonus_feature(self, opp_pieces) -> float:
        return sum(
            p.type.score * 2
            for p in opp_pieces.values()
            if p.mcts_revealed
        )

    def _self_reveal_penalty_feature(self, my_pieces) -> float:
        return sum(
            -p.type.score
            for p in my_pieces.values()
            if p.mcts_revealed
        )

    def _is_piece_known_to_ai(self, piece) -> bool:
        return bool(getattr(piece, "revealed", False) or getattr(piece, "mcts_revealed", False))

    def _known_identity_confidence(self, piece) -> float:
        if getattr(piece, "revealed", False):
            return 1.0
        if getattr(piece, "mcts_revealed", False):
            return self.confidence_by_level.get(self.difficulty, 1.0)
        return 0.0

    def _revealed_high_rank_hunt_bonus(self, my_pieces, opp_pieces) -> float:
        hunt_pairs = {
            PieceType.Marechal: (PieceType.Espion,),
            PieceType.General: (PieceType.Marechal,),
            PieceType.Colonel: (PieceType.General, PieceType.Marechal),
        }

        my_type = {}
        for piece in my_pieces.values():
            if piece.type is None:
                continue
            my_type.setdefault(piece.type, []).append(piece)

        board = self.algo_infoSet.board_state
        tiles = board.tiles

        bonus = 0.0
        for opp_piece in opp_pieces.values():
            if opp_piece.type not in hunt_pairs:
                continue

            target_confidence = self._known_identity_confidence(opp_piece)
            if target_confidence <= 0:
                continue

            counter_types = hunt_pairs[opp_piece.type]
            counters = []
            for counter_type in counter_types:
                counters.extend(my_type.get(counter_type, []))
            if not counters:
                continue

            target_x, target_y = opp_piece.position
            target_tile = tiles[target_y][target_x]

            best_pressure = 0.0
            for counter in counters:
                if counter.type in (PieceType.Drapeau, PieceType.Bombe):
                    continue

                if self._resolve_combat(counter, opp_piece) != "win":
                    continue

                cx, cy = counter.position
                distance = abs(cx - target_x) + abs(cy - target_y)

                if distance == 1:
                    best_pressure = max(best_pressure, 1.0)
                    continue

                same_row = cy == target_y
                same_col = cx == target_x
                if distance != 2 or not (same_row or same_col):
                    continue

                mid_x = (cx + target_x) // 2
                mid_y = (cy + target_y) // 2
                mid_tile = tiles[mid_y][mid_x]

                lane_open = (
                    mid_tile.state != 1
                    and mid_tile.piece is None
                    and target_tile.state != 1
                )
                if lane_open and not self._is_immediate_recapture_risk(mid_x, mid_y, counter):
                    best_pressure = max(best_pressure, 0.5)

            if best_pressure > 0:
                bonus += best_pressure * (opp_piece.type.score / 10.0) * target_confidence

        return bonus

    def _is_immediate_recapture_risk(self, x: int, y: int, defended_piece: Any) -> bool:
        tiles = self.algo_infoSet.board_state.tiles
        rows = len(tiles)
        cols = len(tiles[0]) if rows else 0

        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < cols and 0 <= ny < rows):
                continue

            enemy_tile = tiles[ny][nx]
            enemy_piece = enemy_tile.piece
            if enemy_piece is None:
                continue

            if enemy_piece.owner == self.order:
                continue

            if enemy_piece.type in (PieceType.Bombe, PieceType.Drapeau):
                continue

            if self._resolve_combat(enemy_piece, defended_piece) == "win":
                return True

        return False

    def _evaluate_heuristics(self, features: dict[str, float], weights: dict[str, float]) -> float:
        return sum(
            features[k] * weights.get(k, 0)
            for k in features
        )

    def heuristic_evaluation(self, ai_won, opp_won) -> float:
        if ai_won:
            return 1.0
        if opp_won:
            return -1.0

        features = self._extract_features_heuristics()

        weights = self.heuristics_weights_by_level[self.difficulty]

        raw = self._evaluate_heuristics(features, weights)

        return max(-1.0, min(1.0, raw / HEURISTIC_NORMALIZATION_DIVISOR))
