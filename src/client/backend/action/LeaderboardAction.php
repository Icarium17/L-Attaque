<?php
require_once("action/CommonAction.php");

class AdminAction extends LeaderboardAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_PUBLIC);
    }

protected function executeAction() {
    $action = isset($_POST["action"]) ? $_POST["action"] : null;
    $key = $_SESSION["key"] ?? $_POST["key"] ?? null;
 

    if (empty($key)) {
        $error = "Session inactive";
        return ["result" => compact("error")];
    }

    if ($action == "get_active_users") {
        $apiResult = parent::callPython("get_all_users", ["key" => $key]);

        if ($apiResult == null) {
            $error = "Erreur Serveur";
            return ["result" => compact("error")];
        }

        $users = isset($apiResult->users) ? $apiResult->users : [];
        return ["result" => ["users" => $users]];
    }

    if ($action == "delete_user") {
        $user_id = $_POST["user_id"] ?? null;
        if (empty($user_id)) {
            $error = "ID manquant";
            return ["result" => compact("error")];
        }

        $apiResult = parent::callPython("delete_user", [
            "key" => $key,
            "user_id" => $user_id
        ]);

        if ($apiResult == null) {
            $error = "Erreur Serveur";
            return ["result" => compact("error")];
        }

        return ["result" => $apiResult, "success" => true];
    }

    $error = "Action inconnue";
    return ["result" => compact("error")];
}
}