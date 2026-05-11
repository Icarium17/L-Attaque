import { makeMove } from "./gameService.js";
import { makeBoard } from "./boardUtils.js";
import { useRef } from "react";

export function useCellClick({ board, setBoard, turn, setTurn, selectedCell, setSelectedCell, loading, setLoading, phase, setError, handlePlacementCellClick, isLake, playerColor, playerOrder, opponentColor, setPingMs, setBattleCell }) {

  const dragSource = useRef(null);

  const applyMoveResult = (data, t, from, to) => {
    if (data?.result?.error) { setError(data.result.error); return; }
    if (setPingMs) setPingMs(Date.now() - t); 
    const status = data?.response_svr?.status?.toUpperCase();
    if (status == "BATTLE") {
      const transitBoard = board.map(r => r.map(c => c ? {...c} : null));
      transitBoard[from.row][from.col] = null;
      setBoard(transitBoard);
      setBattleCell({ row: to.row, col: to.col });
      setSelectedCell(null);
      return;
    }
    if (data?.result?.apiBoard)
      setBoard(makeBoard(data.result.apiBoard, playerOrder, playerColor, opponentColor));
    if (data?.result?.turn)
      setTurn(data.result.turn.toUpperCase());
    setSelectedCell(null);
  };

  const handleCellClick = (row, col) => {
    if (loading) return;
    if (phase == "PLACEMENT") { handlePlacementCellClick(row, col); return; }
    if (isLake(row, col)) return;

    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
    } else {
      const t = Date.now();
      setLoading(true);
      makeMove(selectedCell.row, selectedCell.col, row, col)
        .then((data) => applyMoveResult(data, t, selectedCell, { row, col }))
        .catch(() => setError("Erreur lors du mouvement"))
        .finally(() => setLoading(false));
    }
  };

  const handleDragStart = (source) => {
    if (phase != "PLAYING") return;
    const piece = board[source.row][source.col];
    if (!piece || piece.player != turn || loading) return;
    dragSource.current = source;
    setSelectedCell(null);
  };

  const handleBoardDrop = (row, col) => {
    if (phase != "PLAYING") return;
    const source = dragSource.current;
    if (!source) return;
    dragSource.current = null;
    if (source.row == row && source.col == col) return;
    if (isLake(row, col) || loading) return;
    const t = Date.now();
    setLoading(true);
    makeMove(source.row, source.col, row, col)
      .then((data) => applyMoveResult(data, t, source, { row, col }))
      .catch(() => setError("Mouvement interdit"))
      .finally(() => setLoading(false));
  };

  return { handleCellClick, handleDragStart, handleBoardDrop };
}