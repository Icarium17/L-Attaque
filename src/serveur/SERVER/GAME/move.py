class Move():
    """
    Represent one move between two board coordinates.
    """
    def __init__(self, moveFrom, moveTo):
        """
        Initialize a move.

        Args:
            moveFrom: Source coordinate as `(x, y)`.
            moveTo: Destination coordinate as `(x, y)`.
        """
        self.moveFrom = moveFrom ## tuple(x, y)
        self.moveTo = moveTo ## tuple(x, y)

    def get_params(self):
        """
        Return the move endpoints as individual coordinates.

        Returns:
            tuple: `(x_0, y_0, x_1, y_1)` for the move.
        """
        x_0, y_0 = self.moveFrom
        x_1, y_1 = self.moveTo
        return x_0, y_0, x_1, y_1
    
    def __eq__(self, other):
        """
        Compare two moves, treating forward and backward travel as equivalent.

        Args:
            other: Object to compare against.

        Returns:
            bool: True when both moves connect the same two coordinates.
        """
        if not isinstance(other, Move):
            return False
        return (self.moveFrom == other.moveFrom and self.moveTo == other.moveTo) or (self.moveFrom == other.moveTo and self.moveTo == other.moveFrom)

    def __hash__(self):
        """
        Compute a hash value for the move.

        Returns:
            int: Hash based on the stored endpoints.
        """
        return hash((self.moveFrom, self.moveTo))
    
    def invert(self):
        """
        Mirror the move across the standard 10x10 board.

        Returns:
            None
        """
        x0, y0 = self.moveFrom
        x1, y1 = self.moveTo
        self.moveFrom = (9 - x0, 9 - y0)
        self.moveTo = (9 - x1, 9 - y1)
    
  