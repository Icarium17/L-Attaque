<?php
require_once("action/CommonAction.php");

class OptionsAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_MEMBER);
    }

    protected function executeAction() {
        $action = $_POST["action"] ?? null;
        $key = $_POST["key"] ?? $_SESSION["key"] ?? null;
        $difficulty = $_POST["difficulty"] ?? $_SESSION["difficulty"] ?? null;

        if (empty($key)) {
            return ["result" => ["error" => "Session inactive"]];
        }

        if ($action == "set_difficulty") {
            return $this->handleSetDifficulty($key, $difficulty);
        }

        return ["result" => ["error" => "Action non reconnue"]];
    }


    private function handleSetDifficulty(string $key, ?string $difficulty): array {
        $valides = ["easy", "medium", "hard"];
        if (!in_array($difficulty, $valides, true)) {
            return ["result" => ["error" => "Difficulté invalide"]];
        }

        $diffMap = ["easy" => 1, "medium" => 2, "hard" => 3];
        $data = [
            "key" => $key,
            "difficulty" => $diffMap[$difficulty]
        ];

        $apiResult = parent::callPython("difficulty", $data);
 
        if ($apiResult == null) {
            return ["result" => ["error" => "Erreur Serveur"]];
        }

        $_SESSION["difficulty"] = $difficulty;

        return [
            "result" => [
                "success" => true,
                "difficulty" => $difficulty,
                "message" => "Difficulté mise à jour"
            ],
            "response_svr" => $apiResult
        ];
    }
}