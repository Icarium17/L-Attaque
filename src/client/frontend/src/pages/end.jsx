import { useEffect, useState } from "react";
import Button from "../components/button.jsx";
import victoryImg from "../assets/images/victory.png";
import defaiteImg from "../assets/images/defeat.png";
 
export default function end({ result, onClose }) {
  const [visible, setVisible] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const isWin = result == "WIN";
 
  useEffect(() => {
    const t1 = setTimeout(() => setVisible(true), 2000);
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) { clearInterval(interval); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => { clearTimeout(t1); clearInterval(interval); };
  }, []);
 
  const handleClose = () => {
    setVisible(false);
    setTimeout(() => onClose?.(), 2000);
  };
 
  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">  
      <div className={`flex flex-col items-center gap-8 p-10 rounded-2xl border backdrop-blur-md ${isWin ? "border-yellow-500/30 bg-yellow-950/10" : "border-red-900/30 bg-red-950/10"}`}>
        <img
          src={isWin ? victoryImg : defaiteImg}
          alt={isWin ? "Victoire" : "Défaite"}
          className="w-84 h-auto"
          draggable={false}
        />
        <Button
          variant={isWin ? "primary" : "danger"}
          text={countdown > 0 ? `Continue ${countdown}` : "Continue"}
          onClick={countdown == 0 ? handleClose : undefined}
          disabled={countdown > 0}
          fullWidth
        />
      </div>
    </div>
  );
}
 