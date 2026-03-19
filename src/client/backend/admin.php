<?php

    require_once("action/AdminAction.php");
    $action = new AdminAction();
    $data = $action->execute();
    echo json_encode($data);