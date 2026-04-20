import {useRef, useState } from "react";
import { submitPlacement } from "./gameService.js";
import { createPieces, createEmptyBoard } from "./boardUtils.js";

export function usePlacement({ board, setBoard, phase, setPhase,  setLoading, setError, selectedCell, setSelectedCell,  playerColor }) {
  const [pool, setPool] = useState(() => createPieces(playerColor));
  const [selectedPoolIndex, setSelectedPoolIndex] = useState(null);
  const dragSource = useRef(null); //  type:'pool',index ou type:'board',row,col 


  // Drag
  const handleDragStart = (source) => {
  dragSource.current = source;
  setSelectedCell(null);
  setSelectedPoolIndex(null);
  };

  // Drop sur une case du board
  const handleBoardDrop = (row, col) => {
    if (phase != "PLACEMENT") return;
    if (row < 6) return;                     
    const source = dragSource.current;
    if (!source) return;
      dragSource.current = null;

    const newBoard = board.map((r) => [...r]);
    const newPool  = [...pool];

    if (source.type == "pool") {
      const dragged   = newPool[source.index];
      const existing  = newBoard[row][col];
      if (existing) newPool.push(existing);  
      newBoard[row][col] = dragged;
      newPool.splice(source.index, 1);
      setBoard(newBoard); setPool(newPool);

    } else if (source.type == "board") {    
      const p1 = newBoard[source.row][source.col];
      const p2 = newBoard[row][col];
      newBoard[source.row][source.col] = p2;
      newBoard[row][col] = p1;
      setBoard(newBoard);
    }
  };

  // Drop sur la zone pool 
const handlePoolDrop = () => {
  const source = dragSource.current;
  if (!source || source.type != "board") return;
  dragSource.current = null;
  const newBoard = board.map((r) => [...r]);
  const piece = newBoard[source.row][source.col];
  if (!piece) return;
  newBoard[source.row][source.col] = null;
  setBoard(newBoard);
  setPool([...pool, piece]);
  };


  /*
  Gestion du clic sur une case:
  Phase de placement :
  si une pièce du pool est sélectionnée on la pose
  si une case est sélectionnée, on peut déplacer/échanger
  double clic sur une pièce posée => retour dans le pool
   */


   
   // Clic sur une pièce du pool alors sélection.
  const handlePoolClick = (index) => {
    if (phase != "PLACEMENT") return;
    setSelectedPoolIndex(index);
    setSelectedCell(null);
  };


  const handlePlacementCellClick = (row, col) => {
    if (row < 6) return;
    const clickedPiece = board[row][col];
    
    // Pièce du pool choisie : on la place sur la case cliquée
    if (selectedPoolIndex != null) {
      const newBoard = board.map((r) => [...r]);
      const newPool = [...pool];

      // Si une pièce existe sur la case,retourne dans le pool
      if (clickedPiece) newPool.push(clickedPiece);

      newBoard[row][col] = newPool[selectedPoolIndex];
      newPool.splice(selectedPoolIndex, 1);
      setBoard(newBoard);
      setPool(newPool);
      setSelectedPoolIndex(null);
      return;
    }
    
    // Sélectionne une pièce placée
    if (!selectedCell) {
      if (clickedPiece) setSelectedCell({ row, col });
    } else {  // Double-clic la même case -> retour au pool
      if (selectedCell.row == row && selectedCell.col == col) {// copie du board
        const newBoard = board.map((r) => [...r]);
        newBoard[row][col] = null;// met la case a null
        setBoard(newBoard);
        setPool([...pool, board[row][col]]);// ajoute la piece a la fin du board
        setSelectedCell(null);
        return;
      }

      // Sinon, switche entre la case sélectionnée et la case cliquée
      const newBoard = board.map((r) => [...r]);
      const piece1 = newBoard[selectedCell.row][selectedCell.col];
      const piece2 = newBoard[row][col];
      newBoard[selectedCell.row][selectedCell.col] = piece2;
      newBoard[row][col] = piece1;
      setBoard(newBoard);
      setSelectedCell(null);
    }
  };

    /*
    Placement automatique aléatoire 
  */
  const handleAutoPlacement = () => {
    if (phase != "PLACEMENT" || pool.length == 0) return;
    const newBoard = board.map((r) => [...r]);
    let currentPool = [...pool];
    for (let row = 6; row < 10; row++) {
      for (let col = 0; col < 10; col++) {
        if (!newBoard[row][col] && currentPool.length > 0) {
          const randomIndex = Math.floor(Math.random() * currentPool.length);
          newBoard[row][col] = currentPool.splice(randomIndex, 1)[0];
        }
      }
    }
    setBoard(newBoard);
    setPool([]);
    setError("");
  };

   
   /*
    Réinitialise complètement le placement 
    */
  const handleResetPlacement = () => {
    if (phase != "PLACEMENT") return;
    setBoard(createEmptyBoard());
    setPool(createPieces("BLUE"));
    setSelectedPoolIndex(null);
    setSelectedCell(null);
    setError("");
    setLoading(false);
  };

  
  /*
    Envoie le placement final au serveur. 
  */
  const handleSubmitPlacement = () => {
    if (pool.length > 0) { setError("Il reste des pièces à placer!"); return; }
    setLoading(true);
    setError("");
    const placement = [];

    // On parcourt tout le board 
    board.forEach((row, rowIndex) => {
      row.forEach((cell, colIndex) => {
        if (cell) placement.push({
             rank: cell.rank, 
             type: cell.type, 
             position: [colIndex, rowIndex] });
      });
    });

    submitPlacement(placement)
      .then((data) => {
        if (data?.result?.error) { setError(data.result.error); return; }
        const gameData = data.response_svr;
        if (gameData?.status) {
          if (gameData?.status == "SETUP_SUCCESS" ) {
          setPhase("PLAYING");}     
          setError("");
        }
      })
      .catch(() => setError("Erreur serveur."))
      .finally(() => setLoading(false));
  };

  return { 
    pool, selectedPoolIndex, 
    handlePoolClick, handlePlacementCellClick,
    handleAutoPlacement, handleResetPlacement, handleSubmitPlacement,
    handleDragStart, handleBoardDrop, handlePoolDrop,
};
}