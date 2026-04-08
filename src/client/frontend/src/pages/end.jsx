import { useEffect, useState } from "react";
import Button from "../components/Button.jsx";
import victoryImg from "../assets/images/victory.png";
import defaiteImg from "../assets/images/defeat.png";

export default function end({ result, onClose }) {
  const [visible, setVisible] = useState(false);
  const isWin = result == "WIN";

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 2000);
    return () => clearTimeout(t);
  }, []);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => onClose?.(), 4000);
  };

  return (
    <div className={`absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm transition-opacity duration-300 ${visible ? "opacity-100" : "opacity-0 pointer-events-none"}`}>
      <div className={`flex flex-col items-center gap-8 p-10 rounded-2xl border ${isWin ? "border-yellow-500/40 bg-yellow-950/20" : "border-red-900/40 bg-red-950/20"}`}>
        <img
          src={isWin ? victoryImg : defaiteImg}
          alt={isWin ? "Victoire" : "Défaite"}
          className="w-84 h-auto"
          draggable={false}
        />
        <Button
          variant={isWin ? "primary" : "danger"}
          text="Continue"
          onClick={handleClose}
          fullWidth
        />
      </div>
    </div>
  );
}
