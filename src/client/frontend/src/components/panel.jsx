// Composant de base réutilisable pour tous les GameMessage et les Notifications.

import { useState, useEffect, useRef } from "react";
import plaqueError from "../assets/images/plaque-error.svg";
import plaqueSuccess from "../assets/images/plaque-success.svg";
import plaqueInfo from "../assets/images/plaque-info.svg";
import plaqueWarning from "../assets/images/plaque-warning.svg";

const VARIANTS = {
  error: {
    plaque: plaqueError,
    color: "#ff8a7a",
    colorSecond: "#fdf3ee",
    glow: "231,76,60",
  },
  warning: {
    plaque: plaqueWarning,
    color: "#f5d78e",
    colorSecond: "#fdf3ee",
    glow: "212,164,74",
  },
  info: {
    plaque: plaqueInfo,
    color: "#8eb5f5",
    colorSecond: "#fdf3ee",
    glow: "91,155,255",
  },
  success: {
    plaque: plaqueSuccess,
    color: "#a8e6c0",
    colorSecond: "#fdf3ee",
    glow: "46,204,113",
  },
  title: {
    plaque: null,
    bg: "transparent",
    color: "#d4a44a",
    colorSecond: "#ffffff",
    glow: "212,164,74",
  },
  score: {
    plaque: null,
    bg: "linear-gradient(to bottom, #1a1600, #110f00, #0a0800)",
    color: "#ffe066",
    colorSecond: "#ffffff",
    glow: "255,220,80",
  },
  name: {
    plaque: null,
    bg: "transparent",
    color: "#ffffff",
    colorSecond: "#ffffff",
    glow: "231,76,60",
  },
};

export default function Panel({
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

  useEffect(() => {
    setVisible(true);
  }, [message, title, children]);

  // Fermeture automatique
  useEffect(() => {
    if (autoClose > 0 && visible) {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        setVisible(false);
        onClose?.();
      }, autoClose);
      return () => clearTimeout(timerRef.current);
    }
  }, [autoClose, message, title, visible]);
    /* Animation si hover */  
    useEffect(() => {
    if (!hovered) {
      setAnim({ glow: 0.3, pulse: 1 });
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }
    const tick = (t) => {
      setAnim({
        glow: 0.3 + 0.15 * (1 + Math.sin(t / 600)),
        pulse: 1 + 0.003 * Math.sin(t / 400),
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [hovered]);

  if (!visible) return null;
  if (!message && !children && !title) return null;

  const v = VARIANTS[variant] || VARIANTS.error;
  const g = v.glow;
  const usesPlaque = !!v.plaque;

  const handleClose = () => {
    setVisible(false);
    onClose?.();
  };

  // Variant bois
  if (usesPlaque) {
    return (
      <div
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        className={className}
        style={{
          position: "relative",
          minHeight: "80px",
          padding: "18px 50px",
          backgroundImage: `url(${v.plaque})`,
          backgroundSize: "100% 100%",
          backgroundRepeat: "no-repeat",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          filter: hovered
            ? `drop-shadow(0 0 18px rgba(${g},0.45)) drop-shadow(0 6px 12px rgba(0,0,0,0.6))`
            : `drop-shadow(0 0 8px rgba(${g},0.2)) drop-shadow(0 4px 8px rgba(0,0,0,0.5))`,
          transition: "all 0.3s ease",
          transform: `scale(${anim.pulse})`,
          ...style,
        }}
      >
        {title && (
          <div
            style={{
              color: v.color,
              fontWeight: 700,
              fontSize: "16px",
              letterSpacing: "3px",
              textAlign: "center",
              textTransform: "uppercase",
              whiteSpace: "nowrap",
              textShadow: `0 0 12px rgba(${g},0.7), 0 2px 4px rgba(0,0,0,0.9)`,
              marginBottom: children || message ? "6px" : 0,
              width: "100%",
            }}
          >
            {title}
          </div>
        )}

        {(children || message) && (
          <div
            style={{
              color: v.colorSecond,
              fontSize: "16px",
              lineHeight: 1.4,
              textAlign: "center",
              textTransform: "uppercase",
              letterSpacing: "2px",
              fontWeight: 600,
              textShadow: `0 2px 4px rgba(0,0,0,0.95), 0 0 8px rgba(${g},0.4)`,
              width: "100%",
            }}
          >
            {children || message}
          </div>
        )}

        {onRetry && (
          <button
            onClick={onRetry}
            style={{
              marginTop: "10px",
              background: "rgba(0,0,0,0.3)",
              border: `1.5px solid rgba(245,216,120,0.6)`,
              borderRadius: "6px",
              color: "#f5d878",
              fontSize: "14px",
              fontWeight: 600,
              letterSpacing: "3px",
              textTransform: "uppercase",
              padding: "6px 16px",
              cursor: "pointer",
              transition: "all 0.2s ease",
              textShadow: `0 0 8px rgba(${g},0.4)`,
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = `rgba(245,216,120,1)`;
              e.target.style.boxShadow = `0 0 12px rgba(${g},0.4)`;
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = `rgba(245,216,120,0.6)`;
              e.target.style.boxShadow = "none";
            }}
          >
            Réessayer
          </button>
        )}
   
        {onClose && (
          <button
            onClick={handleClose}
            style={{
              position: "absolute",
              top: "10px",
              right: "14px",
              background: "none",
              border: "none",
              color: v.colorSecond,
              cursor: "pointer",
              padding: "2px",
              fontSize: "20px",
              lineHeight: 1,
              opacity: 0.7,
              transition: "all 0.2s ease",
              textShadow: "0 1px 3px rgba(0,0,0,0.9)",
              zIndex: 2,
            }}
            onMouseEnter={(e) => {
              e.target.style.opacity = "1";
              e.target.style.color = v.color;
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = "0.7";
              e.target.style.color = v.colorSecond;
            }}
          >
            ×
          </button>
        )}
      </div>
    );
  }

  //  Variants sans plaque  
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: "transparent",
        padding: "0px",
        borderRadius: "12px",
        transition: "all 0.3s ease",
        transform: `scale(${anim.pulse})`,
      }}
      className={className}
    >
      <div
        style={{
          background: v.bg,
          borderRadius: "15px",
          padding: variant == "score" ? "8px 10px" : "16px 25px",
          position: "relative",
          overflow: "hidden",
          display: variant == "score" ? "flex" : undefined,
          flexDirection: variant == "score" ? "column" : undefined,
          justifyContent: variant == "score" ? "center" : undefined,
          alignItems: variant == "score" ? "center" : undefined,
          height: variant == "score" ? "100%" : undefined,
          ...style,
        }}
      >
        <div style={{ position: "relative", zIndex: 1, display: "flex", gap: "14px", alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            {title && (
              <div
                style={{
                  color: v.color,
                  fontWeight: 700,
                  fontSize: variant == "title" ? "20px" 
                  : variant == "score" ? "15px" 
                  : variant == "name" ? "clamp(16px, 0.9vw, 22px)" 
                  : "16px",
                  letterSpacing: variant == "title" ? "6px" : "3px",
                  textAlign: variant == "title" || variant == "name" ? "center" : "left",
                  textTransform: "uppercase",
                  whiteSpace: "nowrap",
                  textShadow: variant == "title"
                    ? `0 0 20px rgba(${g},0.8)`
                    : `0 0 16px rgba(${g},0.6)`,
                  marginBottom: children || message ? "6px" : 0,
                }}
              >
                {title}
              </div>
            )}
            {(children || message) && (
              <div
                style={{
                  color: v.colorSecond,
                  fontSize: variant == "score" ? "28px" : "16px",
                  lineHeight: 1.5,
                  opacity: 0.85,
                  textAlign: "center",
                  textTransform: "uppercase",
                }}
              >
                {children || message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
