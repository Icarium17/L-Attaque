const API_URL = "/api/game.php";

function callApi(action, formData) {
  formData.append("action", action);
  formData.append("key", localStorage.getItem("sessionKey"));

  return fetch(API_URL, { method: "POST", body: formData })
    .then(res => res.json())
    .catch(err => {
      console.error("Erreur API:", err);
      return null;
    });
}

export function makeMove(fromRow, fromCol, toRow, toCol) {
  let formData = new FormData();
  formData.append("from_row", fromRow);
  formData.append("from_col", fromCol);
  formData.append("to_row", toRow);
  formData.append("to_col", toCol);
  return callApi("make_move", formData);
}

export function submitPlacement(pieces) {
  let formData = new FormData();
 formData.append("pieces", JSON.stringify(pieces)); // Conversion en JSON
  return callApi("submit_placement",formData);
}

export function getGameStatus() {
  let formData = new FormData();
  return callApi("get_game_status", formData);
}