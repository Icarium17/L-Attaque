<?php
session_start(); // Démarrage de la session PHP 

// Classe abstraite  base de toutes les actions du site
abstract class CommonAction {
    protected static $VISIBILITY_PUBLIC = 0;
    protected static $VISIBILITY_MEMBER = 1;
    protected static $VISIBILITY_MODERATOR = 2;
    protected static $VISIBILITY_ADMINISTRATOR = 3;
    private $pageVisibility; // Niveau de visibilité requis pour accéder à cette page

    // Le constructeur reçoit le niveau de visibilité minimum requis  
    public function __construct($pageVisibility) {
        $this->pageVisibility = $pageVisibility;
    }

    // Méthode d'exécution d'une action
    public function execute() {      
        
        // Si le paramètre "logout" alors on detruit
        if (!empty($_GET["logout"])) {
            session_destroy();
            session_start();
        }

        if (!isset($_SESSION["visibility"])) {
            $_SESSION["visibility"] = self::$VISIBILITY_PUBLIC;
        }

        // Redirige si niveau de visibilte non atteint
        if ($_SESSION["visibility"] < $this->pageVisibility) {
            header("location:login.php");
            exit;
        }

        // Exécution de l'action spécifique définie dans la classe enfant
        $data = $this->executeAction();

        // Ajout au tableau de donnees: etat de connexion et username
        $data["isLoggedIn"] = isset($_SESSION["visibility"]) && $_SESSION["visibility"] > self::$VISIBILITY_PUBLIC;
        $data["username"] = $_SESSION["username"] ?? "Invite";

        return $data;
    }

    
    // Méthode utilitaire  appeler le backend Python (API Flask)
    // $service et $data (les données à envoyer en JSON)
    protected function callPython($service, $data) {
        $url = "http://68.183.195.223:5000/" . $service; 
        
        // Configuration de la requete HTTP POST avec les donnees en JSON
        $options = [
            'http' => [
                'header'  => "Content-type: application/json\r\n",
                'method'  => 'POST',
                'content' => json_encode($data)
            ]
        ];

        // Envoi de la requete et récupération de la réponse
        $context  = stream_context_create($options);
        $result = file_get_contents($url, false, $context);
        
       
       return json_decode($result);
    }
 
    protected abstract function executeAction();
}