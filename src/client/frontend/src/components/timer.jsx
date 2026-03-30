import timerBlue from '../assets/images/timer-blue.png';
import timerRed from '../assets/images/timer_red.png';

export default function Timer({ timeLeft = 600, color = "BLUE" }) {
  const isEnding = timeLeft <= 30;
  const minutes = Math.floor(timeLeft / 60);
  const seconds = `${timeLeft % 60}`.padStart(2, '0');

  return (
    <div className="relative flex items-center justify-center w-32 h-32">
      <img
        src={color == "RED" ? timerRed : timerBlue}
        alt="timer"
        className={`absolute inset-0 w-full h-full object-contain transition-all duration-300
          ${isEnding ? 'animate-pulse brightness-150 hue-rotate-300 saturate-200' : ''}`}
      />
      <span
        className={`relative z-10 font-black text-2xl select-none leading-none
          ${isEnding ? 'text-red-500' : 'text-white'}
          drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]`}
        style={{ transform: 'translateY(-7px)' }}
      >
        {minutes}:{seconds}
      </span>
    </div>
  );
}