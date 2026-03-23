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

function createEmptyBoard() {
  return Array.from({ length: 10 }, () => 
    Array(10).fill(null));
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
  const [board, setBoard] = useState(() => createEmptyBoard());
  const [error, setError] = useState("");

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
  };


const handleCellClick = (row, col) => {
    if (loading) return;

    if (phase == "placement") {
      if (row < 6) return; 
      const clickedPiece = board[row][col];

      if (selectedPoolIndex != null) {
        const newBoard = board.map((r) => [...r]);
        const newPool = [...pool];

        if (clickedPiece) {
          newPool.push(clickedPiece);
        }

        newBoard[row][col] = newPool[selectedPoolIndex];
        newPool.splice(selectedPoolIndex, 1);

        setBoard(newBoard);
        setPool(newPool);
        setSelectedPoolIndex(null);
        return;
      }

      if (!selectedCell) {

        if (clickedPiece) {
          setSelectedCell({ row, col });
        }
      } else {
        const newBoard = board.map((r) => [...r]);
        const piece1 = newBoard[selectedCell.row][selectedCell.col];
        const piece2 = newBoard[row][col];

        newBoard[selectedCell.row][selectedCell.col] = piece2;
        newBoard[row][col] = piece1;

        setBoard(newBoard);
        setSelectedCell(null); 
      }
      return; 
    }


    if (isLake(row, col)) return;

    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
    } else {
      setLoading(true);
      makeMove(selectedCell.row, selectedCell.col, row, col)
        .then((data) => {
          if (data?.result?.board) setBoard(data.result.board);
          if (data?.result?.turn) setTurn(data.result.turn);
          setSelectedCell(null);
        })
        .catch(() => setError("Erreur lors du mouvement"))
        .finally(() => setLoading(false));
    }
  };


  const handleAutoPlacement = () => {
      if (phase != "placement" || pool.length == 0) return;
      const newBoard = board.map((r) => [...r]);
      let currentPool = [...pool];  
 
      for (let row = 6; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
          if (!newBoard[row][col] && currentPool.length > 0) {
            const randomIndex = Math.floor(Math.random() * currentPool.length);
            const pieceChosen = currentPool.splice(randomIndex, 1)[0];
            newBoard[row][col] = pieceChosen;            
          }
        }
      }
      setBoard(newBoard);
      setPool([]);  
      setError("");
    };

 

  const handleResetPlacement = () => {
    if (phase != "placement") return;
    setBoard(createEmptyBoard());
    setPool(createPieces("blue"));
    setSelectedPoolIndex(null);
    setSelectedCell(null);
    setError("");
    setLoading(false);
  }

  const handleSubmitPlacement = () => {
    if (pool.length > 0) {
      setError("Il reste des pièces à placer!");
      return;
    }   

    setLoading(true);
    setError("");

    const placement = board.slice(6, 10).map((row) =>
      row.map((cell) => (cell ? { rank: cell.rank, name: cell.name } : null))
    );

    submitPlacement(placement)
      .then((data) => {
        if (data?.result?.error) {
          setError(data.result.error);
        } else {
          setPhase("playing");
        }
      })
      .catch(() => {
        setError("Erreur de connexion au serveur.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <MainLayout
      title="Game - L'Attaque"
      background={backgroundGame}
      session={session}
      hideMenu={true}
    >
      {phase == "placement" && (
        <div className="flex flex-col items-center w-80 shrink-0 px-4">
          <h2 className="text-white text-sm font-bold mb-2 text-center uppercase tracking-wider">
            Pièces à placer
          </h2>

          <button
            onClick={handleAutoPlacement}
            disabled={pool.length == 0}
            className="w-full mb-2 px-3 py-2 bg-blue-500 hover:bg-blue-400 text-white text-xs font-bold rounded shadow-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Placement Auto
          </button>

          <button
            onClick={handleResetPlacement}
            disabled={pool.length == 40}
            className="w-full mb-4 px-3 py-2 bg-red-500 hover:bg-red-400 text-white text-xs font-bold rounded shadow-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Annuler
          </button>
     
          <div className="grid grid-cols-4 gap-2 overflow-y-auto overflow-x-hidden w-full max-h-[60vh] mb-4 p-2 bg-black/20 rounded">
            {pool.map((piece, idx) => (
              <button
                key={idx}
                onClick={() => handlePoolClick(idx)}
                className={`w-12 h-12 flex flex-col items-center justify-center font-bold rounded border-2 transition-transform mx-auto
                  ${selectedPoolIndex == idx
                    ? "border-yellow-400 bg-blue-600 text-white scale-110 shadow-cyan-500/50 shadow-md"
                    : "border-gray-500 bg-blue-900 text-blue-200 hover:border-blue-300"
                  }`}
              >
                <span className="text-xs">{piece.rank}</span>
                <span className="text-[7px] leading-none opacity-80 mt-0.5">{piece.name}</span>
              </button>
            ))}
          </div>

          {error && <p className="text-red-400 text-[10px] mb-2 font-bold animate-pulse">{error}</p>}

         {pool.length == 0 && (
        <button
          onClick={handleSubmitPlacement}
          disabled={loading}
          className="w-full px-4 py-3 bg-green-600 text-white rounded font-black text-sm uppercase
            disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-green-600
            hover:bg-green-500 shadow-lg"
        >{loading ? "Chargement..." : "Valider"}
        </button>
      )}
        </div>
      )}        

      <div className="grid grid-cols-10 gap-0.5 w-full max-w-[min(600px,80vh)] aspect-square border-[6px] border-yellow-500/50 mx-auto bg-gray-800 p-0.5 rounded shadow-2xl">
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