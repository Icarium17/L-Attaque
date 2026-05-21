from enum import Enum


class PieceType(Enum):
    """
    Enumerate all Stratego piece types with power, count, and score metadata.
    """
    Marechal = (10, 1, 10)
    General = (9, 1, 9)
    Colonel = (8, 2, 8)
    Major = (7, 3, 7)
    Capitaine = (6, 4, 6)
    Lieutenant = (5, 4, 5)
    Sergent = (4, 4, 4)
    Demineur = (3, 5, 3)
    Eclaireur = (2, 8, 2)
    Espion = (None, 1, 1)
    Bombe = (None, 6, 5)
    Drapeau = (-1, 1, 100)

    def __init__(self, power, count, score):
        """
        Store the metadata associated with one piece type.

        Args:
            power: Combat power used by the rules engine.
            count: Number of pieces of this type in a standard setup.
            score: Score contribution used by heuristics and persistence.
        """
        self._power = power
        self._count = count
        self.score = score

    @property
    def power(self):
        """
        Return the combat power of this piece type.

        Returns:
            int | None: Combat power, or `None` for special non-ranked pieces.
        """
        return self._power

    @property
    def count(self):
        """
        Return how many copies of this type exist in a full army.

        Returns:
            int: Standard inventory count for this type.
        """
        return self._count


class Piece():
    """
    Represent one concrete game piece on the board.
    """
    def __init__(self, id, type, position, owner, revealed = True):
        """
        Initialize a concrete piece.

        Args:
            id: Unique identifier for the piece.
            type: Concrete `PieceType` of the piece.
            position: Board coordinate as `(x, y)`.
            owner: Order of the player owning the piece.
            revealed: Whether the piece identity is currently known.
        """
        self.id = id
        self.type = type
        self.position = position
        self.owner = owner 
        self.revealed = revealed
        self.mcts_revealed = False

    def clone(self):
        """
        Create a shallow copy of the piece for board duplication.

        Returns:
            Piece: Cloned piece instance.
        """
        return Piece(self.id, self.type, self.position, self.owner)

    def send(self):
        """
        Serialize the piece into a frontend-friendly dictionary.

        Returns:
            dict: Serializable representation of the piece.
        """
        piece = {
            "id": self.id,
            "type": self.type.name if self.type else None,
            "position": self.position,
            "owner": self.owner
        }
        return piece
    
class BeliefPiece(Piece):
    """
    Represent an opponent piece whose identity is uncertain.
    """
    def __init__(self, id, position, owner):
        """
        Initialize a hidden-information belief piece.

        Args:
            id: Unique identifier for the piece.
            position: Board coordinate as `(x, y)`.
            owner: Player order owning the hidden piece.
        """
        super().__init__(id, None, position, owner, False)
        self.evidence_weights = {}
        self.probabilities = {}
        self.set_probabilities() 

    def clone(self):
        """
        Clone the belief piece and its probability state.

        Returns:
            BeliefPiece: Cloned belief piece instance.
        """
        belief_piece = BeliefPiece(self.id, self.position, self.owner)
        belief_piece.evidence_weights = self.evidence_weights.copy()
        belief_piece.probabilities = self.probabilities.copy()
        return belief_piece
    
    def upgrade(self, type_piece):
        """
        Convert the belief piece into a concrete piece of a chosen type.

        Args:
            type_piece: Concrete type to assign.

        Returns:
            Piece: Concrete piece with the same identity and position.
        """
        piece = Piece(self.id, type_piece, self.position, self.owner)
        return piece
        
    ## At the start, all types are equally compatible, and probabilities follow piece counts
    def set_probabilities(self):
        """
        Initialize uniform evidence weights and count-based prior probabilities.

        Returns:
            None
        """
        total_pieces = sum(piece.count for piece in PieceType)
        for piece in PieceType:
            self.evidence_weights[piece] = 1.0
            self.probabilities[piece] = piece.count / total_pieces

    def normalize(self): #when a piece becomes impossible (when it moves, it cant be a flag...)
        """
        Normalize the current probability distribution in place.

        Returns:
            str | None: Error message when no probability mass remains, otherwise `None`.
        """
        s = sum(self.probabilities.values())
        if s == 0:
            return ("No more ennemy pieces")
        for type in self.probabilities:
            self.probabilities[type] /= s


    def update_probabilities(self, pieces_left):
        """
        Recompute probabilities from evidence weights and remaining inventory.

        Args:
            pieces_left: Remaining counts keyed by `PieceType`.

        Returns:
            None
        """
        for t in self.probabilities:
            self.probabilities[t] = self.evidence_weights[t] * pieces_left[t]

        self.normalize()
    
    def update_probabilities_on_move(self, distance):
        """
        Refine piece-type evidence after observing movement.

        Args:
            distance: Distance traveled by the observed piece.

        Returns:
            None
        """
        # Any movement eliminates immobile pieces
        self.evidence_weights[PieceType.Drapeau] = 0
        self.evidence_weights[PieceType.Bombe] = 0

        # Scout rule (long movement)
        if distance > 1:
            for t in self.evidence_weights:
                if t != PieceType.Eclaireur:
                    self.evidence_weights[t] = 0

    def check_upgrade_bp_to_piece(self):
        """
        Upgrade the belief piece when only one type remains possible.

        Returns:
            Piece | None: Concrete upgraded piece when certainty is reached, else `None`.
        """
        possible_types = [
            piece_type
            for piece_type, probability in self.probabilities.items()
            if probability > 0
        ]

        if len(possible_types) == 1:
            return self.upgrade(possible_types[0])

        return None
    
    def save(self): 
        """
        Serialize the belief piece, including probability metadata.

        Returns:
            dict: Serializable representation including evidence weights and probabilities.
        """
        save = self.send()
        save["evidence_weights"] = {k.name if hasattr(k, 'name') else str(k): v for k, v in self.evidence_weights.items()}
        save["probabilities"] = {k.name if hasattr(k, 'name') else str(k): v for k, v in self.probabilities.items()}
        return save
    
    @staticmethod
    def restore_dict_with_enum_keys(d):
        """
        Convert a dict with string keys (PieceType names) back to PieceType enum keys.

        Args:
            d: Dictionary that may contain serialized enum names as keys.

        Returns:
            dict | Any: Dictionary with restored `PieceType` keys, or the original value.
        """
        if not isinstance(d, dict):
            return d
        restored = {}
        for k, v in d.items():
            try:
                enum_key = PieceType[k]
            except (KeyError, TypeError):
                enum_key = k  # fallback if not a valid PieceType
            restored[enum_key] = v
        return restored

    def restore_belief_data(self, save):
        """
        Restore evidence_weights and probabilities from string-keyed dicts to PieceType-keyed dicts.

        Args:
            save: Serialized belief-piece payload.

        Returns:
            None
        """
        if "evidence_weights" in save:
            self.evidence_weights = self.restore_dict_with_enum_keys(save["evidence_weights"])
        if "probabilities" in save:
            self.probabilities = self.restore_dict_with_enum_keys(save["probabilities"])
