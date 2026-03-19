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

        if ($action == "make_move") {
            $data = [
                "key" => $key,
                "from_row" => $_POST["from_row"],
                "from_col" => $_POST["from_col"],
                "to_row" => $_POST["to_row"],
                "to_col" => $_POST["to_col"]
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

            $success = true;
            $message = "Move effectué";
            return ["result" => compact("success", "message"), "response_svr" => $apiResult];
        }

        $error = "Action inconnue";
        return ["result" => compact("error")];
    }
}