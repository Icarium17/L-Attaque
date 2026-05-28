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

  // Dernier etat de la piece
  const [lastMoves, setLastMoves] = useState([null, null]);
  const [arrows, setArrows] = useState({});  

  const [opponentName, setOpponentName] = useState("Adversaire");

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

// Logique dernier mouvement
useEffect(() => {
  if (!lastMoves || playerOrder == null) return;
  setArrows(prev => {
    const next = { ...prev };
    let changed = false;
    lastMoves.forEach((m, owner) => {
      if (!m || !m.moveFrom || !m.moveTo) return;
      const color = owner == playerOrder ? playerColor : opponentColor;
      const key = `${m.moveFrom[0]},${m.moveFrom[1]}->${m.moveTo[0]},${m.moveTo[1]}`;
      if (prev[color] && prev[color].key == key) return;  
      next[color] = {
        from: { row: m.moveFrom[1], col: m.moveFrom[0] },
        to:   { row: m.moveTo[1],   col: m.moveTo[0] },
        key,
        ts: Date.now(),
      };
      changed = true;
    });
    return changed ? next : prev;
  });
}, [lastMoves, playerOrder, playerColor, opponentColor]);

  // Fleche
   useEffect(() => {
    if (!lastMoves || playerOrder == null) return;
    setArrows(prev => {
      const next = { ...prev };
      let changed = false;
      lastMoves.forEach((m, owner) => {
        if (!m || !m.moveFrom || !m.moveTo) return;
        const color = owner == playerOrder ? playerColor : opponentColor;
        const key = `${m.moveFrom[0]},${m.moveFrom[1]}->${m.moveTo[0]},${m.moveTo[1]}`;
        if (prev[color] && prev[color].key == key) return;  
        next[color] = {
          from: { row: m.moveFrom[1], col: m.moveFrom[0] },
          to:   { row: m.moveTo[1],   col: m.moveTo[0] },
          key,
          ts: Date.now(),
        };
        changed = true;
      });
      return changed ? next : prev;
    });
  }, [lastMoves, playerOrder, playerColor, opponentColor]);

  useEffect(() => {
    const timers = [];
    for (const color of Object.keys(arrows)) {
      const arrow = arrows[color];
      const remaining = 3000 - (Date.now() - arrow.ts);
      if (remaining <= 0) continue;
      timers.push(setTimeout(() => {
        setArrows(prev => {
          if (!prev[color] || prev[color].ts != arrow.ts) return prev;
          const cp = { ...prev };
          delete cp[color];
          return cp;
        });
      }, remaining));
    }
    return () => timers.forEach(clearTimeout);
  }, [arrows]);

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
  useGameSync({ 
    phase, setPhase, 
    setTurn: setTurnWithPop, 
    setTimeRemaining, setBoard, setBattleData, setGameResult, 
    setCapturedPieces, setLostPieces, setScoreBlue, setScoreRed, 
    playerOrder, setPlayerOrder, playerColor, opponentColor,
    setLastMoves,
    setOpponentName 
  });
  
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
       <div className="absolute left-[13%] top-1/2 -translate-y-1/2 flex flex-col items-center w-64 fhd:w-72 4k:w-96 z-20 space-y-3 fhd:space-y-4 4k:space-y-5">
          <GameMessage variant="title" title="Pièces à placer" />
          <Button variant="primary" onClick={handleAutoPlacement} disabled={pool.length == 0} fullWidth text="Placement Auto" />
          <Button variant="danger" onClick={handleResetPlacement} disabled={pool.length == 40} fullWidth text="Annuler" />

        {/* POOL */}
          <div className="grid grid-cols-4 place-items-center gap-2 fhd:gap-2 4k:gap-3 overflow-y-auto w-full mb-2 p-2 fhd:p-2.5 bg-black/40 backdrop-blur-md rounded border border-white/10"
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

                className={`flex items-center justify-center w-11 h-11 fhd:w-12 fhd:h-12 4k:w-16 4k:h-16 rounded border-2 transition-all overflow-hidden
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

      <div className="flex items-center gap-6 fhd:gap-8 4k:gap-10 z-10">
        {/* Timers */}
        {phase != "PLACEMENT" && phase != "WAITING" && (
            <div className={`flex flex-col justify-between h-[80vh] py-4 ${phase != "PLAYING" ? "invisible" : ""}`}>
            <Timer timeLeft={timeRemaining[1] || 0} 
                   color={opponentColor} 
                   turn={turn} 
                   isPaused={isPaused}/>
            <Panel 
            variant="name" 
            title={opponentName} 
            className={`absolute top-[32%] left-[18%] [--panel-w:260px] [--panel-h:95px] fhd:[--panel-w:280px] fhd:[--panel-h:100px] 4k:[--panel-w:400px] 4k:[--panel-h:150px] ${turn == opponentColor ? "animate-pulse" : ""}`}
            style={{
              backgroundImage: `url(${opponentColor == "RED" ? redName : blueName})`,
              backgroundSize: "contain",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
              width: "var(--panel-w)",
              height: "var(--panel-h)",
              padding: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }} 
          />
            <Panel variant="score" title="SCORE" message={(opponentColor == "RED" ? scoreRed : scoreBlue).toString()}
              className="absolute top-[15%] left-[15%] w-20 h-[80px] fhd:w-[100px] fhd:h-[100px] 4k:w-[120px] 4k:h-[120px]"
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }} />
            <Panel 
            variant="name" 
            title={session.username}
            className={`absolute top-[60%] left-[18%] [--panel-w:260px] [--panel-h:95px] fhd:[--panel-w:280px] fhd:[--panel-h:100px] 4k:[--panel-w:400px] 4k:[--panel-h:150px] ${turn == playerColor ? "animate-pulse" : ""}`}
            style={{
              backgroundImage: `url(${playerColor == "RED" ? redName : blueName})`,
              backgroundSize: "contain",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
              width: "var(--panel-w)",
              height: "var(--panel-h)",
              padding: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }} 
          />

            <TurnIndicator turn={turn} playerColor={playerColor} playerName={session.username}  title={opponentName} />
            <Panel variant="score" title="SCORE" message={(playerColor == "RED" ? scoreRed : scoreBlue).toString()}
              className="absolute bottom-[15%] left-[15%] w-[80px] h-[80px] fhd:w-[100px] fhd:h-[100px] 4k:w-[120px] 4k:h-[120px]"
              style={{
                backgroundImage: `url(${backgroundScore})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }} />
            <Timer timeLeft={timeRemaining[0] || 0} 
                   color={playerColor}
                   turn={turn} 
                   isPaused={isPaused} />
          </div>
        )}
        
        {/* Board */}
        <div className="relative grid grid-cols-10 gap-0.5 w-[min(600px,75vh)] fhd:w-[min(680px,72vh)] 4k:w-[min(900px,82vh)] shrink-0 aspect-square border-[4px] fhd:border-[5px] 4k:border-[6px] border-yellow-500/50 bg-gray-800 p-0.5 rounded shadow-2xl">
          {/* Bloquer toutes les interactions si pas son tour */}
          {phase == "PLAYING" && turn != playerColor && (
            <div className="absolute inset-0 z-40 cursor-not-allowed" />
          )}
          {/* Bloquer toutes les interactions si en pause */}
          {phase == "PLAYING" && isPaused && (
            <div className="absolute inset-0 z-40 cursor-not-allowed bg-black/50 flex items-center justify-center">
              <span className="text-yellow-400 text-2xl fhd:text-3xl 4k:text-4xl font-bold">PAUSE</span>
            </div>
          )}
         {board.map((row, rowIndex) =>
          row.map((cell, colIndex) => {
            let arrow = null;
            const battleInProgress = battleData != null || battleCell != null || phase == "BATTLE";
            
            if (!battleInProgress) {
              for (const color of Object.keys(arrows)) {
                const a = arrows[color];
                if (a.from.row != rowIndex || a.from.col != colIndex) continue;
                
                const pieceOnFrom = board[a.from.row]?.[a.from.col];
                const pieceOnTo   = board[a.to.row]?.[a.to.col];
                const aliveOnFrom = pieceOnFrom && pieceOnFrom.player == color;
                const aliveOnTo   = pieceOnTo   && pieceOnTo.player   == color;
                
                if (!aliveOnFrom && !aliveOnTo) break;
                
                arrow = { from: a.from, to: a.to, color };
                break;
              }
            }
            
            return (
              <Cell
                key={`${rowIndex}-${colIndex}`}
                row={rowIndex}
                col={colIndex}
                isLake={isLake(rowIndex, colIndex)}
                isSelected={selectedCell && selectedCell.row == rowIndex && selectedCell.col == colIndex}
                piece={cell}
                playerColor={playerColor}
                onClick={handleCellClick}
                onDragStart={activeDragStart}
                onDrop={activeBoardDrop}
                isBattle={battleCells.some(c => c.row == rowIndex && c.col == colIndex)}
                arrow={arrow}
              />
            );
          })
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
        className="absolute bottom-[3%] left-[80%] fhd:left-[76%] [--btn-w:80px] [--btn-h:80px] fhd:[--btn-w:100px] fhd:[--btn-h:100px] 4k:[--btn-w:120px] 4k:[--btn-h:120px] text-[12px] fhd:text-[10px] 4k:text-[12px]"
        style={{ 
          width: "var(--btn-w)",
          height: "var(--btn-h)",
          background: `url(${surrender}) center/cover no-repeat`, 
          color: "#ffffff",
          textShadow: "0 0 8px rgba(0,0,0,0.8)",
          paddingTop: "70px",  
        }}
      />
      {/* Pause/Play Button */}
      <Button 
        variant="ghost" 
        text={isPaused ? "Reprendre" : "Pause"} 
        onClick={togglePause} 
        className="absolute bottom-[3%] left-[83%] fhd:left-[82%] [--btn-w:80px] [--btn-h:80px] fhd:[--btn-w:100px] fhd:[--btn-h:100px] 4k:[--btn-w:120px] 4k:[--btn-h:120px] text-[10px] fhd:text-[10px] 4k:text-[14x]"
        style={{ 
          width: "var(--btn-w)",
          height: "var(--btn-h)",
          background: `url(${isPaused ? play : pause}) center/cover no-repeat`,  
          color: "#ffffff",
          textShadow: "0 0 8px rgba(0,0,0,0.8)",
          paddingTop: "70px",  
        }}
      />

      {/* Save Button */}
      <Button 
        variant="ghost" 
        text="Sauver"
        onClick={saveGame}
        className="absolute bottom-[3%] left-[88%] fhd:left-[88%] [--btn-w:85px] [--btn-h:85px] fhd:[--btn-w:100px] fhd:[--btn-h:100px] 4k:[--btn-w:130px] 4k:[--btn-h:130px] text-[11px] fhd:text-[10px] 4k:text-[13px]"
        style={{ 
          width: "var(--btn-w)",
          height: "var(--btn-h)",
          background: `url(${save}) center/cover no-repeat`, 
          color: "#ffffff",
          textShadow: "0 0 8px rgba(0,0,0,0.8)",
          paddingTop: "70px",  
        }}
      /> 
    </div>
    )}  

      {/*Cimetières  */}
      {phase == "PLAYING" && (
        <div className="absolute left-[calc(57%+min(300px,38vh)+10px)] fhd:left-[calc(55%+min(340px,36vh)+10px)] 4k:left-[calc(57%+min(450px,41vh)+20px)] top-1/2 -translate-y-1/2 flex flex-row items-center gap-1 fhd:gap-1.5 4k:gap-2 h-[70vh] z-20">
          <Graveyard title="Pièces Capturées" counts={capturedPieces} />
          <Graveyard title="Pièces Perdues" counts={lostPieces} />
        </div>
      )}   
      {phase == "PLAYING" && (
      <div className="absolute bottom-4 right-10 fhd:bottom-6 fhd:right-6 4k:bottom-8 4k:right-6">
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