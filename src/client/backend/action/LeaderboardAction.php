<?php
require_once("action/CommonAction.php");

class LeaderboardAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_PUBLIC); 
    }

    protected function executeAction() {
        $apiResult = parent::callPython("get_high_scores", []);

        if ($apiResult == null) {
            $error = "Serveur injoignable";
            return ["result" => compact("error")];
        }

        $success = true;
        $data = $apiResult; 
        
        return ["result" => compact("success", "data")];
    }
}