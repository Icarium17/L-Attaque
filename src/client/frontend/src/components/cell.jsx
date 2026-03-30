 

import cellTexture from '../assets/images/cell-default.png';
import cellLake from '../assets/images/cell-lake.png';
import cellSelected from '../assets/images/cell-selected.png';
import cellValid from '../assets/images/cell-valid.png';
import Piece  from "../components/piece.jsx";
 
export default function Cell({ row, col, isLake, piece, onClick, isSelected, isValidMove, playerColor }) {
  let texture;
  if (isLake) {
    texture = cellLake;
  } else if (isSelected) {
    texture = cellSelected;
  } else if (isValidMove) {
    texture = cellValid;
  } else {
    texture = cellTexture;
  }

 return (
    <div
      onClick={() => onClick(row, col)}
      className={`
        aspect-square flex items-center justify-center
        ${isLake ? "cursor-not-allowed" : "cursor-pointer hover:brightness-125"}
        transition-all duration-150 bg-cover bg-center
      `}
      style={{ backgroundImage: `url(${texture})` }}
    >
      {piece && <Piece rank={piece.rank} type={piece.type} player={piece.player} revealed={piece.revealed} playerColor ={playerColor} />}
    </div>
  );
}