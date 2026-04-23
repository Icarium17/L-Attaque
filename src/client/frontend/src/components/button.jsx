import { useState, useEffect, useRef } from "react";

/*
 Variantes de boutons avec 4 props:
- border → Couleurs de la bordure 
- bg → Les couleurs de fond du bouton: base, hover, pressed 
- color →  Couleur du texte : normal, hover, pressed 
- glow  → "Couleur pour les effets lumineux : rgb

Pour personnaliser : la prop `style` écrase tout.
Ex: Button style={{ color: '#fff', backgroundImage: 'url(...)' }}
 */
const VARIANTS = {
  primary: {
    border: '#d4a44a,#f5d78e,#8b6914,#d4a44a,#f5d78e',
    bg:     ['#1e2333,#141928,#0d1117','#272d42,#1a2030,#111722','#0d1117,#080b10'],
    color:  ['#d4a44a','#f0c860','#b8902e'],
    glow:   '212,164,74',
  },
  secondary: {
    border: '#777,#aaa,#555,#777,#aaa',
    bg:     ['#2a2a2a,#1a1a1a', '#363636,#252525', '#1a1a1a,#111'],
    color:  ['#ccc', '#f0f0f0', '#999'],
    glow:   '200,200,200',
  },
  danger: {
    border: '#c0392b,#ff6b5a,#8b1a1a,#c0392b,#ff6b5a',
    bg:     ['#1e1111,#150b0b', '#2a1515,#1e0e0e', '#120909,#0a0505'],
    color:  ["#eFFFFF", '#ff7b6a', '#a33025'],
    glow:   '231,76,60',
  },
  success: {
    border: '#27ae60,#6fcf97,#1a7a42,#27ae60,#6fcf97',
    bg:     ['#111e16,#0b150e', '#1a2e20,#112218', '#0b150e,#060d08'],
    color:  ['#eafff1', '#6fcf97', '#27ae60'],
    glow:   '111,207,151',
  },
  ghost: {
    border: null, 
    bg: ['transparent', 'transparent', 'transparent'],
    color: ['#000000', '#333333', '#FF0000'], 
    glow: '0,0,0',  
  },
};

/*
 COMPOSANT BUTTON
 Props :
   variant    → "primary" | "secondary" | "danger" | "ghost" 
   children   → Contenu JSX du bouton (prioritaire sur text)
   text       → Texte alternatif si pas de children
   onClick    → Callback au clic
   disabled   → Grise le bouton et bloque le clic
   loading    → Affiche un spinner et bloque le clic
   icon       → Élément affiché à gauche du texte
   iconRight  → Élément affiché à droite du texte
   fullWidth  → Le bouton prend toute la largeur
   style      →  écrase les styles de la variante
   className  → Classes Tailwind supplémentaires
   type       → par défaut: "button"
 */

export default function Button({
  type, onClick, className, text, children, style,
  variant = "primary", disabled, loading, icon, iconRight, fullWidth,
}) {
  const [hovered, setHovered] = useState(false);
  const [pressed, setPressed] = useState(false);

  /*
   Animation des 3 effets derrière le texte quand Le bouton est hovered ou loading  ou disabled 
   shine → Position X du trait de lumière (-100% à +200%)
   glow    → Opacité  entre 0.3 et 0.6
   spin    → Angle de rotation du spinner de chargement 
   */
  const [anim, setAnim] = useState({ shine: -100, glow: 0.3, spin: 0 });
  const rafRef = useRef(null);

  useEffect(() => {
    const needsAnim = (hovered && !disabled) || loading;
    if (!needsAnim) {
      setAnim({ shine: -100, glow: 0.3, spin: 0 });
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }

    const tick = (t) => {
      setAnim({
        shine: -100 + ((t % 1500) / 1500) * 300,
        glow: 0.3 + 0.15 * (1 + Math.sin(t / 500)),
        spin: (t / 2) % 360,
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [hovered, disabled, loading]);

  /*
    Etat
    state = 0 (base), 1 (hover), ou 2 (pressed)
   */
  const v = VARIANTS[variant] || VARIANTS.primary;
  const state = disabled ? 0 : pressed ? 2 : hovered ? 1 : 0;
  const g = v.glow; // raccourci pour la couleur RGB des effets

  /*
   Bordure dorée
   Le boxShadow change selon l'état :base,hover,pressed
   */

  const borderStyle = v.border ? {
    background: `linear-gradient(135deg, ${v.border})`,
    padding: '3px',
    borderRadius: '12px',
    boxShadow: state == 1
      ? `0 8px 32px rgba(0,0,0,0.6), 0 0 40px rgba(${g},0.35)`
      : state == 2
      ? `0 2px 10px rgba(0,0,0,0.6)`
      : `0 4px 20px rgba(0,0,0,0.6), 0 0 25px rgba(${g},0.2)`,
  } : {
    padding: '0px',
    borderRadius: '0px',
    border: 'none', 
    boxShadow: 'none',  
    background: 'none',
    outline: 'none',  
    ...(variant == 'ghost' ? { 
      boxShadow: 'none !important',
      appearance: 'none',
      border: '0px solid transparent' 
    } : {})
  };
  /*
   STYLE DU BOUTON INTÉRIEUR 
   On peut mettre son propre Background
   */
  const bgValue = v.bg[state].includes('rgba')
    ? v.bg[state]
    : `linear-gradient(to bottom, ${v.bg[state]})`;

  const btnStyle = {
    background: bgValue,
    color: v.color[state],
    border: 'none',
    
    borderRadius: variant == 'ghost' ? '0px' : '9px', 
    textTransform: 'uppercase',
    letterSpacing: '4px',
    fontWeight: '700',
    textShadow: `0 0 ${state == 1 ? 20 : 12}px rgba(${g},${state == 1 ? 0.7 : 0.4})`,
    width: '100%',
    position: 'relative',
    overflow: 'hidden',         
    transition: 'all 0.2s ease',
    ...(pressed ? { transform: 'translateY(1px)' } : {}),
    ...(disabled ? { opacity: 0.45, cursor: 'not-allowed', filter: 'grayscale(0.6)' } : {}),
    ...style, // les styles custom écrasent ici les styles de la variante
  };

  return (
    //  Bordure dorée 
    <div 
    className={className}
    style={{
      ...borderStyle,
      display: 'flex',
      width: '100%',
      transition: 'all 0.3s ease',
      ...(disabled ? { opacity: 0.45, filter: 'grayscale(0.6)' } : {}),
    }}>

      {/*BOUTON : fond sombre avec les effets lumineux*/}
      <button
        type={type || "button"}
        onClick={disabled || loading ? undefined : onClick}
        disabled={disabled || loading}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => { setHovered(false); setPressed(false); }}
        onMouseDown={() => setPressed(true)}
        onMouseUp={() => setPressed(false)}
        className={
          "px-8 py-4 font-semibold tracking-wide whitespace-nowrap "
          + (fullWidth ? "w-full " : "")
          + (disabled || loading ? "" : "cursor-pointer ")
          
        }
        style={btnStyle}
      >
        {/*
          Traits de lumiere en diagonal
          */}
        {!disabled && hovered && (
          <span style={{
            position: 'absolute', top: 0, left: `${anim.shine}%`,
            width: '60%', height: '100%',
            background: `linear-gradient(90deg, transparent, rgba(${g},0.2), transparent)`,
            transform: 'skewX(-20deg)', pointerEvents: 'none',
          }} />
        )}

        {/*
        Reflets         
          */}
       {variant != 'ghost' && (
        <span style={{
          position: 'absolute', top: 0, left: '10%', right: '10%', height: '1px',
          background: `linear-gradient(90deg, transparent, rgba(${g},${hovered ? 0.5 : 0.2}), transparent)`,
          transition: 'all 0.3s ease', pointerEvents: 'none',
        }} />
      )}

        {/*
        Glow
          */}
        {!disabled && hovered && (
          <span style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%,-50%)', width: '80%', height: '80%',
            background: `radial-gradient(ellipse, rgba(${g},${anim.glow * 0.15}), transparent 70%)`,
            pointerEvents: 'none',
          }} />
        )}

        {/*
           icône + texte + icône droite 
           en mode loading: l'icône est remplacée par un spinner
          */}
        <span className="flex items-center justify-center gap-2" style={{ position: 'relative', zIndex: 1 }}>
          {loading ? (
            <span style={{
              display: 'inline-block', width: 16, height: 16, borderRadius: '50%',
              border: '2px solid rgba(255,255,255,0.15)',
              borderTopColor: v.color[0],
              transform: `rotate(${anim.spin}deg)`,
            }} />
          ) : icon ? <span>{icon}</span> : null}
          <span>{children || text}</span>
          {iconRight && !loading && <span>{iconRight}</span>}
        </span>
      </button>
    </div>
  );
}
