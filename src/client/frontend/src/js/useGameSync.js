import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { getGameStatus } from "./gameService.js";
import { makeBoard } from "./boardUtils.js";
import { PIECES_CONFIG } from "./gameConfig.js";

const TYPE_TO_RANK = Object.fromEntries(PIECES_CONFIG.map(p => [p.type, p.rank]));

export function useGameSync({ phase, setPhase, setTurn, setTimeRemaining, setBoard, setBattleData, setGameResult }) {
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

          const status = gameData?.status?.toUpperCase();

          if (gameData?.turn) setTurn(gameData.turn.toUpperCase());
          if (gameData?.time_remaining)
            setTimeRemaining(gameData.time_remaining.map(val => Number(val)));

          const boardData = result.result?.apiBoard || gameData?.board;
          if (boardData) setBoard(makeBoard(boardData));

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
            else                                             battleResult = "BOTH_LOSE";

            setBattleData({
              attacker: { type: attacker.type, rank: TYPE_TO_RANK[attacker.type], player: attacker.owner == 1 ? "RED" : "BLUE" },
              defender: { type: defender.type, rank: TYPE_TO_RANK[defender.type], player: defender.owner == 1 ? "RED" : "BLUE" },
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