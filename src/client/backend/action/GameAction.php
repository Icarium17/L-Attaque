<?php
require_once("action/CommonAction.php");

class GameAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_MEMBER);
    }

    protected function executeAction() {
        $action = isset($_POST["action"]) ? $_POST["action"] : null;
        $key = $_POST["key"] ?? $_SESSION["key"] ?? null;

        if (empty($key)) {
            $error = "Session inactive";
            return ["result" => compact("error")];
        }

        // Gestion déplacer pièce
        if ($action == "make_move") {
            $data = [
                "user_key" => $key, 
                "ligne" => (int)$_POST["ligne"],
                "colonne" => (int)$_POST["colonne"],
                "destination_ligne" => (int)$_POST["destination_ligne"],
                "destination_colonne" => (int)$_POST["destination_colonne"]
            ];
            $apiResult = parent::callPython("make_move", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur";
                return ["result" => compact("error")];
            }

            if (isset($apiResult->status) && $apiResult->status == "INVALID_MOVE") {
                $error = "Mouvement invalide";
                return ["result" => compact("error"), "response_svr" => $apiResult];
            }

            if (isset($apiResult->status) && $apiResult->status == "NOT_YOUR_TURN") {
                $error = "Pas ton tour";
                return ["result" => compact("error"), "response_svr" => $apiResult];
            }

            if (isset($apiResult->status) && $apiResult->status == "INVALID_KEY") {
                $error = "Clef invalide";
                return ["result" => compact("error"), "response_svr" => $apiResult];
            }
             
            $statusData = ["key" => $key];
            $statusResult = parent::callPython("get_status", $statusData);

            $success = true;
            $message = "Move effectue";
            $apiBoard = $statusResult->board; 
            $turn = strtoupper($statusResult->turn?? '');
            
            return ["result" => compact("success", "message", "apiBoard", "turn"), "response_svr" => $statusResult];
        }

        // Gestion envoi placement
        if ($action == "submit_placement") {
            $data = [
                "key" => $key,
                "pieces" => json_decode($_POST["pieces"], true)
            ];
            
            $apiResult = parent::callPython("set_pieces", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur Python Set_pieces)";
                return ["result" => compact("error")];
            }
            
            $success = true;
            $message = "Placement envoye";
            return ["result" => compact("success", "message"), "response_svr" => $apiResult];
        }

        // Gestion du statut
        if ($action == "get_game_status") {
            $data = [
                "key" => $key
            ];
            
            $apiResult = parent::callPython("get_status", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur Status";
                return ["result" => compact("error")];
            }

            $success = true;
            $status = $apiResult -> status;
            $turn = strtoupper($apiResult->turn ?? '');
            $time_remaining = $apiResult->time_remaining ?? null;
            $apiBoard = $apiResult->board ?? null;
            return ["result" => compact("success","status","turn","time_remaining","apiBoard"), "response_svr" => $apiResult];
        }

        // Gestion capituler
        if ($action == "surrender") {
            $data = ["key" => $key];
            $apiResult = parent::callPython("surrender", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur";
                return ["result" => compact("error")];
            }
            $success = true;
            $status = $apiResult;
        return ["result" => compact("success","status")];
        }

        if ($action == "pause" || $action == "resume") {
            $data = ["key" => $key];
            $apiResult = parent::callPython("pause", $data);
            
            if ($apiResult == null ) {
                $error = "Erreur Serveur";
                return ["result" => compact("error")];
            }

            $success = true;
            $pauseStatus = $apiResult;
            return ["result" => compact("success", "pauseStatus")];
        }

        $error = "Action inconnue";
        return ["result" => compact("error")];
    }
    
}


 