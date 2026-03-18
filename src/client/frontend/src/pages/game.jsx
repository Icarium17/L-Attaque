import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Cell from "../components/cell.jsx";
import backgroundGame from '../assets/images/background-game.png';

const LAKES = [
  "4-2", "4-3", "5-2", "5-3",
  "4-6", "4-7", "5-6", "5-7",
];

function isLake(row, col) {
  return LAKES.indexOf(`${row}-${col}`) !== -1;
}

export default function Game() {
  const [session, setSession] = useState(null);
  const navigate = useNavigate();

  const [board, setBoard] = useState(() =>
    Array.from({ length: 10 }, () => Array(10).fill(null))
  );

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) {
      navigate("/");
    } else {
      setSession({ username, key });
    }
  }, [navigate]);



const [selectedCell, setSelectedCell] = useState(null);

const handleCellClick = (row, col) => {
  if (isLake(row, col)) return;
  setSelectedCell({ row, col });
  console.log(`Cell: ${row}, Col: ${col}`);
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
            isSelected={selectedCell && selectedCell.row === rowIndex && selectedCell.col === colIndex}
            piece={cell}
            onClick={handleCellClick}
            />
          ))
        )}
      </div>
    </MainLayout>
  );
}