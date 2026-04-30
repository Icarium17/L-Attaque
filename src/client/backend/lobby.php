<?php

    require_once("action/LobbyAction.php");

    $action = new LobbyAction();

    $data = $action->execute();

    echo json_encode($data);