import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { getGameStatus } from "./gameService.js";
import { makeBoard } from "./boardUtils.js";
import { PIECES_CONFIG } from "./gameConfig.js";

// Crée un objet { type: rang } à partir de PIECES_CONFIG
// ex: { Marechal: 10, General: 9 ... }
const TYPE_TO_RANK = Object.fromEntries(PIECES_CONFIG.map(p => [p.type, p.rank]));

// Fonction ajoute à un compteur par type
function addToCounts(prev,type){
  return { ...prev, [type]: (prev[type] ?? 0) +1};
}

export function useGameSync({ phase, setPhase, setTurn, setTimeRemaining, setBoard, setBattleData, setGameResult ,setCapturedPieces, setLostPieces, setScoreBlue, setScoreRed,  playerOrder, setPlayerOrder,playerColor, opponentColor }) {
  const navigate = useNavigate();
  const lastBattleRef = useRef(null);

  useEffect(() => {
    if (phase != "PLAYING") return;

    let cancelled = false;
    let timerId;

    const pull = () => {
      getGameStatus()
        .then((result) => {
          if (cancelled) return;

          if (!result || !result.response_svr) {
            timerId = setTimeout(pull, 2000);
            return;
          }

          const gameData = result.response_svr;

          if (result.result?.error == "Session inactive" || gameData?.status == "INVALID_KEY") {
            return navigate("/");
          }

          // Ordre du joueur
          if (gameData?.order != undefined && playerOrder == null) {
            setPlayerOrder(gameData.order);            
          }

          const status = gameData?.status?.toUpperCase();

          // Times
          if (gameData?.turn) setTurn(gameData.turn.toUpperCase());
          if (gameData?.time_remaining)
            setTimeRemaining(gameData.time_remaining.map(val => Number(val)));

          // Scores
          if (gameData?.scores?.length == 2) {   
              setScoreBlue(gameData.scores[0]);
              setScoreRed(gameData.scores[1]);
          }

          const currentOrder = gameData?.order != undefined ? gameData.order : playerOrder;
          const currentPlayerColor = currentOrder == 1 ? "RED" : "BLUE";
          const currentOpponentColor = currentOrder == 1 ? "BLUE" : "RED";

          const boardData = result.result?.apiBoard || gameData?.board;
          if (boardData) setBoard(makeBoard(boardData, currentOrder, currentPlayerColor, currentOpponentColor));

          // PHASE BATTLE
          if (status == "BATTLE" && gameData.battle?.length == 2) { // verif si on a bien des data battle
            const [attacker, defender] = gameData.battle;
            const battleKey = attacker.id + "-" + defender.id; // id de la battle
            if (lastBattleRef.current == battleKey) {
              timerId = setTimeout(pull, 2000);
              return;
             }
            lastBattleRef.current = battleKey;
            
            // Cherche si la pièce est encore sur le board après la bataille a partir de data server
            const attackerSurvived = !!gameData.board.find(p => p.id == attacker.id && p.owner == attacker.owner);
            const defenderSurvived = !!gameData.board.find(p => p.id == defender.id && p.owner == defender.owner);

            let battleResult;
            if (attackerSurvived && !defenderSurvived)      battleResult = "ATTACKER_WIN";
              else if (!attackerSurvived && defenderSurvived) battleResult = "DEFENDER_WIN";
                else battleResult = "BOTH_LOSE";

            // Logique update cimetiere : mort + RED = capturée , mort + BLUE = perdue

            const attackerPlayer = attacker.owner ==  1 ? "RED" : "BLUE";
            const defenderPlayer = defender.owner == 1 ? "RED" : "BLUE";
 
            // Etat du board après combat
            console.log("board après battle:", gameData.board);

            if(!attackerSurvived){
              if (attackerPlayer == "RED") setCapturedPieces(prev => addToCounts(prev, attacker.type));
                else if ( attackerPlayer == "BLUE") setLostPieces(prev => addToCounts(prev, attacker.type));
              }
              if (!defenderSurvived){
                if (defenderPlayer == "RED")  setCapturedPieces(prev => addToCounts(prev, defender.type));
                  else if (defenderPlayer =="BLUE") setLostPieces(prev => addToCounts(prev, defender.type));
              }

            setBattleData({
              attacker: { type: attacker.type, rank: TYPE_TO_RANK[attacker.type], player: attackerPlayer },
              defender: { type: defender.type, rank: TYPE_TO_RANK[defender.type], player: defenderPlayer },
              result: battleResult,
            });
            setPhase("BATTLE");
            return;
          }

          if (status == "WIN" || status == "LOSE") { setGameResult(status); setPhase(status); return; }

          if (status == "PLAYING") setPhase("PLAYING");
          timerId = setTimeout(pull, 2000);
        })
        .catch(() => {
          if (!cancelled) timerId = setTimeout(pull, 3000);
        });
    };

    timerId = setTimeout(pull, 500);

    return () => {
      cancelled = true;
      clearTimeout(timerId);
    };
  }, [phase, navigate]);
}