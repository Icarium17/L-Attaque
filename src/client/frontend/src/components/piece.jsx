import pieceBlue from '../assets/images/piece-blue.png';
import pieceRed from '../assets/images/piece-red.png';
import Marshal from '../assets/svg-pieces/marshal.svg?react';
import Bomb from '../assets/svg-pieces/bomb.svg?react';
import Captain from '../assets/svg-pieces/captain.svg?react';
import Colonel from '../assets/svg-pieces/colonel.svg?react';
import Flag from '../assets/svg-pieces/flag.svg?react';
import General from '../assets/svg-pieces/general.svg?react';
import Lieutenant from '../assets/svg-pieces/lieutenant.svg?react';
import Major from '../assets/svg-pieces/major.svg?react';
import Miner from '../assets/svg-pieces/miner.svg?react';
import Scout from '../assets/svg-pieces/scout.svg?react';
import Sergeant from '../assets/svg-pieces/sergeant.svg?react';
import Spy from '../assets/svg-pieces/spy.svg?react';

const PIECE_COMPONENTS = {
  'Marechal': Marshal,
  'General': General,
  'Colonel': Colonel,
  'Major': Major,
  'Capitaine': Captain,
  'Lieutenant': Lieutenant,
  'Sergent': Sergeant,
  'Demineur': Miner,
  'Eclaireur': Scout,
  'Espion': Spy,
  'Bombe': Bomb,
  'Drapeau': Flag
};

export default function Piece({ rank, player, type, revealed, playerColor }) {
  const isBlue = player == "BLUE";
  const isVisible = (player == playerColor) || revealed;
  const Aspect = PIECE_COMPONENTS[type];

  const isFlag = type == 'Drapeau';
  const isBomb = type == 'Bombe';
  const isSpecial = isFlag || isBomb;
 
  let specialRing = '';
  if (isVisible) {
    if (isFlag) {
      specialRing = 'shadow-[0_0_14px_rgba(254,240,138,0.85)]';
    } else if (isBomb) {
      specialRing = isBlue 
        ? 'shadow-[0_0_14px_rgba(153,27,27,0.85)]'
        : 'shadow-[0_0_14px_rgba(0,0,0,0.7)]';
    }
  }

  // Couleur du SVG  
  let svgColor;
  if (isVisible && isFlag) {
    svgColor = isBlue ? 'text-yellow-100' : 'text-yellow-600';
  } else if (isVisible && isBomb) {
    svgColor = isBlue ? 'text-red-700' : 'text-slate-900';
  } else {
    svgColor = 'text-slate-900';
  }

  // Outline autour du SVG
  const outlineColor = isBlue ? 'rgba(255,255,255,0.95)' : 'rgba(254,202,202,0.9)';
  const svgFilter = isSpecial 
    ? 'drop-shadow(0 1px 2px rgba(0,0,0,0.5))'
    : `drop-shadow(1px 0 0 ${outlineColor}) 
       drop-shadow(-1px 0 0 ${outlineColor}) 
       drop-shadow(0 1px 0 ${outlineColor}) 
       drop-shadow(0 -1px 0 ${outlineColor})`;

  return (
    <div
      className={`
        relative w-[92%] h-[92%] rounded-sm flex items-center justify-center
        text-white font-bold text-[clamp(8px,1.3vw,16px)]
        bg-cover bg-center select-none shadow-sm transition-all duration-300
        ${specialRing}
      `}
      style={{ backgroundImage: `url(${isBlue ? pieceBlue : pieceRed})` }}
    >
      <span
        className={`
          absolute top-2 left-3 z-10
          text-[clamp(8px,1.2vw,14px)] fhd:text-[clamp(10px,1.1vw,14px)] 4k:text-[clamp(14px,0.9vw,20px)]
          ${isVisible && !isSpecial ? "opacity-100" : "opacity-0"}
        `}
      >
        {isVisible ? rank : "?"}
      </span>

      {isVisible && Aspect && (
        <div
          className={`object-contain pointer-events-none ${
          isSpecial ? 'w-[60%] h-[65%]' : 'w-[55%] h-[62%]'
          }`}
          style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.5))' }}
        >
          <Aspect className={`w-full h-full ${svgColor}`} />
        </div>
      )}

      {!isVisible && (
        <div className="absolute inset-0 bg-black/10 rounded-sm flex items-center justify-center">
          <span className="text-white text-xl">?</span>
        </div>
      )}
    </div>
  );
}