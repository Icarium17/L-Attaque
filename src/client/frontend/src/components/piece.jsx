import pieceBlue from '../assets/images/piece-blue.png';
import pieceRed from '../assets/images/piece-red.png';

export default function Piece({ rank, player, revealed }) {
  const isBlue = player == "BLUE";

  return (
    <div
      className={`
        w-[85%] h-[85%] rounded-sm flex items-center justify-center
        text-white font-bold text-[clamp(8px,1.3vw,16px)]
        bg-cover bg-center select-none
        ${revealed || isBlue ? "" : "text-transparent"}
      `}
      style={{ backgroundImage: `url(${isBlue ? pieceBlue : pieceRed})` }}
    >
      {revealed || isBlue ? rank : "?"}
    </div>
  );
}