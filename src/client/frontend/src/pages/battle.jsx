import { useEffect, useState } from "react";
import PieceCard             from "../components/pieceCard.jsx";
import battleBackground   from "../assets/images/battle-background.png";

const PHASE_REVEAL = 1700;
const PHASE_CLOSE  = 2500;


export default function Battle({ attacker, defender, result, onClose }) {
  const [visible,    setVisible]    = useState(false);
  const [showResult, setShowResult] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 50);
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

  const isDraw  = result == "DRAW" || result == "BOTH_LOSE";
  const winner  = result == "ATTACKER_WIN" ? attacker : result == "DEFENDER_WIN" ? defender : null;
  const isRed   = winner?.player == "RED";

  return (
    <div
      className={`
        absolute inset-0 z-50 flex flex-col items-center justify-center
        bg-cover bg-center transition-opacity duration-350
        ${visible ? "opacity-100" : "opacity-0 pointer-events-none"}
      `}
      style={{ backgroundImage: `url(${battleBackground})` }}
    >
      <div className="absolute inset-0 bg-black/65 pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center gap-4">

        {/* Afficher les 2 pieces */}
        {!showResult && (
          <div className="flex items-center gap-10 px-8">
            <PieceCard piece={attacker} />
            <PieceCard piece={defender} />
          </div>
        )}

        {/* Afficher la piece gagnante*/}
        {showResult && (
          <div className="flex flex-col items-center gap-4 animate-[fadeIn_0.5s_ease]">
            {isDraw ? (
                <div className="flex items-center gap-6">
                  <div className="scale-110"><PieceCard piece={attacker} /></div>
                  <div className="scale-110"><PieceCard piece={defender} /></div>
                </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="scale-150">
                  <PieceCard piece={winner} />
                </div>
                <span className={`mt-10 text-xl font-black tracking-widest uppercase ${isRed ? "text-red-300" : "text-blue-300"}`}>
                  Vainqueur !
                </span>
              </div>
            )}
          </div>
        )}

        {/* Égalité */}
        {showResult && isDraw && (
          <span className="mt-4 text-xl font-black tracking-widest uppercase text-yellow-300">
            Égalité !
          </span>
        )}
      </div>
    </div>
  );
}