 

import cellTexture from '../assets/images/cell-default.png';
import cellLake from '../assets/images/cell-lake.png';
import cellSelected from '../assets/images/cell-selected.png';
import cellValid from '../assets/images/cell-valid.png';

export default function Cell({ row, col, isLake, piece, onClick, isSelected, isValidMove }) {
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
      onClick={() => !isLake && onClick(row, col)}
      className={`
        aspect-square flex items-center justify-center
        ${isLake ? "cursor-not-allowed" : "cursor-pointer hover:brightness-125"}
        transition-all duration-150 bg-cover bg-center
      `}
      style={{ backgroundImage: `url(${texture})` }}
    >
      {piece && (
        <div className={`
          w-[80%] h-[80%] rounded-sm flex items-center justify-center
          text-white font-bold text-[clamp(10px,1.5vw,18px)]
          ${piece.player == "blue" ? "bg-blue-700 border border-blue-400" : "bg-red-800 border border-red-500"}
        `}>
          {piece.revealed || piece.player == "blue" ? piece.rank : "?"}
        </div>
      )}
    </div>
  );
}