import arrow from '../assets/images/arrow.png';
import hood from '../assets/images/hood.png';

export default function TurnIndicator({
  turn,
  playerColor = "BLUE",
  playerName = "BLUE",
  opponentName = "Adversaire"
}) {

  const isMyTurn = turn == playerColor;
  const iAmBlue = playerColor == "BLUE";
  const myColor = iAmBlue ? '#ffffff' : '#f87171';
  const myBg = iAmBlue ? 'rgba(96,165,250,0.35)' : 'rgba(220,38,38,0.35)';
  const oppColor = iAmBlue ? '#f87171' : '#ffffff';
  const oppBg = iAmBlue ? 'rgba(220,38,38,0.35)' : 'rgba(96,165,250,0.35)';
 

  return (
  <div className="fixed left-0 top-1/2 -translate-y-1/2 select-none z-50">      
    <div className="relative w-125 h-36 fhd:w-100 fhd:h-28">
      <img
        src={hood}
        alt="hood"
        className="absolute inset-0 w-full h-full object-fill opacity-90"
      />
      <span
        className="
          relative z-10 flex h-full items-center pl-4 pr-4
          font-black text-4xl fhd:text-3xl tracking-widest rounded-xl
          drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]
        "
        style={{
          color: isMyTurn ? myColor : oppColor,
          backgroundColor: isMyTurn ? myBg : oppBg,
          transition: 'color 0.5s, background-color 0.5s',
        }}
      >
        {(isMyTurn ? playerName : opponentName).toUpperCase()}
      </span>

      {/* Point fixe de rotation*/}
      <div
        className="absolute left-1/2 -translate-x-1/2 ml-36 fhd:ml-28 z-50"
        style={{ top: '-5.5rem' }}
        >
        <div
          className="absolute w-3 h-3 rounded-full z-60"
          style={{
            bottom: '3.3rem',
            left: '50%',
            transform: 'translateX(-50%)',
          }}
        />
        <img
          src={arrow}
          alt="tour"
          className="relative w-40 h-60 fhd:w-32 fhd:h-48 object-contain z-55"
          style={{
            transformOrigin: '40% 75%',
            transform: isMyTurn ? 'scaleY(-1)' : 'scaleY(1)',
            transition: 'transform 0.5s',
          }}
        />
      </div>
    </div>
  </div>
);
}