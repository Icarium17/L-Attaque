import { useEffect, useState } from "react";
import PieceCard from "../components/pieceCard.jsx";
import battleBackground from "../assets/images/battle-background.png";

const DELAY_APPEAR = 1000;
const PHASE_REVEAL = 3000 + DELAY_APPEAR;
const PHASE_CLOSE = 4000 + DELAY_APPEAR;

export default function Battle({ attacker, defender, result, onClose }) {
  const [visible, setVisible] = useState(false);
  const [showResult, setShowResult] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), DELAY_APPEAR);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setShowResult(true), PHASE_REVEAL);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onClose?.(), 350);
    }, PHASE_CLOSE);
    return () => clearTimeout(t);
  }, [onClose]);

  const isDraw = result == "DRAW" || result == "BOTH_LOSE";
  const winner = result == "ATTACKER_WIN" ? attacker : result == "DEFENDER_WIN" ? defender : null;
  const isRed = winner?.player == "RED";

  return (
    <div
      className={`
        absolute inset-0 z-50 flex items-center justify-center
        bg-cover bg-center transition-opacity duration-350
        ${visible ? "opacity-100" : "opacity-0 pointer-events-none"}
      `}
      style={{ backgroundImage: `url(${battleBackground})` }}
    >
      <div className="absolute inset-0 bg-black/65 pointer-events-none" />

     
      <div className="relative z-10 flex items-center justify-center w-[500px] h-[320px]">

        {/* Phase 1 : les 2 pièces côte à côte */}
        {!showResult && (
          <div className="flex items-center gap-10">
            <PieceCard piece={attacker} />
            <PieceCard piece={defender} />
          </div>
        )}

        {/* Phase 2 : résultat */}
        {showResult && (
          <div className="flex items-center justify-center animate-[fadeIn_0.5s_ease]">
            {isDraw ? (
              <div className="flex items-center gap-10">
                <div className="scale-110"><PieceCard piece={attacker} /></div>
                <div className="scale-110"><PieceCard piece={defender} /></div>
              </div>
            ) : (
              <div className="scale-150">
                <PieceCard piece={winner} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Égalité */}
      {showResult && (
        <div className="absolute left-1/2 -translate-x-1/2 z-10" style={{ top: "calc(50% + 180px)" }}>
          {isDraw ? (
            <span className="text-xl font-black tracking-widest uppercase text-yellow-300animate-[fadeIn_0.5s_ease]">
              Égalité !
            </span>
          ) : (
            <span className={`text-xl font-black tracking-widest uppercase animate-[fadeIn_0.5s_ease] ${isRed ? "text-red-300" : "text-blue-300"}`}>
              Vainqueur !
            </span>
          )}
        </div>
      )}
    </div>
  );
}