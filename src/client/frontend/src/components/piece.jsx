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

export default function Piece({ rank, player, revealed }) {
  const isBlue = player == "BLUE";
  const isVisible = isBlue || revealed;

  return (
    <div
     className={`
        relative w-[85%] h-[85%] rounded-sm flex items-center justify-center
        text-white font-bold text-[clamp(8px,1.3vw,16px)]
        bg-cover bg-center select-none shadow-sm transition-all duration-300
      `}
      style={{ backgroundImage: `url(${isBlue ? pieceBlue : pieceRed})` }}
    >
    {/* Le Grade*/}
    <span 
      className={`
        absolute top-0.5 left-1 z-10 
        text-[clamp(8px,1.1vw,14px)] text-emerald-900
        ${isVisible ? "opacity-100" : "opacity-0"}
      `}
    >
      {isVisible ? rank : "?"}
    </span>
      {/*  Le visuel SVG si visible*/} 
      {isVisible && (
        <div className="absolute inset-0 flex items-center justify-center p-1 pointer-events-none">
        <Marshal 
          className="text-blue-900"
        />
        </div>
      )}  {/* ? si invisible*/} 
      {!isVisible &&(
        <div className= "absolute inset-0 bg-black/10 rounded-sm flex items-center justify-center">
        <span className="text-white/50 text-xl">?</span>
        </div>
      )}    
    </div>
  );
}