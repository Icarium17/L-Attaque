import math
import random


class BeamBeliefSystem:

    # =========================
    # INITIAL BEAM GENERATION
    # =========================
    def assign_types_beam(self, belief_pieces, pieces_left, beam_width=10):
        # Sort once (MRV heuristic)
        belief_pieces = sorted(
            belief_pieces,
            key=lambda bp: sum(
                1 for t in bp.probabilities
                if bp.probabilities[t] > 0 and pieces_left[t] > 0
            )
        )

        # (score, assignment_dict, pieces_left)
        beam = [(0.0, {}, pieces_left.copy())]

        for bp in belief_pieces:
            new_beam = []

            for score, assignment, remaining in beam:
                options = [
                    t for t in bp.probabilities
                    if bp.probabilities[t] > 0 and remaining[t] > 0
                ]

                if not options:
                    continue

                for t in options:
                    new_assignment = assignment.copy()
                    new_remaining = remaining.copy()

                    new_assignment[bp] = t
                    new_remaining[t] -= 1

                    p = bp.probabilities[t]
                    new_score = score + (math.log(p) if p > 0 else -1e9)

                    # small noise for diversity
                    new_score += random.uniform(0, 1e-6)

                    new_beam.append((new_score, new_assignment, new_remaining))

            if not new_beam:
                return None

            new_beam.sort(key=lambda x: x[0], reverse=True)
            beam = new_beam[:beam_width]

        return beam


    # =========================
    # INCREMENTAL UPDATE
    # =========================
    def update_beam(self, beam, belief_pieces, observation, beam_width=10):
        new_beam = []

        for score, assignment, pieces_left in beam:
            valid = True
            new_score = score

            for bp, t in assignment.items():
                if not observation.is_valid(bp, t):
                    valid = False
                    break

                # reweight (optional but useful)
                p = bp.probabilities.get(t, 0)
                if p > 0:
                    new_score += math.log(p)
                else:
                    new_score -= 1e9

            if valid:
                new_beam.append((new_score, assignment.copy(), pieces_left.copy()))

        # If beam collapses → rebuild
        if not new_beam:
            return self.assign_types_beam(belief_pieces, pieces_left, beam_width)

        # Repair incomplete assignments
        new_beam = self._repair_beam(new_beam, belief_pieces, beam_width)

        new_beam.sort(key=lambda x: x[0], reverse=True)
        return new_beam[:beam_width]


    # =========================
    # REPAIR STEP
    # =========================
    def _repair_beam(self, beam, belief_pieces, beam_width):
        repaired = []

        for score, assignment, pieces_left in beam:
            missing = [bp for bp in belief_pieces if bp not in assignment]

            if not missing:
                repaired.append((score, assignment, pieces_left))
                continue

            sub_beam = [(score, assignment.copy(), pieces_left.copy())]

            for bp in missing:
                next_sub = []

                for s, a, remaining in sub_beam:
                    options = [
                        t for t in bp.probabilities
                        if bp.probabilities[t] > 0 and remaining[t] > 0
                    ]

                    if not options:
                        continue

                    for t in options:
                        new_a = a.copy()
                        new_r = remaining.copy()

                        new_a[bp] = t
                        new_r[t] -= 1

                        p = bp.probabilities[t]
                        new_s = s + (math.log(p) if p > 0 else -1e9)

                        next_sub.append((new_s, new_a, new_r))

                if not next_sub:
                    break

                next_sub.sort(key=lambda x: x[0], reverse=True)
                sub_beam = next_sub[:beam_width]

            repaired.extend(sub_beam)

        return repaired


    # =========================
    # SAMPLING FOR MCTS
    # =========================
    def sample_assignment(self, beam):
        scores = [s for s, _, _ in beam]
        assignments = [a for _, a, _ in beam]

        weights = [math.exp(s) for s in scores]
        return random.choices(assignments, weights=weights, k=1)[0]
    


class Observation:
    def is_valid(self, bp, t):
        if bp.revealed:
            return t == bp.true_type

        if bp.has_moved:
            return t not in ("Bomb", "Flag")

        return True
    




# to use

# beam_system = BeamBeliefSystem()
# beam = beam_system.assign_types_beam(belief_pieces, pieces_left, beam_width=20)


# beam = beam_system.update_beam(beam, belief_pieces, observation, beam_width=20)


# assignment = beam_system.sample_assignment(beam)

# def materialize_board(self, assignment):
#     board = copy.deepcopy(self.ai.known_board)

#     for bp, t in assignment.items():
#         x, y = bp.position
#         board.tiles[y][x].piece = Piece(bp.id, t, bp.position, bp.owner)

#     return board

# def algo(self):
#     # sample hidden world from beam
#     beam = self.ai.beam
#     assignment = beam_system.sample_assignment(beam)

#     # build concrete state
#     self.root_node.infoSet.board_state = self.materialize_board(assignment)

#     self.current_node = self.root_node

#     self.selection()
#     self.expansion()
#     win_score = self.simulation()
#     self.backpropagation(win_score)

# but nodes should not have sampled boards