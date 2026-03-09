 
import { useState, useEffect, useRef } from "react";

const VARIANTS = {
  error: {
    border: "#c0392b,#ff6b5a,#8b1a1a,#c0392b,#ff6b5a",
    bg: "linear-gradient(to bottom, #1e1111, #150b0b, #0d0606)",
    color: "#e74c3c",
    colorMuted: "#a33025",
    glow: "231,76,60",
  },
  warning: {
    border: "#d4a44a,#f5d78e,#8b6914,#d4a44a,#f5d78e",
    bg: "linear-gradient(to bottom, #1e1a0f, #14100a, #0d0b06)",
    color: "#d4a44a",
    colorMuted: "#b8902e",
    glow: "212,164,74",
  },
  info: {
    border: "#4a7fd4,#8eb5f5,#14418b,#4a7fd4,#8eb5f5",
    bg: "linear-gradient(to bottom, #0f1520, #0a0f18, #06090d)",
    color: "#5b9bff",
    colorMuted: "#2e6ab8",
    glow: "91,155,255",
  },
};



export default function Error({
  variant = "error",
  title,
  message,
  children,
  onClose,
  onRetry,
  className,
  style,
  autoClose = 0,
}) {
  const [visible, setVisible] = useState(true);
  const [hovered, setHovered] = useState(false);
  const [anim, setAnim] = useState({ glow: 0.3, pulse: 1 });
  const rafRef = useRef(null);
  const timerRef = useRef(null);

  /* Femeture automatique */
  useEffect(() => {
    if (autoClose > 0) {
      timerRef.current = setTimeout(() => {
        setVisible(false);
        onClose?.();
      }, autoClose);
      return () => clearTimeout(timerRef.current);
    }
  }, [autoClose, onClose]);

  return (
   
    <div></div>)}