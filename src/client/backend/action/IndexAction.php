<?php
// Inclusion de la classe parente CommonAction
require_once("action/CommonAction.php");

class IndexAction extends CommonAction {
     // La page d'accueil  publique accessible sans connexion
    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_PUBLIC);
    }
    
// Implémentation de l'action spécifique à la page d'accueil
protected function executeAction() {
    //Donnees de test
    $dataToSend = [
        "pion" => "General", 
        "colonne" => "B", 
        "ligne" => 4
    ];

    // On récupère  depuis le formulaire du frontend (via POST)
    //$dataFromFrontend = [
    //    "pion" => $_POST["pion"] ?? null, 
    //    "colonne" => $_POST["colonne"] ?? null, 
    //    "ligne" => $_POST["ligne"] ?? null
    //];

    // Appel service "move" de l'API Python avec les données du mouvement
    $result = $this->callPython("move", $dataToSend); 

    // Retourne le résultat de l'API  enrichi par execute() dans CommonAction
    return $result;
}
}