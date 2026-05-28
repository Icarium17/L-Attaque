import graveyardBg from "../assets/images/graveyard.svg";
import graveyardTextCapture from "../assets/images/graveyard-text-capture.svg";
import graveyardTextLost from "../assets/images/graveyard-text-lost.svg";
import Piece from "../components/piece.jsx";

const PIECE_TYPES = [
  { type: 'Marechal', total: 1 },
  { type: 'General', total: 1 },
  { type: 'Colonel', total: 2 },
  { type: 'Major', total: 3 },
  { type: 'Capitaine', total: 4 },
  { type: 'Lieutenant', total: 4 },
  { type: 'Sergent', total: 4 },
  { type: 'Demineur', total: 5 },
  { type: 'Eclaireur', total: 8 },
  { type: 'Espion', total: 1 },
  { type: 'Bombe', total: 6 },
];

export default function Graveyard({ title , counts ={}}) {
  const isCapture = title == "Pièces Capturées";
  const headerImg = isCapture ? graveyardTextCapture : graveyardTextLost;


  return (
    <div className="relative flex flex-col items-center justify-center w-52 fhd:w-64 4k:w-80 h-full 4k:h-[102%]">
    {/* Titre */}
      <div className="w-full flex justify-center z-10 mb-1 fhd:mb-1.5 4k:mb-2">
        <img
          src={headerImg}
          alt={title}
          className="h-5 fhd:h-6 4k:h-8 object-contain"
        />
      </div>

      {/* Cimetière */}
      <div
        className="w-full flex-1 bg-contain bg-no-repeat bg-center flex flex-col items-center justify-center px-3 fhd:px-4 4k:px-5"
        style={{ backgroundImage: `url(${graveyardBg})` }}
      >       
        <div className="flex flex-col items-center gap-y-0.5 fhd:gap-y-1 w-full py-[15%] fhd:pt-[22%] fhd:pb-[0%] 4k:pt-[30%] 4k:pb-[10%] overflow-hidden">
          {PIECE_TYPES.map(({ type, total }) => {
            const count = counts[type] ?? 0;
            return(
            <div key={type} className="flex items-center justify-center gap-1 fhd:gap-1.5 4k:gap-2 h-9 fhd:h-11 4k:h-14 w-full">
              <div className="w-9 h-9 fhd:w-12 fhd:h-12 4k:w-16 4k:h-16 shrink-0">
                <Piece
                  type={type}
                  player={isCapture ? "RED" : "BLUE"}
                  revealed={true}
                />
              </div>
             <span className={`font-bold text-base fhd:text-lg 4k:text-2xl min-w-10 fhd:min-w-12 4k:min-w-17 ${ count > 0 ? "text-amber-300" :  "text-stone-100" }`}>
              {count}/{total}
            </span>
            </div>
          );
          })}       
        </div>
      </div>
    </div>
  );
}