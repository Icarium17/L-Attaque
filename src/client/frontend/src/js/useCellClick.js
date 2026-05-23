import { makeMove } from "./gameService.js";
import { makeBoard } from "./boardUtils.js";
import { useRef } from "react";

export function useCellClick({ board, setBoard, turn, setTurn, selectedCell, setSelectedCell, loading, setLoading, phase, setError, setMoveSuccess, handlePlacementCellClick, isLake, playerColor, playerOrder, opponentColor, setPingMs, setBattleCell }) {

  const dragSource = useRef(null);

  const notifyInvalid = () => {
    setError("");
    setTimeout(() => setError("Mouvement invalide"), 0);
  };

  const notifySuccess = () => {
    if (!setMoveSuccess) return;
    setMoveSuccess("");
    setTimeout(() => setMoveSuccess("Mouvement réussi"), 0);
  };

  const applyMoveResult = (data, t, from, to) => {
    if (!data || data?.result?.error) {
      notifyInvalid();
      setSelectedCell(null);
      return;
    }

    if (setPingMs) setPingMs(Date.now() - t);
    const status = data?.response_svr?.status?.toUpperCase();

    if (status == "BATTLE") {
      const transitBoard = board.map(r => r.map(c => c ? { ...c } : null));
      transitBoard[from.row][from.col] = null;
      setBoard(transitBoard);
      setBattleCell({ row: to.row, col: to.col });
      setSelectedCell(null);
      return;
    }

    const newBoard = data?.result?.apiBoard
      ? makeBoard(data.result.apiBoard, playerOrder, playerColor, opponentColor)
      : null;

    let moveValid = false;
    if (newBoard) {
      const pieceBefore = board[from.row][from.col];
      const cellFromAfter = newBoard[from.row][from.col];
      const cellToAfter = newBoard[to.row][to.col];
      const fromIsEmpty = cellFromAfter == null;
      const toHasOurPiece =
        cellToAfter != null &&
        pieceBefore != null &&
        cellToAfter.type == pieceBefore.type &&
        cellToAfter.player == pieceBefore.player;
      moveValid = fromIsEmpty && toHasOurPiece;
    }

    if (newBoard) setBoard(newBoard);
    if (data?.result?.turn) setTurn(data.result.turn.toUpperCase());
    setSelectedCell(null);

    if (moveValid) notifySuccess();
  };

  const handleCellClick = (row, col) => {
    if (loading) return;
    if (phase == "PLACEMENT") { handlePlacementCellClick(row, col); return; }

    if (isLake(row, col)) {
      if (selectedCell) {
        notifyInvalid();
        setSelectedCell(null);
      }
      return;
    }

    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
      return;
    }

    if (selectedCell.row == row && selectedCell.col == col) {
      setSelectedCell(null);
      return;
    }

    const target = board[row][col];
    if (target && target.player == turn) {
      setSelectedCell({ row, col });
      return;
    }

    const t = Date.now();
    setLoading(true);
    makeMove(selectedCell.row, selectedCell.col, row, col)
      .then((data) => applyMoveResult(data, t, selectedCell, { row, col }))
      .catch(() => {
        notifyInvalid();
        setSelectedCell(null);
      })
      .finally(() => setLoading(false));
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

    if (isLake(row, col)) {
      notifyInvalid();
      return;
    }
    if (loading) return;

    const t = Date.now();
    setLoading(true);
    makeMove(source.row, source.col, row, col)
      .then((data) => applyMoveResult(data, t, source, { row, col }))
      .catch(() => notifyInvalid())
      .finally(() => setLoading(false));
  };

  return { handleCellClick, handleDragStart, handleBoardDrop };
}