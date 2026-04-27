<?php
    require_once("action/LeaderboardAction.php");

    $action = new LeaderboardAction();
    $data = $action->execute();

    echo json_encode($data);