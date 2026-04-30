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


        if ($action == "init_game") {
            $data = [
                "key" => $key,
                "mode" => $mode
            ];
            
            $apiResult = parent::callPython( "init_game", $data);

            if ($apiResult == null) {
                $error = "Erreur Serveur)";
                return ["result" => compact("error")];
            }
            
            $success = true;
            $message = "Jeu initialisé";
            return ["result" => compact("success", "message"), "response_svr" => $apiResult];
        }

        $error = "Action inconnue";
        return ["result" => compact("error")];
    }
    
}


 