 
import { makeMove } from "./gameService.js";

export function useCellClick({ board, setBoard, turn, setTurn, selectedCell, setSelectedCell, loading, setLoading, phase, setError, handlePlacementCellClick, isLake }) {

  const handleCellClick = (row, col) => {
    if (loading) return;
    if (phase == "PLACEMENT") { handlePlacementCellClick(row, col); return; }
    if (isLake(row, col)) return;

    // Premier clic sélectionne une piece
    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
    } else {
      // Deuxième clic validation du déplacement via l'API
      setLoading(true);
      makeMove(selectedCell.row, selectedCell.col, row, col)
        .then((data) => {
          if (data?.result?.board) setBoard(data.result.board);
          if (data?.result?.turn) setTurn(data.result.turn);
          setSelectedCell(null);
        })
        .catch(() => setError("Erreur lors du mouvement"))
        .finally(() => setLoading(false));
    }
  };
  return { handleCellClick };
}