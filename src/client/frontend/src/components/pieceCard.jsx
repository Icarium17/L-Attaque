import Piece from "../components/piece.jsx";

export default function PieceCard({ piece }) {
  const isRed = piece.player == "RED";
  const cardColor = isRed
    ? "border-red-600/70 bg-red-950/40 shadow-[0_0_32px_rgba(220,38,38,0.5)]"
    : "border-blue-600/70 bg-blue-950/40 shadow-[0_0_32px_rgba(37,99,235,0.5)]";

  return (
    <div className={`relative flex items-center justify-center rounded-xl border-2 w-36 h-36 ${cardColor}`}>
      <div className="w-28 h-28 flex items-center justify-center">
        <Piece rank={piece.rank} type={piece.type} player={piece.player} playerColor={piece.player} revealed={true} />
      </div>
    </div>
  );
}