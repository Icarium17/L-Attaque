// React
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
// Hooks custom
import { useGameSync } from "../js/useGameSync.js";
import { usePlacement } from "../js/usePlacement.js";
import { useCellClick } from "../js/useCellClick.js";
// Utils Plateau
import { createEmptyBoard } from "../js/boardUtils.js";
import { isLake } from "../js/gameConfig.js";
// Components
import MainLayout from "../layouts/main-layout";
import Cell from "../components/cell.jsx";
import Piece from "../components/piece.jsx";
import Button from "../components/Button.jsx";
import Loading from "../components/loading.jsx";
import GameMessage from "../components/gameMessage.jsx";
import Timer from "../components/timer.jsx";
import TurnIndicator from "../components/turnIndicator.jsx";
import Notification from "../components/notification.jsx";
import Battle from "../pages/battle.jsx";
import End from "../pages/end.jsx";

// Assets
import backgroundGame from '../assets/images/background-game.png';


export default function Game() {
  const navigate = useNavigate();
  
  // État du plateau et du jeu
  const [board, setBoard] = useState(() => createEmptyBoard()); 
  const [turn, setTurn] = useState("BLUE");
  const [phase, setPhase] = useState("PLACEMENT"); // Phase placement à l'arrivée sur la page
  const [timeRemaining, setTimeRemaining] = useState([0, 0]);

  // État UI
  const [session, setSession] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [loading, setLoading] = useState(false);    
  const [error, setError] = useState("");

  // Ecran battle {  attacker: { rank: 10, type: "Marechal",  player: "RED"  },  defender: { rank: 2,  type: "Eclaireur", player: "BLUE" },  result:   "ATTACKER_WIN",}
  const [battleData, setBattleData] = useState(null); 

  // Ecran fin de jeu  {"WIN" | "LOSE"}
  const [gameResult, setGameResult] = useState(null); 

  // Vérifie la session au chargement, retour accueil si absente
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) { navigate("/"); return;}
      setSession({ username, key });
}, [navigate]);

  // Sync avec le serveur toutes les 1s en phase PLAYING
  useGameSync({ phase, setPhase, setTurn, setTimeRemaining, setBoard });
  
  // Logique placement (pool, drag, submit)
  const {
    pool, selectedPoolIndex,
    handlePoolClick, handlePlacementCellClick,
    handleAutoPlacement, handleResetPlacement, handleSubmitPlacement,
    handleDragStart: handlePlacementDragStart,
    handleBoardDrop: handlePlacementBoardDrop,
    handlePoolDrop,
  } = usePlacement({ board, setBoard, phase, setPhase, setTurn, loading, setLoading, setError, selectedCell, setSelectedCell });
 
  // Logique clic ou drag case (sélection + déplacement)
  const { handleCellClick,
    handleDragStart: handlePlayingDragStart,
    handleBoardDrop: handlePlayingBoardDrop,
} = useCellClick({
    board, setBoard, turn, setTurn, selectedCell, setSelectedCell,
    loading, setLoading, phase, setError, handlePlacementCellClick, isLake,
  });

  const activeDragStart = phase == "PLACEMENT" ? handlePlacementDragStart : phase == "PLAYING"   ? handlePlayingDragStart
                        : undefined;

  const activeBoardDrop = phase == "PLACEMENT" ? handlePlacementBoardDrop : phase == "PLAYING"   ? handlePlayingBoardDrop
                        : undefined;

return (
  <MainLayout
    title="Game - L'Attaque"
    background={backgroundGame}
    session={session}
    hideMenu={true}
  >
    <div className="relative flex items-center justify-center w-full h-full"> 
      <div className="absolute left-25 top-[4%] flex flex-col items-center w-110 shrink-0 px-4 space-y-5">
     
        {/* PLACEMENT */}
        {phase == "PLACEMENT" && (
          <>
            <GameMessage variant="title" title="Pièces à placer" />
            <Button variant="primary" onClick={handleAutoPlacement} disabled={pool.length == 0} fullWidth text="Placement Auto" />
            <Button variant="danger" onClick={handleResetPlacement} disabled={pool.length == 40} fullWidth text="Annuler" />

            {/* POOL */}
            <div className="grid grid-cols-5 gap-2 overflow-y-auto overflow-x-hidden w-full max-h-[60vh] mb-4 p-2 bg-black/20 rounded"
             onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }}
                onDrop={(e) => { e.preventDefault(); handlePoolDrop(); }}
              >
              {pool.map((piece, idx) => (
                <button
                    key={idx}
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.effectAllowed = "move";
                      handlePlacementDragStart({ type: "pool", index: idx });
                    }}
                    onClick={() => handlePoolClick(idx)}
                  className={`w-16 h-16 flex flex-col items-center justify-center font-bold rounded border-2 transition-transform mx-auto
                    ${selectedPoolIndex == idx
                      ? "border-yellow-400 bg-blue-600 text-white scale-110 shadow-cyan-500/50 shadow-md"
                      : "border-gray-500 bg-gray-800 text-blue-200 hover:border-blue-300"
                    }`}
                >
                  <Piece
                    rank={piece.rank}
                    type={piece.type}
                    player={piece.player}
                    playerColor="BLUE"
                    revealed={true}
                  />
                </button>
              ))}
            </div>
            {pool.length == 0 && (
              <Button variant="success" onClick={handleSubmitPlacement} loading={loading} fullWidth text="Valider" />
            )}
          </>
        )}

        {/* WAITING */}
        {phase == "WAITING" && (
          <div className="w-full py-10 flex flex-col items-center justify-center bg-black/30 rounded-lg border border-yellow-500/20 backdrop-blur-sm">
            <Loading message="Attente..." size={80} />
          </div>
        )}

        {/* PLAYING */}
        {phase == "PLAYING" && (
          <div className="flex flex-col items-center w-full">
            <GameMessage
              variant="title"
              title={turn.toUpperCase() == "BLUE" ? "VOTRE TOUR" : "TOUR ADVERSE"}
            />
          </div>
        )}

        {/* NOTIFICATION ERREUR */}
        {error && (
          <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm">
            <Notification
              variant="error"
              message={error}
              autoClose={3000}
              onClose={() => setError("")}
              className="w-full"
            />
          </div>
        )}
      </div>

    <div className="flex items-stretch gap-20">      
      {/* Timers */}
      {phase == "PLAYING" && (
        <div className="flex flex-col justify-between py-2">
          {/* {timeRemaining}*/}
          <Timer timeLeft={timeRemaining[1] || 0} color="RED"  turn={turn} onExpire={() => setError("Temps écoulé pour Red!")} />
          <TurnIndicator turn={turn} />
          <Timer timeLeft={timeRemaining[0] || 0} color="BLUE" turn={turn} onExpire={() => setError("Temps écoulé pour Blue!")} />
        </div>
      )}
      
  {/* Board */}
  <div className="relative grid grid-cols-10 gap-0.5 w-[min(950px,85vh)] shrink-0 aspect-square border-[6px] border-yellow-500/50 bg-gray-800 p-0.5 rounded shadow-2xl">
    {board.map((row, rowIndex) =>
      row.map((cell, colIndex) => (
        <Cell
          key={`${rowIndex}-${colIndex}`}
          row={rowIndex}
          col={colIndex}
          isLake={isLake(rowIndex, colIndex)}
          isSelected={selectedCell && selectedCell.row == rowIndex && selectedCell.col == colIndex}
          piece={cell}
          playerColor="BLUE"
          onClick={handleCellClick}
          onDragStart={activeDragStart}
          onDrop={activeBoardDrop}
        />
      ))
    )}
  {battleData && (
  <Battle
    attacker={battleData.attacker}
    defender={battleData.defender}
    result={battleData.result}
  />
)}
{gameResult && (
  <End result={gameResult} onClose={() => navigate("/lobby")} />
)}
  </div>
</div>
    </div>
  </MainLayout>
);}