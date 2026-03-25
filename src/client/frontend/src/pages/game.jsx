import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { makeMove ,submitPlacement} from "../services/gameService.js";

import MainLayout from "../layouts/main-layout";
import backgroundGame from '../assets/images/background-game.png';
import Cell from "../components/cell.jsx";
import Button from "../components/Button.jsx";
import GameMessage from "../components/gameMessage.jsx";

/*
  Cases d'eau: pas de déplacement.
*/
const LAKES = [
  "4-2", "4-3", "5-2", "5-3",
  "4-6", "4-7", "5-6", "5-7",
];

/*
  Configuration des pièces: rank, type, nombre
*/

const PIECES_CONFIG = [
  { rank: "B", type: "Bombe", count: 6 },
  { rank: "10", type: "Marechal", count: 1 },  
  { rank: "9", type: "General", count: 1 },   
  { rank: "8", type: "Colonel", count: 2 },
  { rank: "7", type: "Major", count: 3 },      
  { rank: "6", type: "Capitaine", count: 4 },
  { rank: "5", type: "Lieutenant", count: 4 },
  { rank: "4", type: "Sergent", count: 4 },
  { rank: "3", type: "Demineur", count: 5 },  
  { rank: "2", type: "Eclaireur", count: 8 },  
  { rank: "1", type: "Espion", count: 1 },
  { rank: "D", type: "Drapeau", count: 1 },
];
/*
  Vérifie si une case est eau
*/
function isLake(row, col) {
  return LAKES.indexOf(`${row}-${col}`) != -1;
}

/*
  Génère toutes les pièces dans le pool
*/
function createPieces(player) {
  const pieces = [];
  for (let i = 0; i < PIECES_CONFIG.length; i++) {
    const config = PIECES_CONFIG[i];
    for (let j = 0; j < config.count; j++) {
      pieces.push({ rank: config.rank, type: config.type, player, revealed: false });
    }
  }
  return pieces;
}

/*
  Crée un plateau 10x10 vide.
*/
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
  const [pool, setPool] = useState(() => createPieces("blue"));  // on definit pour l instant le joueur comme blue
  const [board, setBoard] = useState(() => createEmptyBoard());
  const [error, setError] = useState("");

   /*
    Vérifie la session au chargement si l'utilisateur n'a pas de session retour accueil.
  */
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) {
      navigate("/");
    } else {
      setSession({ username, key });
    }
  }, [navigate]);


  /*
    Clic sur une pièce du pool alors sélection.
  */
  const handlePoolClick = (index) => {
    if (phase != "placement")
      return;
    setSelectedPoolIndex(index);
    setSelectedCell(null);
  };


  /*
  Gestion du clic sur une case:
  Phase de placement :
  si une pièce du pool est sélectionnée on la pose
  si une case est sélectionnée, on peut déplacer/échanger
  double clic sur une pièce posée => retour dans le pool
*/
const handleCellClick = (row, col) => {
    if (loading) return;

    if (phase == "placement") {
      if (row < 6) return; 
      const clickedPiece = board[row][col];

      // Pièce du pool choisie : on la place sur la case cliquée
      if (selectedPoolIndex != null) {
        const newBoard = board.map((r) => [...r]);
        const newPool = [...pool];

      // Si une pièce existe sur la case,retourne dans le pool
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

      // Sélectionne une pièce placée
      if (!selectedCell) {
        if (clickedPiece) {
          setSelectedCell({ row, col });
        }
      } else {
        // Double-clic la même case -> retour au pool
        if (selectedCell.row == row && selectedCell.col == col) {
          const newBoard = board.map((r) => [...r]); // copie du board
          newBoard[row][col] = null; // met la case a null
          setBoard(newBoard);
          setPool([...pool, board[row][col]]); // ajoute la piece a la fin du board
          setSelectedCell(null);
          return;
        }

        // Sinon, switche entre la case sélectionnée et la case cliquée
        const newBoard = board.map((r) => [...r]);
        const piece1 = newBoard[selectedCell.row][selectedCell.col];
        const piece2 = newBoard[row][col];
        newBoard[selectedCell.row][selectedCell.col] = piece2;
        newBoard[row][col] = piece1;
        setBoard(newBoard);
        setSelectedCell(null);
      }}

    if (isLake(row, col)) return;

    // Premier clic sélectionne une piece
    if (!selectedCell) {
      const piece = board[row][col];
      if (!piece || piece.player != turn) return;
      setSelectedCell({ row, col });
    } else {
      // Deuxième clic validation du déplacement via l'API
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

   /*
    Placement automatique aléatoire 
  */

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
 
   /*
    Réinitialise complètement le placement 
    */
  const handleResetPlacement = () => {
    if (phase != "placement") return;
    setBoard(createEmptyBoard());
    setPool(createPieces("blue"));
    setSelectedPoolIndex(null);
    setSelectedCell(null);
    setError("");
    setLoading(false);
  }

  /*
    Envoie le placement final au serveur. 
  */
  const handleSubmitPlacement = () => {
    if (pool.length > 0) {
      setError("Il reste des pièces à placer!");
      return;
    }   

    setLoading(true);
    setError("");

    const placement = [];

    // On parcourt tout le board 
      board.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
          if (cell) {
            placement.push({
              rank: cell.rank,
              type: cell.type,
              position: [colIndex, rowIndex] 
            });
          }
        });
      });

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
        <div className="flex flex-col items-center w-110 shrink-0 px-4  space-y-5">
          <GameMessage variant="title" title="Pièces à placer"></GameMessage>
          <Button
            variant="primary"
            onClick={handleAutoPlacement}
            disabled={pool.length == 0}
            fullWidth
            text="Placement Auto"
          />
          <Button
            variant="danger"
            onClick={handleResetPlacement}
            disabled={pool.length == 40}
            fullWidth
            text="Annuler"
          />
     
          <div className="grid grid-cols-5 gap-2 overflow-y-auto overflow-x-hidden w-full max-h-[60vh] mb-4 p-2 bg-black/20 rounded">
            {pool.map((piece, idx) => (
              <button
                key={idx}
                onClick={() => handlePoolClick(idx)}
                className={`w-16 h-16 flex flex-col items-center justify-center font-bold rounded border-2 transition-transform mx-auto
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
            <Button
              variant="success"
              onClick={handleSubmitPlacement}
              loading={loading}
              fullWidth
              text={loading ? "Chargement..." : "Valider"}
            />
          )}
        </div>
      )}        

      <div className="grid grid-cols-10 gap-0.5 w-full max-w-[min(600px,80vh)] aspect-square border-[6px] border-yellow-500/50 ml-42 bg-gray-800 p-0.5 rounded shadow-2xl">
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