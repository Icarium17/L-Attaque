// React
import { useEffect, useState} from "react";
import { useNavigate, useLocation } from "react-router";
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
import Button from "../components/button.jsx";
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
import ConnectionStatus from "../components/connectionStatus.jsx";

// Assets
import backgroundGame from '../assets/images/background-game.png';
import backgroundScore from '../assets/images/background-score.png';  
import surrender from '../assets/images/surrender.png';  
import blueName from '../assets/images/blue-name.png';  
import redName from '../assets/images/red-name.png';
import pause from '../assets/images/pause.png';  
import play from '../assets/images/play.png';
import save from '../assets/images/save.png';

export default function Game() {
  const navigate = useNavigate();
  
  // État du plateau et du jeu
  const [board, setBoard] = useState(() => createEmptyBoard()); 
  const [turn, setTurn] = useState("BLUE");
  const location = useLocation();
  const [phase, setPhase] = useState(location.state?.resumed ? "PLAYING" : "PLACEMENT"); 
  const [timeRemaining, setTimeRemaining] = useState([0, 0]);

  // État UI
  const [session, setSession] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [loading, setLoading] = useState(false);    
  const [error, setError] = useState("");

  // Ecran battle {  attacker: { rank: 10, type: "Marechal",  player: "RED"  },  defender: { rank: 2,  type: "Eclaireur", player: "BLUE" },  result:   "ATTACKER_WIN",}
  const [battleData, setBattleData] = useState(null);
  const [battleCell, setBattleCell] = useState(null);  

  //  Ordre et couleurs des joueurs
  const [playerOrder, setPlayerOrder] = useState(null);
  const [playerColor, opponentColor] = playerOrder == 1 ? ["RED", "BLUE"] : ["BLUE", "RED"];

  // Etats cimetières
  const [capturedPieces, setCapturedPieces] = useState({});
  const [lostPieces, setLostPieces] = useState({});

  // Etats des scores
  const [scoreBlue, setScoreBlue] = useState(0);
  const [scoreRed, setScoreRed] = useState(0);

  // Ecran fin de jeu  {"WIN" | "LOSE"}
  const [gameResult, setGameResult] = useState(null); 

  // Etat PAUSE
  const [isPaused, setIsPaused] = useState(false);  

  // Sauvegarde
  const [saveSuccess, setSaveSuccess] = useState("");

  // Notification mouvement réussi
  const [moveSuccess, setMoveSuccess] = useState("");

  // PopUp YourTurn
  const [showYourTurn, setShowYourTurn] = useState(false);

  const [pingMs, setPingMs] = useState(null);

  // Affiche la popup "Your Turn" quand le tour passe à BLUE après RED
  const setTurnWithPop = (newTurn) => {
  setTurn(prev => {
    if (newTurn == playerColor && prev == opponentColor) {
      setShowYourTurn(true);
      setTimeout(() => setShowYourTurn(false), 900);
    }
    return newTurn;
  });
};

 // Affiche la popup au début de la phase PLAYING si c'est déjà le tour du joueur
  useEffect(() => {
  if (phase == "PLAYING" && turn == playerColor) {
    setShowYourTurn(true);
    setTimeout(() => setShowYourTurn(false), 900);
  }
  }, [phase]);

  // Initialise la session utilisateur au montage, puis récupère l'ordre du joueur.
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (!key || !username) { navigate("/"); return;}
      setSession({ username, key });
  }, [navigate]);

  // Hook custom : Sync serveur (polling) : board, turn, timers, scores, battle, fin de partie
  useGameSync({ phase, setPhase, setTurn: setTurnWithPop, setTimeRemaining, setBoard, setBattleData, setGameResult, setCapturedPieces, setLostPieces, setScoreBlue, setScoreRed, playerOrder, setPlayerOrder, playerColor, opponentColor });
 
  
  // Destructuration de usePlacement : retourne le pool de pièces à placer,l'index sélectionné, et les fonctions de placement (clic, drag & drop, auto, reset, envoi au serveur)
  // { propriétés extraites } = usePlacement(params)  | handleDragStart/handleBoardDrop renommés pour éviter conflit avec useCellClick
  const {
    pool, selectedPoolIndex,
    handlePoolClick, handlePlacementCellClick,handleAutoPlacement, handleResetPlacement, handleSubmitPlacement,
    handleDragStart: handlePlacementDragStart,handleBoardDrop: handlePlacementBoardDrop, handlePoolDrop} = 
    usePlacement({ board, setBoard, phase, setPhase, setTurn, loading, setLoading, setError, selectedCell, setSelectedCell,playerColor, playerOrder });
 
  // Logique clic ou drag case (sélection + déplacement)
  // { propriétés extraites } = useCellClick(params)
  const { 
    handleCellClick,handleDragStart: handlePlayingDragStart,handleBoardDrop: handlePlayingBoardDrop,} = 
    useCellClick({board, setBoard, turn, setTurn, selectedCell, setSelectedCell,loading, setLoading, phase, setError, setMoveSuccess, handlePlacementCellClick, isLake, playerColor, playerOrder, opponentColor, setPingMs, setBattleCell});

  // Sélectionne le bon handler drag/drop selon la phase (PLACEMENT ou PLAYING)
  const activeDragStart = phase == "PLACEMENT" ? handlePlacementDragStart : phase == "PLAYING"   ? handlePlayingDragStart: undefined;
  const activeBoardDrop = phase == "PLACEMENT" ? handlePlacementBoardDrop : phase == "PLAYING"   ? handlePlayingBoardDrop: undefined;

 
  // Fonction pause
  const togglePause = () => {
  const key = localStorage.getItem("sessionKey");

  let formData = new FormData();
  formData.append("action", isPaused ? "resume" : "pause");
  formData.append("key", key);

  fetch("/api/game.php", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {

      const status = data.result.pauseStatus?.[1];

      if (data.result.success && status == "GAME_PAUSED") {
        setIsPaused(true);
      } 
      else if (data.result.success && status == "GAME_RESTARTED") {
        setIsPaused(false);
      } 
      else {
        setError(data.result.error || "Pause impossible.");
      }

    })
    .catch(() => setError("Erreur du serveur."));
  };

  // Fonction capituler
  const surrenderGame = () => {
    setLoading(true);
    let formData = new FormData();
    const key = localStorage.getItem("sessionKey");
    formData.append("action", "surrender");
    formData.append("key", key);
    fetch("/api/game.php", { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            setLoading(false);
            if (data.result.success && data.result.status == "GAME_SURRENDERED") {
                setGameResult("LOSE");
                setPhase("LOSE");
            }
    });
  };

 
// Fonction sauvegarder
  const saveGame = () => {
    setLoading(true);
    const key = localStorage.getItem("sessionKey");
    const formData = new FormData();
    formData.append("action", "save");
    formData.append("key", key);

    fetch("/api/game.php", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        setLoading(false);
        if (data.result.success) {
          const status = data.result.gameState?.[1];
          if (status == "SAVE_COMPLETE") {
            setSaveSuccess("Partie sauvegardée");           
 
            setTimeout(() => {
              // Reset complet de l'état du jeu
              setBoard(createEmptyBoard());
              setPhase("PLACEMENT");
              setBattleData(null);
              setBattleCell(null);
              setGameResult(null);
              setCapturedPieces({});
              setLostPieces({});
              setScoreBlue(0);
              setScoreRed(0);
              setPlayerOrder(null);
              setTurn("BLUE");
              navigate("/lobby");
            }, 3000);

          } else if (status == "SAVING") {
          }
        } else {
          setError(data.result.error || "Erreur sauvegarde");
        }
      })
      .catch(() => { setLoading(false); setError("Erreur serveur"); });
  };


  const battleCells = battleCell
    ? [battleCell]
    : [];

if (!session) return null;
 
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
                  playerColor = {playerColor}
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
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/60 backdrop-blur-md">
          <Loading message="Attente..." size={80} />
        </div>
      )}

      <div className="flex items-center gap-10 z-10">
        {/* Timers */}
        {phase != "PLACEMENT" && phase != "WAITING" && (
            <div className={`flex flex-col justify-between h-[80vh] py-4 ${phase != "PLAYING" ? "invisible" : ""}`}>
            <Timer timeLeft={timeRemaining[1] || 0} color={opponentColor} turn={turn} isPaused={isPaused} onExpire={() => setError("Temps écoulé pour " + opponentColor + "!")} />
            <Panel 
              variant="name" 
              title="Adversaire"
              className="absolute top-[32%] left-[18%]"
              style={{
                backgroundImage: `url(${opponentColor == "RED" ? redName : blueName})`,
                backgroundSize: "contain",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                width: "400px",
                height: "150px",
                padding: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }} 
            />
            <Panel variant="score" title="SCORE" message={(opponentColor == "RED" ? scoreRed : scoreBlue).toString()}
              className="absolute top-[15%] left-[15%] "
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                width: "120px",
                height: "120px",
              }} />
            <Panel 
              variant="name" 
              title={session.username}
              className="absolute top-[60%] left-[18%]"
              style={{
                backgroundImage: `url(${playerColor == "RED" ? redName : blueName})`,
                backgroundSize: "contain",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                width: "400px",
                height: "150px",
                padding: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }} 
            />

            <TurnIndicator turn={turn} playerColor={playerColor} playerName={session.username} opponentName="Adversaire"/>
            <Panel variant="score" title="SCORE" message={(playerColor == "RED" ? scoreRed : scoreBlue).toString()}
              className="absolute bottom-[15%] left-[15%] "
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                width: "120px",
                height: "120px",
              }} />
            <Timer timeLeft={timeRemaining[0] || 0} color={playerColor} turn={turn} isPaused={isPaused} onExpire={surrenderGame} />
          </div>
        )}
        
        {/* Board */}
        <div className="relative grid grid-cols-10 gap-0.5 w-[min(900px,82vh)] shrink-0 aspect-square border-[6px] border-yellow-500/50 bg-gray-800 p-0.5 rounded shadow-2xl">
          {/* Bloquer toutes les interactions si pas son tour */}
          {phase == "PLAYING" && turn != playerColor && (
            <div className="absolute inset-0 z-40 cursor-not-allowed" />
          )}
          {/* Bloquer toutes les interactions si en pause */}
          {phase == "PLAYING" && isPaused && (
            <div className="absolute inset-0 z-40 cursor-not-allowed bg-black/50 flex items-center justify-center">
              <span className="text-yellow-400 text-4xl font-bold">PAUSE</span>
            </div>
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
                playerColor = {playerColor}
                onClick={handleCellClick}
                onDragStart={activeDragStart}
                onDrop={activeBoardDrop}
                isBattle={battleCells.some(c => c.row == rowIndex && c.col == colIndex)}
              />
            ))
          )}
          {battleData?.attacker && battleData?.defender && (
            <Battle
              attacker={battleData.attacker}
              defender={battleData.defender}
              result={battleData.result}
              onClose={() => { setBattleData(null); setBattleCell(null); setPhase("PLAYING"); }}
            />
          )}
          {gameResult && (
            <End result={gameResult} onClose={() => {
            setBoard(createEmptyBoard());
            setPhase("PLACEMENT");
            setBattleData(null);
            setBattleCell(null);
            setGameResult(null);
            setCapturedPieces({});
            setLostPieces({});
            setScoreBlue(0);
            setScoreRed(0);
            setPlayerOrder(null);
            setTurn("BLUE");
            navigate("/lobby");
          }} />
          )}
          {/* YOUR TURN */}
          <YourTurn show={showYourTurn} />
        </div>
      </div>

      {/* Bouton surrender & pause */}
        {phase == "PLAYING" && (
        <div className="flex flex-col gap-2">
        
        {/* Surrender Button */}
        <Button 
            variant="ghost" 
            text="Capituler"
            onClick={surrenderGame} 
            className="absolute bottom-[4%] left-[78%] w-!"
          style={{ 
            width: "120px",
            height: "120px",
            background: `url(${surrender}) center/cover no-repeat`, 
            color: "#ffffff",
            textShadow: "0 0 8px rgba(0,0,0,0.8)",
            fontSize: "12px",
            paddingTop: "70px",  
        }}
        />

        {/* Pause/Play Button */}
        <Button 
            variant="ghost" 
            text={isPaused ? "Reprendre" : "Pause"} 
            onClick={togglePause} 
            className="absolute bottom-[4%] left-[83%] w-30!"  
          style={{ 
            width: "120px",
            height: "120px",
            background: `url(${isPaused ? play : pause}) center/cover no-repeat`,  
            color: "#ffffff",
            textShadow: "0 0 8px rgba(0,0,0,0.8)",
            fontSize: "10px",
            paddingTop: "70px",  
        }}
        />
        {/* Save Button */}
        <Button 
            variant="ghost" 
            text="Sauver"
            onClick={saveGame}
            className="absolute bottom-[3.5%] left-[88%] w-!"
          style={{ 
            width: "130px",
            height: "130px",
            background: `url(${save}) center/cover no-repeat`, 
            color: "#ffffff",
            textShadow: "0 0 8px rgba(0,0,0,0.8)",
            fontSize: "11px",
            paddingTop: "90px",  
        }}
        /> 
        </div>
        )} 

      {/*Cimetières  */}
      {phase == "PLAYING" && (
        <div className="absolute left-[calc(57%+min(450px,41vh)+20px)] top-1/2 -translate-y-1/2 flex flex-row items-center gap-2 h-[70vh] z-20">
          <Graveyard title="Pièces Capturées" counts={capturedPieces} />
          <Graveyard title="Pièces Perdues" counts={lostPieces} />
        </div>
      )}   
      {phase == "PLAYING" && (
        <div className="absolute bottom-10 right-24">
          <ConnectionStatus pingMs={pingMs} />
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

    {saveSuccess && (
    <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm">
    <Notification
      variant="success"
      message={saveSuccess}
      autoClose={1000}
      onClose={() => setSaveSuccess("")}
    />
  </div>
  )}

  {moveSuccess && (
    <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm">
      <Notification
        variant="success"
        message={moveSuccess}
        autoClose={1000}
        onClose={() => setMoveSuccess("")}
      />
    </div>
  )}
  
    </div> 
  </MainLayout>
);
}