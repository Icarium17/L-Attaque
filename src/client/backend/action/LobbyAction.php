<?php
require_once("action/CommonAction.php");

class LobbyAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_MEMBER);
    }

    protected function executeAction() {
        $action = $_POST["action"] ?? null;
        $key = $_POST["key"] ?? $_SESSION["key"] ?? null;
        $mode = $_POST["mode"] ?? $_SESSION["mode"] ?? null;

        if (empty($key)) {
            return ["result" => ["error" => "Session inactive"]];
        }

        try {
            switch ($action) {
                case "start_game":
                    return $this->handleStartGame($key, $mode);
                case "resume_game":  
                    return $this->handleResumeGame($key);
                default:
                    return ["result" => ["error" => "Action non reconnue"]]; 
            }
        } catch (Exception $e) {
            return ["result" => ["error" => $e->getMessage()]];
        }
    }


    private function handleStartGame(string $key, ?string $mode): array {
        $data = [
            "key" => $key,
            "mode" => $mode
        ];
        
        $apiResult = parent::callPython("start_game", $data);

        if ($apiResult === null) {
            throw new Exception("Erreur Serveur");
        }
        
        return [
            "result" => [
                "success" => true,
                "status" => $apiResult->status ?? null,
                "message" => "Jeu initialisé"
            ],
            "response_svr" => $apiResult
        ];
    }    


    private function handleResumeGame(string $key): array {
        $data = ["key" => $key];
        
        $apiResult = parent::callPython("load", $data);

        if ($apiResult === null) {
            throw new Exception("Erreur Serveur");
        }

        return [
            "result" => [
                "success" => true,
                "restored" => $apiResult->restored ?? false
            ],
            "response_svr" => $apiResult
        ];
    }
}