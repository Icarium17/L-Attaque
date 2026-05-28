import PieceCard from "../components/pieceCard.jsx";

const PIECES_INFO = [
  { rank: 10, type: "Marechal",  count: 1, desc: "La plus forte. Craint l'Espion et les Bombes." },
  { rank: 9,  type: "General",   count: 1, desc: "Ne craint que le Maréchal et les Bombes." },
  { rank: 8,  type: "Colonel",   count: 2, desc: "Bat les rangs de 1 à 7." },
  { rank: 7,  type: "Major",     count: 3, desc: "Bat les rangs de 1 à 6." },
  { rank: 6,  type: "Capitaine", count: 4, desc: "Bat les rangs de 1 à 5." },
  { rank: 5,  type: "Lieutenant", count: 4, desc: "Bat les rangs de 1 à 4." },
  { rank: 4,  type: "Sergent",   count: 4, desc: "Bat les rangs de 1 à 3." },
  { rank: 3,  type: "Demineur",  count: 5, desc: "Le seul à pouvoir détruire les Bombes." },
  { rank: 2,  type: "Eclaireur", count: 8, desc: "Se déplace de plusieurs cases d'un coup." },
  { rank: 1,  type: "Espion",    count: 1, desc: "Faible, mais tue le Maréchal s'il attaque." },
  { rank: "B", type: "Bombe",     count: 6, desc: "Immobile. Élimine tout attaquant (sauf le Démineur)." },
  { rank: "F", type: "Drapeau",   count: 1, desc: "Immobile. Le perdre entraîne la défaite." },
];

export default function PieceGallery({ playerColor = "BLUE" }) {
  return (
    <div className="min-h-full w-full flex items-center justify-center py-4 fhd:py-6 4k:py-10">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-1 fhd:gap-x-10 fhd:gap-y-2 4k:gap-x-16 4k:gap-y-4 justify-items-center w-full max-w-6xl fhd:max-w-7xl 4k:max-w-400">
        {PIECES_INFO.map((p) => (
          <div key={p.type} className="flex flex-col items-center text-center group">
            <div className="scale-65 fhd:scale-75 4k:scale-100 transition-transform">
              <PieceCard piece={{ rank: p.rank, type: p.type, player: playerColor }} />
            </div>

            <h3 className="text-yellow-300 font-bold text-base fhd:text-lg 4k:text-2xl uppercase tracking-wider">
              {p.type}
            </h3>
            <p className="text-white text-sm fhd:text-md 4k:text-xl font-semibold">
              Quantité : <span className="text-yellow-500">{p.count}</span>
            </p>
            <p className="text-gray-200 text-xs fhd:text-sm 4k:text-lg leading-tight max-w-40 fhd:max-w-45 4k:max-w-64 italic">
              {p.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}