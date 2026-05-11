import yourTurnBg from '../assets/images/your-turn-bg.png';

export default function YourTurn({ show }) {
  if (!show) return null;

  return (
    <div className="absolute inset-0 z-100 flex items-center justify-center pointer-events-none">
      <img src={yourTurnBg} alt="ton tour" className="w-1/2" />
    </div>
  );
}