import arrow from "../assets/arrow.svg";

export default function MoveArrow({ from, to, color }) {
  const dx = to.col - from.col;
  const dy = to.row - from.row;

  let rotation = 0;
  if (dx > 0) rotation = 0;          // droit
  else if (dx < 0) rotation = 180;   // gauche
  else if (dy > 0) rotation = 90;    // bas
  else if (dy < 0) rotation = -90;   // haut

  const tint = color === "RED"
    ? "invert(45%) sepia(95%) saturate(2000%) hue-rotate(340deg) brightness(95%)"
    : "invert(45%) sepia(95%) saturate(1500%) hue-rotate(200deg) brightness(100%)";

  return (
    <div className="absolute inset-0 z-30 pointer-events-none flex items-center justify-center">
      <img
        src={arrow}
        alt=""
        className="animate-pulse"
        style={{
          width: "60%",
          height: "60%",
          transform: `rotate(${rotation}deg)`,
          filter: `${tint} drop-shadow(0 0 3px rgba(0,0,0,0.9))`,
          transition: "transform 0.2s ease",
        }}
      />
    </div>
  );
}