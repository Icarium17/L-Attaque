import React from 'react';
import cellTexture from '../assets/images/cell-default.png';
import cellLake from '../assets/images/cell-lake.png';
import cellSelected from '../assets/images/cell-selected.png';
import cellValid from '../assets/images/cell-valid.png';
import cellBattle from '../assets/images/cell-battle.png';
import Piece from "../components/piece.jsx";
import React, { useState } from 'react';

export default function Cell({ 
  row, col, isLake, piece, onClick, isSelected, 
  isValidMove, playerColor, onDragStart, onDrop, isBattle 
}) {
  
  const [isDragOver, setIsDragOver] = useState(false);
  const [isDraggingThisPiece, setIsDraggingThisPiece] = useState(false);

  let texture;
  if (isLake)           texture = cellLake;
  else if (isBattle)    texture = cellBattle;
  else if (isSelected)  texture = cellSelected;
  else if (isValidMove) texture = cellValid;
  else                  texture = cellTexture;

  const isDraggable = onDragStart != null && piece != null;

  return (
    <>
      <style>
        {`
          /* Glow VERT pour la sélection et le départ du drag */
          @keyframes greenPulse {
            0%, 100% { box-shadow: inset 0 0 10px #22c55e, 0 0 15px #22c55e; }
            50% { box-shadow: inset 0 0 20px #4ade80, 0 0 25px #4ade80; }
          }
          
          /* Glow BLANC  pour la zone de drop */
          @keyframes dropZonePulse {
            0%, 100% { box-shadow: inset 0 0 15px #ffffff, 0 0 20px #fef08a; filter: brightness(1.2); }
            50% { box-shadow: inset 0 0 30px #ffffff, 0 0 40px #fef08a; filter: brightness(1.4); }
          }

          .glow-selection {
            animation: greenPulse 1.5s ease-in-out infinite;
            z-index: 10;
            outline: 2px solid #22c55e;
          }

          .glow-drop-target {
            animation: dropZonePulse 0.6s ease-in-out infinite;
            z-index: 20;
            transform: scale(1.05);
            outline: 3px solid #ffffff;
          }

          .valid-move-hint {
            border: 2px dashed #22c55e;
            box-shadow: inset 0 0 10px rgba(34, 197, 94, 0.3);
          }
        `}
      </style>

      <div
        onClick={() => onClick(row, col)}
        draggable={isDraggable}
        
        onDragStart={isDraggable ? (e) => {
          e.dataTransfer.effectAllowed = "move";
          setIsDraggingThisPiece(true);
          onDragStart({ type: "board", row, col });
        } : undefined}
        
        onDragEnd={() => setIsDraggingThisPiece(false)}

        onDragOver={onDrop ? (e) => { 
          e.preventDefault(); 
          if (!isLake) setIsDragOver(true);
        } : undefined}

        onDragLeave={() => setIsDragOver(false)}

        onDrop={onDrop ? (e) => { 
          e.preventDefault(); 
          setIsDragOver(false); 
          onDrop(row, col); 
        } : undefined}

        className={`
          aspect-square flex items-center justify-center
          transition-all duration-150 bg-cover bg-center relative
          ${isLake ? "cursor-not-allowed" : "cursor-pointer"}
          ${isSelected || isDraggingThisPiece ? "glow-selection" : ""}
          ${isDragOver ? "glow-drop-target" : ""}
          ${isValidMove && !isDragOver ? "valid-move-hint" : ""}
          ${isDraggingThisPiece ? "opacity-50" : "opacity-100"}
        `}
        style={{ backgroundImage: `url(${texture})` }}
      >
        {piece && !isBattle && (
          <Piece 
            rank={piece.rank} 
            type={piece.type} 
            player={piece.player} 
            revealed={piece.revealed} 
            playerColor={playerColor} 
          />
        )}
      </div>
    </>
  );
}