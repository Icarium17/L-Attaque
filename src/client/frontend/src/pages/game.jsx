// React
import { useEffect, useState, useRef } from "react";
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
import YourTurn from "../components/yourTurn.jsx";
import Graveyard from "../components/graveyard.jsx";
import Panel from "../components/panel.jsx";

// Assets
import backgroundGame from '../assets/images/background-game.png';
import backgroundScore from '../assets/images/background-score.png';  

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

  // Etats cimetières
  const [capturedPieces, setCapturedPieces] = useState({});
  const [lostPieces, setLostPieces] = useState({});

  // Etats des scores
  const [scoreBlue, setScoreBlue] = useState(0);
  const [scoreRed, setScoreRed] = useState(0);

  // Ecran fin de jeu  {"WIN" | "LOSE"}
  const [gameResult, setGameResult] = useState(null); 

  // PopUp YourTurn
  const [showYourTurn, setShowYourTurn] = useState(false);

  // Affiche la popup "Your Turn" quand le tour passe à BLUE après RED
  const setTurnWithPop = (newTurn) => {
  setTurn(prev => {
    if (newTurn == "BLUE" && prev == "RED") {
      setShowYourTurn(true);
      setTimeout(() => setShowYourTurn(false), 900);
    }
    return newTurn;
  });
};

 // Affiche la popup au début de la phase PLAYING si c'est déjà le tour de BLUE
  useEffect(() => {
  if (phase == "PLAYING" && turn == "BLUE") {
    setShowYourTurn(true);
    setTimeout(() => setShowYourTurn(false), 900);
  }
  }, [phase]);

  // Vérifie la session au chargement, retour accueil si absente
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) { navigate("/"); return;}
      setSession({ username, key });
}, [navigate]);

  // Hook custom : Sync serveur (polling) : board, turn, timers, scores, battle, fin de partie
  useGameSync({ phase, setPhase, setTurn: setTurnWithPop, setTimeRemaining, setBoard, setBattleData, setGameResult, setCapturedPieces, setLostPieces , setScoreBlue, setScoreRed });
  
  // Destructuration de usePlacement : retourne le pool de pièces à placer,l'index sélectionné, et les fonctions de placement (clic, drag & drop, auto, reset, envoi au serveur)
  // { propriétés extraites } = usePlacement(params)  | handleDragStart/handleBoardDrop renommés pour éviter conflit avec useCellClick
  const {
    pool, selectedPoolIndex,
    handlePoolClick, handlePlacementCellClick,handleAutoPlacement, handleResetPlacement, handleSubmitPlacement,
    handleDragStart: handlePlacementDragStart,handleBoardDrop: handlePlacementBoardDrop, handlePoolDrop} = 
    usePlacement({ board, setBoard, phase, setPhase, setTurn, loading, setLoading, setError, selectedCell, setSelectedCell });
 
  // Logique clic ou drag case (sélection + déplacement)
  // { propriétés extraites } = useCellClick(params)
  const { 
    handleCellClick,handleDragStart: handlePlayingDragStart,handleBoardDrop: handlePlayingBoardDrop,} = 
    useCellClick({board, setBoard, turn, setTurn, selectedCell, setSelectedCell,loading, setLoading, phase, setError, handlePlacementCellClick, isLake});

  // Sélectionne le bon handler drag/drop selon la phase (PLACEMENT ou PLAYING)
  const activeDragStart = phase == "PLACEMENT" ? handlePlacementDragStart : phase == "PLAYING"   ? handlePlayingDragStart: undefined;
  const activeBoardDrop = phase == "PLACEMENT" ? handlePlacementBoardDrop : phase == "PLAYING"   ? handlePlayingBoardDrop: undefined;


return (
  <MainLayout
    title="Game - L'Attaque"
    background={backgroundGame}
    session={session}
    hideMenu={true}
  >
    <div className="relative flex items-center justify-center w-full h-full overflow-hidden">

      {/* PLACEMENT */}
      {phase == "PLACEMENT" && (
        <div className="absolute left-[15%] top-1/2 -translate-y-1/2 flex flex-col items-center w-96 z-20 space-y-5">
          <GameMessage variant="title" title="Pièces à placer" />
          <Button variant="primary" onClick={handleAutoPlacement} disabled={pool.length == 0} fullWidth text="Placement Auto" />
          <Button variant="danger" onClick={handleResetPlacement} disabled={pool.length == 40} fullWidth text="Annuler" />

          {/* POOL */}
          <div className="grid grid-cols-4 place-items-center gap-3 overflow-y-auto w-full mb-2 p-2.5 bg-black/40 backdrop-blur-md rounded border border-white/10"
            onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }}
            onDrop={(e) => { e.preventDefault(); handlePoolDrop(); }}>
            {pool.map((piece, idx) => (
              <button
                key={idx}
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.effectAllowed = "move";
                  handlePlacementDragStart({ type: "pool", index: idx });
                }}
                onClick={() => handlePoolClick(idx)}

                className={`flex items-center justify-center w-16 h-16  rounded border-2 transition-all overflow-hidden
                 ${selectedPoolIndex == idx
                    ? "border-yellow-400 bg-blue-600 text-white scale-115 shadow-cyan-500/50 shadow-md"
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
        </div>
      )}
      {/* WAITING */}
      {phase == "WAITING" && (
        <div className="w-full py-10 flex flex-col items-center justify-center bg-black/30 rounded-lg border border-yellow-500/20 backdrop-blur-sm">
          <Loading message="Attente..." size={80} />
        </div>
      )}

      <div className="flex items-center gap-8 z-10">
        {/* Timers */}
        {phase == "PLAYING" && (
          <div className="flex flex-col justify-between h-[80vh] py-4">
            <Timer timeLeft={timeRemaining[1] || 0} color="RED" turn={turn} onExpire={() => setError("Temps écoulé pour Red!")} />
            <Panel variant="score" title="SCORE" message={scoreRed.toString()}
              className="absolute top-[15%] left-0"
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                width: "120px",
                height: "120px",
              }} />
            <TurnIndicator turn={turn} />
            <Panel variant="score" title="SCORE" message={scoreBlue.toString()}
              className="absolute bottom-[15%] left-0"
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                width: "120px",
                height: "120px",
              }} />
            <Timer timeLeft={timeRemaining[0] || 0} color="BLUE" turn={turn} onExpire={() => setError("Temps écoulé pour Blue!")} />
          </div>
        )}

        {/* Board */}
        <div className="relative grid grid-cols-10 gap-0.5 w-[min(900px,82vh)] shrink-0 aspect-square border-[6px] border-yellow-500/50 bg-gray-800 p-0.5 rounded shadow-2xl">
          {/* Bloquer toutes les interactions si pas son tour */}
          {phase == "PLAYING" && turn != "BLUE" && (
            <div className="absolute inset-0 z-40 cursor-not-allowed" />
          )}
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
          {battleData?.attacker && battleData?.defender && (
            <Battle
              attacker={battleData.attacker}
              defender={battleData.defender}
              result={battleData.result}
              onClose={() => { setBattleData(null); setPhase("PLAYING"); }}
            />
          )}
          {gameResult && (
            <End result={gameResult} onClose={() => navigate("/lobby")} />
          )}
          {/* YOUR TURN */}
          <YourTurn show={showYourTurn} />
        </div>
      </div>

      {/*Cimetières  */}
      {phase == "PLAYING" && (
        <div className="absolute left-[calc(55%+min(450px,41vh)+20px)] top-1/2 -translate-y-1/2 flex flex-row items-center gap-1 h-[70vh] z-20">
          <Graveyard title="Pièces Capturées" counts={capturedPieces} />
          <Graveyard title="Pièces Perdues" counts={lostPieces} />
        </div>
      )}

      {/* Erreurs*/}
      {error && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm">
          <Notification
            variant="error"
            message={error}
            autoClose={3000}
            onClose={() => setError("")}
          />
        </div>
      )}
    </div>
  </MainLayout>
);
}