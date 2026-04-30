<?php
require_once("action/CommonAction.php");

class LobbyAction extends CommonAction {

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


        if ($action == "start_game") {
            $data = [
                "key" => $key,
                "mode" => $mode
            ];
            
            $apiResult = parent::callPython("start_game", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur)";
                return ["result" => compact("error")];
            }
            
            $success = true;
            $status = $apiResult -> status;
            $message = "Jeu initialisé";
            return ["result" => compact("success","status", "message"), "response_svr" => $apiResult];
        }

        $error = "Pas de réponse serveur";
        return ["result" => compact("error")];
    }    
}

       