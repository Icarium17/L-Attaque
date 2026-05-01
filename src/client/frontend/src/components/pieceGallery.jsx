import PieceCard from "../components/pieceCard.jsx";

const PIECES_INFO = [
  { rank: 10, type: "Marechal",   count: 1, desc: "La plus forte. Craint l'Espion et les Bombes." },
  { rank: 9,  type: "General",    count: 1, desc: "Ne craint que le Maréchal et les Bombes." },
  { rank: 8,  type: "Colonel",    count: 2, desc: "Bat les rangs de 1 à 7." },
  { rank: 7,  type: "Major",      count: 3, desc: "Bat les rangs de 1 à 6." },
  { rank: 6,  type: "Capitaine",  count: 4, desc: "Bat les rangs de 1 à 5." },
  { rank: 5,  type: "Lieutenant", count: 4, desc: "Bat les rangs de 1 à 4." },
  { rank: 4,  type: "Sergent",    count: 4, desc: "Bat les rangs de 1 à 3." },
  { rank: 3,  type: "Demineur",   count: 5, desc: "Le seul à pouvoir détruire les Bombes." },
  { rank: 2,  type: "Eclaireur",  count: 8, desc: "Se déplace de plusieurs cases d'un coup." },
  { rank: 1,  type: "Espion",     count: 1, desc: "Faible, mais tue le Maréchal s'il attaque en premier." },
  { rank: "B",type: "Bombe",      count: 6, desc: "Immobile. Élimine tout attaquant (sauf le Démineur)." },
  { rank: "F",type: "Drapeau",    count: 1, desc: "Immobile. Le perdre entraîne la défaite." },
];

export default function PieceGallery({ playerColor = "RED" }) {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 gap-4 sm:gap-6 p-6 justify-items-center w-full max-w-5xl mx-auto min-h-full content-center">
      {PIECES_INFO.map((p) => (
        <div key={p.type} className="flex flex-col items-center text-center">
          <PieceCard piece={{ rank: p.rank, type: p.type, player: playerColor }} />
          <h3 className="mt-2 text-yellow-300 font-bold text-lg">{p.type}</h3>
          <p className="text-white text-sm">×{p.count}</p>
          <p className="text-gray-200 text-xs mt-1 max-w-45">{p.desc}</p>
        </div>
      ))}
    </div>
  );
}