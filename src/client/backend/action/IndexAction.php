
<?php
require_once("action/CommonAction.php");

class IndexAction extends CommonAction {

    public function __construct() {
        parent::__construct(CommonAction::$VISIBILITY_PUBLIC);
    }

    protected function executeAction() {

        // Définir action login par défaut
        $action = isset($_POST["action"]) ? $_POST["action"] : "signin";

        // Déconnexion
        if ($action == "signout") {

            if (!isset($_SESSION["key"])) {
                $error = "Session non active";
                return ["result" => compact("error")];
            }

            $data = ["key" => $_SESSION["key"]];
            $apiResult = parent::callPython("signout", $data);

            if ($apiResult == "INVALID_KEY") {
                $error = "Clé de session invalide";
                return ["result" => compact("error")];
            }

            // Réinitialisation de la variable session
            session_destroy();
            session_start();

            $success = true;
            $message = "Déconnexion réussie";
            return ["result" => compact("success", "message")];
        }

        // Register
        elseif ($action == "register") {
            $nom = isset($_POST["nom"]) ? trim($_POST["nom"]) : "";
            $motDePasse = isset($_POST["motDePasse"]) ? trim($_POST["motDePasse"]) : "";

            if (empty($nom) || empty($motDePasse)) {
                $error = "Saisir login et mot de passe";
                return ["result" => compact("error")];
            }

            $data = [
                "username" => $nom,
                "password" => $motDePasse
            ];

            $apiResult = parent::callPython("signup", $data); 
 
            if ($apiResult == null) {
                $error = "Impossible de joindre le serveur.";
                return ["result" => compact("error")];
            }

            if ($apiResult == "INVALID_USERNAME_PASSWORD") {
                $error = "Mauvais mot de passe";
                return ["result" => compact("error")];
            }

            if ($apiResult == "USER_ALREADY_EXISTS") {
                $error = "Le compte existe  déjà";
                return ["result" => compact("error")];
            }

            // Inscription /connexion réussie
            $_SESSION["visibility"] = self::$VISIBILITY_MEMBER;
            $_SESSION["username"] = $nom;
            $_SESSION["key"] = $apiResult->key;

            $success  = true;
            $key      = $apiResult->key;
            $username = $nom;

            return ["result" => compact("success", "key", "username")];
        }

        // Sigin
        else {
            $nom = isset($_POST["nom"]) ? trim($_POST["nom"]) : "";
            $motDePasse = isset($_POST["motDePasse"]) ? trim($_POST["motDePasse"]) : "";

            if (empty($nom) || empty($motDePasse)) {
                $error = "Veuillez saisir les informations";
                return ["result" => compact("error")];
            }

            $data = [
                "username" => $nom,
                "password" => $motDePasse
            ];

            $apiResult = parent::callPython("signin", $data);

            if ($apiResult == "INVALID_USERNAME_PASSWORD") {
                $error = "Authentification échouée";
                return ["result" => compact("error")];
            }

            // Connexion réussie
            $_SESSION["visibility"] = self::$VISIBILITY_MEMBER;
            $_SESSION["username"] = $nom;
            $_SESSION["key"] = $apiResult->key;

            $success  = true;
            $key      = $apiResult->key;
            $username = $nom;

            return ["result" => compact("success", "key", "username")];
        }
    }
}