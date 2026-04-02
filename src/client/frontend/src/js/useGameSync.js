import { useEffect } from "react";
import { useNavigate } from "react-router";
import { getGameStatus } from "./gameService.js";
import { makeBoard } from "./boardUtils.js";

export function useGameSync({ phase, setPhase, setTurn, setTimeRemaining, setBoard }) {
  const navigate = useNavigate();

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

          if (gameData?.status) setPhase(gameData.status.toUpperCase());
          if (gameData?.turn) setTurn(gameData.turn.toUpperCase());
          if (gameData?.time_remaining) {
            setTimeRemaining(gameData.time_remaining.map(val => Number(val)));
          }

          if (gameData?.status?.toUpperCase() == "PLAYING") {
            const boardData = result.result?.apiBoard || gameData?.board;
            if (boardData) setBoard(makeBoard(boardData));
          }

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