import arrow from '../assets/images/arrow.png';
import hood from '../assets/images/hood.png';

export default function TurnIndicator({ turn, opponentName = "RED", playerName = "BLUE" }) {
  const isBlue = turn == "BLUE";

  return (
    <div className="fixed left-0 top-1/2 -translate-y-1/2 select-none z-50">
      <div className="relative w-125 h-36">
        <img
          src={hood}
          alt="hood"
          className="absolute inset-0 w-full h-full object-fill opacity-90"
        />

      <span className="relative z-10 flex h-full items-center pl-4 font-black text-4xl tracking-widest drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]"
       style={{ color: isBlue ? '#60a5fa' : '#f87171', transition: 'color 0.5s' }}
      >
      {isBlue ? playerName : opponentName}
      </span>
        {/* Point fixe de rotation*/}
        <div className="absolute left-1/2 -translate-x-1/2 ml-40" style={{ top: '-7rem' }}>
        <div className="absolute w-3 h-3  rounded-full z-50" style={{ bottom: '4rem', left: '50%', transform: 'translateX(-50%)' }} />
        <img
          src={arrow}
          alt="tour"
          className="w-40 h-60 object-contain"
          style={{
            transformOrigin: '40% 75%',
            transform: isBlue ? 'scaleY(-1)' : 'scaleY(1)',
            transition: 'transform 0.5s',
          }}
        />
      </div>
      </div>
    </div>
  );
}