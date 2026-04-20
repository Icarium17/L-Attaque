import { PIECES_CONFIG, RANK_TO_TYPE } from "./gameConfig.js";

/*
  Génère les pièces du pool ou du board
*/
export function createPieces(player) {
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
export function createEmptyBoard() {
  return Array.from({ length: 10 }, () => Array(10).fill(null));
}

/*
  Affiche le plateau et ses pieces a partir de la réponse de l'Api
*/
export function makeBoard(apiBoard, playerOrder = 0, playerColor = "BLUE", opponentColor = "RED") {
  const newGrid = Array.from({ length: 10 }, () => Array(10).fill(null));
  if (!apiBoard || !Array.isArray(apiBoard)) return newGrid;

  const typeToRank = {};
  for (const rank in RANK_TO_TYPE) {
    typeToRank[RANK_TO_TYPE[rank]] = rank;
  }

  apiBoard.forEach((p) => {
    if (!p.position || !Array.isArray(p.position)) return;
    const [x, y] = p.position;
    const player = p.owner == playerOrder ? playerColor : opponentColor;
    const rank = typeToRank[p.type] ?? "?";
    if (y >= 0 && y < 10 && x >= 0 && x < 10) {
          newGrid[y][x] = { rank, type: p.type, player, revealed: p.owner == playerOrder };
       }
    });
   return newGrid;
}