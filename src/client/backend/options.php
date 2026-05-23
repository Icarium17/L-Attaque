<?php

    require_once("action/OptionsAction.php");

    $action = new OptionsAction();

    $data = $action->execute();

    echo json_encode($data);