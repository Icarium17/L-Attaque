<?php
require_once("action/CommonAction.php");

class GameAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_MEMBER);
    }

    protected function executeAction() {
        $action = $_POST["action"] ?? null;
        $key = $_POST["key"] ?? $_SESSION["key"] ?? null;

        if (empty($key)) {
            return ["result" => ["error" => "Session inactive"]];
        }

        try {
            switch ($action) {
                case "make_move":
                    return $this->handleMakeMove($key);
                case "submit_placement":
                    return $this->handleSubmitPlacement($key);
                case "get_game_status":
                    return $this->handleGetGameStatus($key);
                case "surrender":
                case "pause":
                case "resume":
                case "save":
                case "load":
                    return $this->handleSimpleAction($action, $key);
                default:
                    return ["result" => ["error" => "Action inconnue"]];
            }
        } catch (Exception $e) {
            return ["result" => ["error" => $e->getMessage()]];
        }
    }

    /**
     * Gère l'appel à l'API Python 
     */
    private function callApi(string $endpoint, array $data) {
        $apiResult = parent::callPython($endpoint, $data);
        if ($apiResult == null) {
            throw new Exception("Erreur du Serveur");
        }
        return $apiResult;
    }

    private function handleMakeMove(string $key): array {
        $data = [
            "user_key" => $key, 
            "ligne" => (int)$_POST["ligne"],
            "colonne" => (int)$_POST["colonne"],
            "destination_ligne" => (int)$_POST["destination_ligne"],
            "destination_colonne" => (int)$_POST["destination_colonne"]
        ];
        
        $apiResult = $this->callApi("make_move", $data);

        // Gestion des erreurs spécifiques au mouvement
        $errorStatuses = [
            "INVALID_MOVE" => "Mouvement invalide",
            "NOT_YOUR_TURN" => "Pas ton tour",
            "INVALID_KEY" => "Clef invalide"
        ];

        if (isset($apiResult->status) && isset($errorStatuses[$apiResult->status])) {
            return [
                "result" => ["error" => $errorStatuses[$apiResult->status]], 
                "response_svr" => $apiResult
            ];
        }

        // Si le mouvement est valide, on récupère le nouveau statut
        $statusResult = $this->callApi("get_status", ["key" => $key]);

        return [
            "result" => [
                "success" => true,
                "message" => "Move effectue",
                "apiBoard" => $statusResult->board,
                "turn" => strtoupper($statusResult->turn ?? '')
            ],
            "response_svr" => $statusResult
        ];
    }

    private function handleSubmitPlacement(string $key): array {
        $data = [
            "key" => $key,
            "pieces" => json_decode($_POST["pieces"], true)
        ];
        
        $apiResult = $this->callApi("set_pieces", $data);

        return [
            "result" => ["success" => true, "message" => "Placement envoye"], 
            "response_svr" => $apiResult
        ];
    }

    private function handleGetGameStatus(string $key): array {
        $apiResult = $this->callApi("get_status", ["key" => $key]);

        return [
            "result" => [
                "success" => true,
                "status" => $apiResult->status,
                "turn" => strtoupper($apiResult->turn ?? ''),
                "time_remaining" => $apiResult->time_remaining ?? null,
                "apiBoard" => $apiResult->board ?? null
            ], 
            "response_svr" => $apiResult
        ];
    }

    /**
     * Gère toutes les actions sans clef
     */
    private function handleSimpleAction(string $action, string $key): array {
    $endpoint = ($action == "resume") ? "pause" : $action;
    
    $apiResult = $this->callApi($endpoint, ["key" => $key]);
    
    $resultData = ["success" => true];

    if ($action == "surrender") {
        $resultData["status"] = $apiResult; 
    } 
    elseif ($action == "pause" || $action == "resume") {
        $resultData["pauseStatus"] = $apiResult;
    } 
    elseif ($action == "save") {
        $resultData["gameState"] = $apiResult;
    } 
    return ["result" => $resultData];
}
}