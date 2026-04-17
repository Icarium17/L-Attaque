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
    <div className="relative flex flex-col items-center w-80 h-full">

      {/* Titre */}
      <div className="w-full flex justify-center z-10 mb-2">
        <img
          src={headerImg}
          alt={title}
          className="h-8 object-contain"
        />
      </div>

      {/* Cimetière */}
      <div
        className="w-full flex-1 bg-contain bg-no-repeat bg-top flex flex-col items-center pt-[45%] px-5"
        style={{ backgroundImage: `url(${graveyardBg})` }}
      >
        <div className="flex flex-col items-center gap-y-0.5 overflow-y-auto w-full flex-1 scrollbar-hide">
          {PIECE_TYPES.map(({ type, total }) => {
            const count = counts[type] ?? 0;
            return(
            <div key={type} className="flex items-center justify-center gap-2 h-16 w-full">
              <div className="w-16 h-16 shrink-0">
                <Piece
                  type={type}
                  player={isCapture ? "RED" : "BLUE"}
                  revealed={true}
                />
              </div>
              <span className={`font-bold text-2xl min-w-17 ${ count >0 ? "text-amber-300" :"text-amber-600"}`}>
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