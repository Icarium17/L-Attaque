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
            $key = $_SESSION["key"] ?? $_POST["key"] ?? null;

            if (empty($key)) {
                $success = true; 
                $message = "Aucune session active";
                return ["result" => compact("success", "message")];
            }

            $data = ["key" => $key];
            $apiResult = parent::callPython("signout", $data);

            if ($apiResult != null) {
                if ($apiResult->status == "USER_DISCONNECTED") {
                    session_destroy();
                    session_start();
                    $success = true;
                    $message = "Déconnexion réussie";
                    return ["result" => compact("success", "message"), "response_svr" => $apiResult];
                } 

                if ($apiResult->status == "INVALID_KEY") {                 
                    $error = "Clef invalide";
                    return ["result" => compact("error"), "response_svr" => $apiResult];
                }

                $error = "Erreur serveur : " . $apiResult->status;
                return ["result" => compact("error"), "response_svr" => $apiResult];
            } 

            $error = "Serveur Python hors-ligne";
            return ["result" => compact("error")];
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
                $error = "Serveur injoignable";
                return ["result" => compact("error")];
            }

            if ($apiResult->status == "INVALID_USERNAME_PASSWORD") {  
                $error = "Mauvais mot de passe";
                return ["result" => compact("error"), "response_svr" => $apiResult];
            }

            if ($apiResult->status == "ERROR" || $apiResult->status == "USER_ALREADY_EXISTS") {
                $error = "Le compte existe";
                return ["result" => compact("error"), "response_svr" => $apiResult];
            }

            // Inscription / connexion réussie
            $_SESSION["visibility"] = self::$VISIBILITY_MEMBER;
            $_SESSION["username"] = $nom;
            $_SESSION["key"] = $apiResult->key;

            $success  = true;
            $key      = $apiResult->key;
            $username = $nom;

            return ["result" => compact("success", "key", "username"), "response_svr" => $apiResult];
        }

        // SIGNIN (CONNEXION)
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

            if ( $apiResult == "INVALID_USERNAME_PASSWORD"){
                return ["result" =>compact()];}

            if ($apiResult == null) {
                $error = "Serveur injoignable";
                return ["result" => compact("error")];
            }

            if ($apiResult->status == "USER_CONNECTED") {
                // Détecter si le user est admin
                $usersResult = parent::callPython("get_all_users", ["key" => $apiResult->key]);
                $isAdmin = false;
                if ($usersResult && isset($usersResult->users)) {
                    foreach ($usersResult->users as $u) {
                        if ($u->username === $nom && ($u->rights ?? "User") === "Admin") {
                            $isAdmin = true;
                            break;
                        }
                    }
                }

                $_SESSION["visibility"] = $isAdmin
                    ? self::$VISIBILITY_ADMINISTRATOR
                    : self::$VISIBILITY_MEMBER;
                $_SESSION["username"] = $nom;
                $_SESSION["key"] = $apiResult->key;

                $success  = true;
                $key      = $apiResult->key;
                $username = $nom;
                return ["result" => compact("success", "key", "username", "isAdmin"), "response_svr" => $apiResult];
            }

            $error = "Erreur de mot de passe ";
            return ["result" => compact("error"), "response_svr" => $apiResult];
        }
    }
}