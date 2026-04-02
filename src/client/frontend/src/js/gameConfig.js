// Constantes du jeu

export const LAKES = [
  "4-2", "4-3", "5-2", "5-3",
  "4-6", "4-7", "5-6", "5-7",
];

export const PIECES_CONFIG = [
  { rank: "B",  type: "Bombe",     count: 6 },
  { rank: "10", type: "Marechal",  count: 1 },
  { rank: "9",  type: "General",   count: 1 },
  { rank: "8",  type: "Colonel",   count: 2 },
  { rank: "7",  type: "Major",     count: 3 },
  { rank: "6",  type: "Capitaine", count: 4 },
  { rank: "5",  type: "Lieutenant",count: 4 },
  { rank: "4",  type: "Sergent",   count: 4 },
  { rank: "3",  type: "Demineur",  count: 5 },
  { rank: "2",  type: "Eclaireur", count: 8 },
  { rank: "1",  type: "Espion",    count: 1 },
  { rank: "D",  type: "Drapeau",   count: 1 },
];

export const RANK_TO_TYPE = {
  "B": "Bombe",     "10": "Marechal", "9": "General",
  "8": "Colonel",   "7": "Major",     "6": "Capitaine",
  "5": "Lieutenant","4": "Sergent",   "3": "Demineur",
  "2": "Eclaireur", "1": "Espion",    "D": "Drapeau",
};

export function isLake(row, col) {
  return LAKES.indexOf(`${row}-${col}`) != -1;
}