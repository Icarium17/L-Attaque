<?php
    // Inclusion de la classe IndexAction 
    require_once("action/IndexAction.php");

    $action = new IndexAction();

    // Exécution de l'action :
    // Vérifie la session et les permissions, Appelle executeAction() , ajoute(isLoggedIn, username)
    $data = $action->execute();

    // Retourne le résultat final en JSON 
    echo json_encode($data);