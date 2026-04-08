import { useEffect, useState } from "react";
import PieceCard             from "../components/pieceCard.jsx";
import battleBackground   from "../assets/images/battle-background.png";

const PHASE_REVEAL = 5000;
const PHASE_CLOSE  = 10000;


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

  return (
    <div/>    
  );
}