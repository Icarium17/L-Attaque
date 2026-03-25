import { useEffect, useRef, useState } from "react";

/*
  Props :
    message   : Texte affiché sous le spinner  
    size      : Taille du spinner en px défaut: 48
    overlay   : Si true, bloque tous les controles
    silent    : Si true, bloque toute la page sans visuel
*/
export default function Loading({ message = "", size = 48, overlay = false, silent = false }) {


  if (silent) {
    return (
      <div style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        cursor: "wait",
      }} />
    );
  }

  const [anim, setAnim] = useState({ spin: 0, glow: 0.3, pulse: 1 });
  const rafRef = useRef(null);

  useEffect(() => {
    const tick = (t) => {
      setAnim({
        spin: (t / 4) % 360,
        glow: 0.3 + 0.2 * (1 + Math.sin(t / 600)),
        pulse: 1 + 0.015 * Math.sin(t / 400),
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, []);

  const g = "212,164,74";
  const color = "#d4a44a";

  const content = (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>


      <div style={{
        background: "linear-gradient(135deg, #d4a44a,#f5d78e,#8b6914,#d4a44a,#f5d78e)",
        padding: "3px",
        borderRadius: "50%",
        boxShadow: `0 0 30px rgba(${g},${anim.glow * 0.5}), 0 0 60px rgba(${g},0.15)`,
        transform: `scale(${anim.pulse})`,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}>
 
        <div style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: "linear-gradient(to bottom, #1e2333, #141928, #0d1117)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          overflow: "hidden",
        }}>

          <span style={{
            position: "absolute", top: 0, left: "15%", right: "15%", height: "1px",
            background: `linear-gradient(90deg, transparent, rgba(${g},0.4), transparent)`,
            pointerEvents: "none",
          }} />

          <svg width={size * 0.65} height={size * 0.65} viewBox="0 0 40 40"
            style={{ transform: `rotate(${anim.spin}deg)` }}>
            <circle cx="20" cy="20" r="16" fill="none" stroke={`rgba(${g},0.15)`} strokeWidth="3" />
            <path d="M 20 4 A 16 16 0 0 1 36 20" fill="none" stroke={color}
              strokeWidth="3.5" strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 4px rgba(${g},0.8))` }} />
          </svg>
        </div>
      </div>

      {message && (
        <p style={{
          color,
          fontSize: "16px",
          letterSpacing: "2px",
          textTransform: "uppercase",
          textShadow: `0 0 12px rgba(${g},0.5)`,
          margin: 0,
          opacity: 0.9,
        }}>
          {message}
        </p>
      )}
    </div>
  );

  if (overlay) {
    return (
      <div style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.6)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 999,
      }}>
        {content}
      </div>
    );
  }

  return content;
}
