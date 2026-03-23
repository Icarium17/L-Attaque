import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Cell from "../components/cell.jsx";
import backgroundGame from '../assets/images/background-game.png';
import { makeMove ,submitPlacement} from "../services/gameService.js";


const LAKES = [
  "4-2", "4-3", "5-2", "5-3",
  "4-6", "4-7", "5-6", "5-7",
];

const PIECES_CONFIG = [
  { rank: "B", name: "Bombe", count: 6 },
  { rank: "10", name: "Marechal", count: 1 },
  { rank: "9", name: "General", count: 1 },
  { rank: "8", name: "Colonel", count: 2 },
  { rank: "7", name: "Commandant", count: 3 },
  { rank: "6", name: "Capitaine", count: 4 },
  { rank: "5", name: "Lieutenant", count: 4 },
  { rank: "4", name: "Sergent", count: 4 },
  { rank: "3", name: "Demineur", count: 5 },
  { rank: "2", name: "Eclaireur", count: 8 },
  { rank: "1", name: "Espion", count: 1 },
  { rank: "D", name: "Drapeau", count: 1 },
];

function isLake(row, col) {
  return LAKES.indexOf(`${row}-${col}`) != -1;
}

function createPieces(player) {
  const pieces = [];
  for (let i = 0; i < PIECES_CONFIG.length; i++) {
    const config = PIECES_CONFIG[i];
    for (let j = 0; j < config.count; j++) {
      pieces.push({ rank: config.rank, name: config.name, player, revealed: false });
    }
  }
  return pieces;
}

// Fonction creer un board par défaut
function createInitialBoard() {
  const board = Array.from({ length: 10 }, () => Array(10).fill(null));

  const redPieces = createPieces("red");
  let i = 0;
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 10; col++) {
      board[row][col] = redPieces[i++];
    }
  }

  const bluePieces = createPieces("blue");
  i = 0;
  for (let row = 6; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
      board[row][col] = bluePieces[i++];
    }
  }
  return board;
}


export default function Game() {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [loading, setLoading] = useState(false);
  const [turn, setTurn] = useState("blue");
  const [phase, setPhase] = useState("placement");
  const [selectedPoolIndex, setSelectedPoolIndex] = useState(null);
  const [pool, setPool] = useState(() => createPieces("blue"));
  const [board, setBoard] = useState(() =>  Array.from({length:10},() =>Array(10).fill(null)))


  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) {
      navigate("/");
    } else {
      setSession({ username, key });
    }
  }, [navigate]);


  const handlePoolClick = (index) => {
    if (phase != "placement")
      return;
    setSelectedPoolIndex(index);
    setSelectedCell(null);
  }
 
  const handleCellClick = (row, col) => {
    if (isLake(row, col)) return;
    if (loading) return;

    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
      return;
    } 
    setLoading(true);
    makeMove(selectedCell.row, selectedCell.col, row, col).then(data => {
      if (data && data.result && data.result.board) {
        setBoard(data.result.board);
      }
      if (data && data.result && data.result.turn) {
        setTurn(data.result.turn);
      }
      setSelectedCell(null);
      setLoading(false);
    });
  };

  const  handleSubmitPlacement = () =>{

  };

 
  return (
    <MainLayout
      title="Game - L'Attaque"
      background={backgroundGame}
      session={session}
      hideMenu={true}
    >
      {/* ===== POOL À GAUCHE EN PHASE PLACEMENT ===== */}
      {phase == "placement" && (
        <div className="flex flex-col items-center w-32 shrink-0">
          <h2 className="text-white text-sm font-bold mb-2 text-center">
            Pièces à placer
          </h2>

          {/* Grille 2 colonnes de boutons */}
          <div className="grid grid-cols-2 gap-1 overflow-y-auto max-h-[80vh] mb-3">
            {pool.map((piece, idx) => (
              <button
                key={idx}
                onClick={() => handlePoolClick(idx)}
                className={`w-12 h-12 text-xs font-bold rounded border-2 
                  ${selectedPoolIndex == idx
                    ? "border-yellow-400 bg-blue-600 text-white scale-110"
                    : "border-gray-400 bg-blue-800 text-white hover:border-blue-400"
                  }`}
              >
                {piece.rank}
                <div className="text-[8px]">{piece.name}</div>
              </button>
            ))}
          </div>

          {/* Bouton Prêt */}
          <button
            onClick={handleSubmitPlacement}
            disabled={pool.length > 0 || loading}
            className="px-4 py-2 bg-green-600 text-white rounded font-bold text-sm
              disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-500"
          >
            {loading ? "Envoi..." : "Prêt!"}
          </button>

          {/* Pièces restantes */}
          {pool.length > 0 && (
            <p className="text-gray-300 text-xs mt-1">
              Reste: {pool.length}
            </p>
          )}
        </div>
      )}

      {/* ===== BOARD ===== */}
      <div className="grid grid-cols-10 gap-0.5 w-full max-w-[min(600px,80vh)] aspect-square border-[6px] border-yellow-400 mx-auto bg-gray-300 rounded-sm shadow-2xl">
        {board.map((row, rowIndex) =>
          row.map((cell, colIndex) => (
            <Cell
              key={`${rowIndex}-${colIndex}`}
              row={rowIndex}
              col={colIndex}
              isLake={isLake(rowIndex, colIndex)}
              isSelected={selectedCell && selectedCell.row == rowIndex && selectedCell.col == colIndex}
              piece={cell}
              onClick={handleCellClick}
            />
          ))
        )}
      </div>
    </MainLayout>
  );
}