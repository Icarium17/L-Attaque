<?php

    require_once("action/LeaderBoardAction.php");

    $action = new LeaderBoardAction();

    $data = $action->execute();

    echo json_encode($data);