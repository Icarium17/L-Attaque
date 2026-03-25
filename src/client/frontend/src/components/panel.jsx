 
import { useState, useEffect, useRef } from "react";

const VARIANTS = {
  error: {
    border: "#c0392b,#ff6b5a,#8b1a1a,#c0392b,#ff6b5a", // plusieurs couleurs pour le gradient de bordure
    bg: "linear-gradient(to bottom, #1e1111, #150b0b, #0d0606)",
    color: "#e74c3c",
    colorSecond: "#eFFFFF",
    glow: "231,76,60",
  },
  warning: {
    border: "#d4a44a,#f5d78e,#8b6914,#d4a44a,#f5d78e",
    bg: "linear-gradient(to bottom, #1e1a0f, #14100a, #0d0b06)",
    color: "#d4a44a",
    colorSecond: "#eFFFFF",
    glow: "212,164,74",
  },
  info: {
    border: "#4a7fd4,#8eb5f5,#14418b,#4a7fd4,#8eb5f5",
    bg: "linear-gradient(to bottom, #0f1520, #0a0f18, #06090d)",
    color:  "#095228",
    colorSecond:  "#eFFFFF",
    glow: "91,155,255",
  },
  success: {
  border: "#27ae60,#6ddb95,#1a6b3a,#27ae60,#6ddb95",
  bg: "linear-gradient(to bottom, #0f1e14, #0a150d, #060d08)",
  color: "#2ecc71",
  colorSecond: "#eFFFFF",
  glow: "46,204,113",
  },
  title: {
  border: null,
  bg: "transparent",
  color: "#d4a44a",
  colorSecond: "#ffffff",
  glow: "212,164,74",
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

if (!message && !children && !title) return null;

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

  const v = VARIANTS[variant] || VARIANTS.error;
  const g = v.glow;

  const handleClose = () => {
    setVisible(false);
    onClose?.();
  };



  return ( 
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}

      style={{
        background: v.border ? `linear-gradient(135deg, ${v.border})` : "transparent",
        padding: v.border ? "2px" : "0px",
        borderRadius: "12px",
        boxShadow: v.border
        ? (hovered
            ? `0 8px 32px rgba(0,0,0,0.6), 0 0 40px rgba(${g},0.3)`
            : `0 4px 20px rgba(0,0,0,0.5), 0 0 20px rgba(${g},0.15)`)
        : "none",
        transition: "all 0.3s ease",
        transform: `scale(${anim.pulse})`,
      }}
      className={className}
    >

      {/* Bas du container */}
      <div
        style={{
          background: v.bg,
          borderRadius: "15px",
          padding: "16px 25px",
          position: "relative",
          overflow: "hidden",
          ...style,
        }}
      >

        {/* Reflet sur le dessus*/}
        <span
          style={{
            position: "absolute",
            top: 0,
            left: "10%",
            right: "10%",
            height: "1px",
            background: v.border
            ? `linear-gradient(90deg, transparent, rgba(${g},${hovered ? 0.5 : 0.25}), transparent)`
            : "none",
            transition: "all 0.3s ease",
            pointerEvents: "none",
          }}
        />

        {/* Hover */}
        {hovered && (
          <span
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%,-50%)",
              width: "90%",
              height: "90%",
              background: `radial-gradient(ellipse, rgba(${g},${anim.glow * 0.08}), transparent 50%)`,
              pointerEvents: "none",
            }}
          />
        )}
        {/* Texte*/}
        <div style={{ position: "relative", zIndex: 1, display: "flex", gap: "14px", alignItems: "flex-start" }}>      
          <div style={{ flex: 1, minWidth: 0 }}>
            {title && (
              <div
                style={{
                  color: v.color,
                  fontFamily: "'Georgia', 'Times New Roman', serif",
                  fontWeight: 700,
                  fontSize: variant == "title" ? "20px" : "16px",
                  letterSpacing: variant == "title" ? "6px" : "3px",
                  textAlign: variant == "title" ? "center" : "left",
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
                  fontFamily: "'Georgia', 'Times New Roman', serif",
                  fontSize: "16px",
                  lineHeight: 1.5,
                  opacity: 0.85,
                  textAlign: "center",
                  textTransform: "uppercase",
                }}
              >
                {children || message}
              </div>
            )}

            {/* Bouton Réessayer */}
            {onRetry && (
              <button
                onClick={onRetry}
                style={{
                  marginTop: "10px",
                  background: "none",
                  border: `2px solid rgba(${g},0.3)`,
                  borderRadius: "8px",
                  color: v.color,
                  fontFamily: "'Georgia', 'Times New Roman', serif",
                  fontSize: "14px",
                  fontWeight: 600,
                  letterSpacing: "3px",
                  textTransform: "uppercase",
                  padding: "6px 16px",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  textShadow: `0 0 8px rgba(${g},0.3)`,
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = `rgba(${g},0.6)`;
                  e.target.style.boxShadow = `0 0 12px rgba(${g},0.2)`;
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = `rgba(${g},0.3)`;
                  e.target.style.boxShadow = "none";
                }}
              >
                Réessayer
              </button>
            )}
          </div>

          {/* Bouton Fermer */}
          {onClose && (
            <button
              onClick={handleClose}
              style={{
                background: "none",
                border: "none",
                color: v.colorSecond,
                cursor: "pointer",
                padding: "2px",
                fontSize: "24px",
                lineHeight: 1,
                opacity: 0.6,
                transition: "all 0.2s ease",
                flexShrink: 0,
              }}
              onMouseEnter={(e) => {
                e.target.style.opacity = "1";
                e.target.style.color = v.color;
                e.target.style.textShadow = `0 0 8px rgba(${g},0.5)`;
              }}
              onMouseLeave={(e) => {
                e.target.style.opacity = "0.6";
                e.target.style.color = v.colorSecond;
                e.target.style.textShadow = "none";
              }}
              >
              
            </button>
          )}
        </div>
      </div>
    </div>
  );
}