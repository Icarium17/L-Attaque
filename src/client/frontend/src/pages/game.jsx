import { useEffect, useState } from "react";
import { useAsyncError, useNavigate } from "react-router";
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
  const [session, setSession] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [turn, setTurn] = useState("blue");
  const [phase, setPhase] = useState("placement");
  const [pool, setPool] =  useState(() => createPieces=("blue"));
  const [selectedPoolIndex, setSelectedPoolIndex] = useState(null);
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

  useEffect(() => {
      const key = localStorage.getItem("sessionKey");
      const username = localStorage.getItem("username");
      if (!key || !username) {
        navigate("/");
      } else {
        setSession({ username, key });
      }
    }, [navigate]);


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

  return (
    <MainLayout
      title="Game - L'Attaque"
      background={backgroundGame}
      session={session}
      hideMenu={true}
    >
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