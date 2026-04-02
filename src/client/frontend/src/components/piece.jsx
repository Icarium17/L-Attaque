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

export default function Piece({ rank, player, type, revealed, playerColor}) {
  const isBlue = player == "BLUE";
  const isVisible = (player == playerColor) || revealed;   
  const Aspect = PIECE_COMPONENTS[type];

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
        absolute top-3.5 left-3 z-10 
        text-[clamp(14px,1.6vw,16px)] text-white
        ${isVisible ? "opacity-100" : "opacity-0"}
      `}
      >
      {isVisible ? rank : "?"}
      </span>
    {/* Le visuel SVG si visible*/} 
      {isVisible && Aspect && ( 
         <div className="w-9 h-11 object-contain pointer-events-none">
          <Aspect className="text-blue-950" />
        </div>
      )}     
      {/* ? si invisible*/} 
      {!isVisible &&(
        <div className= "absolute inset-0 bg-black/10 rounded-sm flex items-center justify-center">
        <span className="text-white/50 text-xl">?</span>
        </div>
      )}    
    </div>
  );
}