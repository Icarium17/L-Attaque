import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";
import Loading from "../components/loading.jsx";
import MainLayout from "../layouts/main-layout";
import background from '../assets/images/background-index.png';
import logo from '../assets/images/logo.png';
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

export default function Index() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [loginForm, setLoginForm] = useState({ nom: "", motDePasse: "" });
  const [registerForm, setRegisterForm] = useState({ nom: "", motDePasse: "" });
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [redirecting, setRedirecting] = useState(false);
  const [mode, setMode] = useState("login"); // mode de formulaire login ou register

  // Évaluation des critères du mot de passe
  const passwordCriteria = {
    length: registerForm.motDePasse.length >= 6,
    uppercase: /[A-Z]/.test(registerForm.motDePasse),
    lowercase: /[a-z]/.test(registerForm.motDePasse),
    number: /[0-9]/.test(registerForm.motDePasse),
    special: /[^A-Za-z0-9]/.test(registerForm.motDePasse),
  };

  // Vérifie si tous les critères sont respectés
  const isPasswordValid = Object.values(passwordCriteria).every(Boolean);

  // Vérifier session au chargement
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (key && username) {
      setSession({ username, key });
    }
    setLoginForm({ nom: "", motDePasse: "" });
    setRegisterForm({ nom: "", motDePasse: "" });
  }, []);

  // Fonction gérer le signin et le signout
  const auth = (action, data1 = "", data2 = "") => {
    setLoading(true);
    let formData = new FormData();
    formData.append("action", action);

    if (action == "signin") {
      formData.append("nom", data1);
      formData.append("motDePasse", data2);
    } else {
      formData.append("key", data1);
    }

    fetch("/api/index.php", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        setLoading(false);

        // SIGNIN REUSSI
        if (action == "signin" && data.result.success) {
          setRedirecting(true);
          setSuccess(`Bienvenue ${data.result.username} !`);
          localStorage.setItem("sessionKey", data.result.key);
          localStorage.setItem("username", data.result.username);
          setTimeout(() => {
            setSession({ username: data.result.username, key: data.result.key });
            navigate("/lobby");
            setRedirecting(false);
          }, 3000);
        }

        // SIGNOUT REUSSI
        else if (action == "signout" && data.response_svr.status == "USER_DISCONNECTED") {
          setRedirecting(true);
          setSuccess("Déconnexion réussie");
          setTimeout(() => {
            localStorage.removeItem("sessionKey");
            localStorage.removeItem("username");
            setSession(null);
            setRedirecting(false);
            setSuccess("");
          }, 1000);
        }

        // Erreurs
        else if (data.result.error) {
          setError(data.result.error);
          setTimeout(() => setError(""), 3000);
          if (action == "signin") setLoginForm({ nom: "", motDePasse: "" });
        }
      })
      .catch(() => {
        setLoading(false);
        setError("Erreur serveur");
      });
  };

  const register = () => {
    // On bloque si le mot de passe ne respecte pas les critères
    if (!isPasswordValid) {
      setError("Le mot de passe ne respecte pas les critères.");
      setTimeout(() => setError(""), 3000);
      return;
    }

    setLoading(true); 
    let formData = new FormData();
    formData.append("action", "register");
    formData.append("nom", registerForm.nom);
    formData.append("motDePasse", registerForm.motDePasse);

    fetch("/api/index.php", { method: "POST", body: formData })
      .then((response) => response.json())
      .then((data) => {
        setLoading(false); 
        setRedirecting(true);  
        if (data.result.error) {
          setError(data.result.error);                  
          setRegisterForm({ nom: "", motDePasse: "" });
          setTimeout(() => setError(""), 5000);
        } else {
          localStorage.setItem("sessionKey", data.result.key);
          localStorage.setItem("username", data.result.username);
          setSuccess(`Compte "${data.result.username}" créé`);
          setTimeout(() => {
            setSession({ username: data.result.username, key: data.result.key });  
            navigate("/lobby");
          }, 3000);
        }
      })   
      .catch(() => {
        setLoading(false);  
        setError("Erreur d'inscription.");
      });
  };

  // Affichage pendant la session
  if (session) {
    return (
      <MainLayout title="Accueil" background={background} session={session} hideMenu={true}>
        <div className="relative flex flex-col justify-center items-center min-h-screen w-full overflow-hidden">
          <div className="absolute inset-0 bg-gray-950/70" />
          
          <div className="relative z-10 flex flex-col items-center gap-8 p-10 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
            <img src={logo} alt="Logo" className="max-w-3xl h-auto drop-shadow-2xl" />
            <h1 className="text-white text-4xl md:text-5xl font-bold text-center">
              Bienvenue dans l'Attaque, <span className="text-primary">{session.username}</span> !
            </h1>
            <Button
              className="w-full max-w-sm mx-auto text-xl py-3"
              variant="secondary"
              onClick={() => auth("signout", session.key)}
            >
              Se déconnecter
            </Button>
            <Button 
              className="w-full max-w-sm mx-auto text-xl py-3"
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
            >
              RESET
            </Button>
          </div>
          {error && (
            <div className="absolute bottom-10 z-50 w-full max-w-lg">
              <Notification variant="error" message={error} onClose={() => setError("")} />
            </div>
          )}
          {success && (
            <div className="absolute bottom-10 z-50 w-full max-w-lg">
              <Notification variant="success" message={success} onClose={() => setSuccess("")} />
            </div>
          )}
        </div>
        {(loading || redirecting) && <Loading silent={true} />}
      </MainLayout>
    );
  }

  return (
    <MainLayout
      title="Accueil"
      background={background}
      session={session}
      hideMenu={true}
    >
      <div className="relative flex flex-col justify-start items-center min-h-screen w-full overflow-hidden">
        <div className="absolute inset-0 bg-gray-950/70" />

        <div className="relative z-10 flex flex-col items-center mt-32 w-full max-w-7xl">
          <img
            src={logo}
            alt="Logo du Jeu"
            className="max-w-3xl h-auto drop-shadow-2xl mb-12"
          />

          <div className="flex flex-col items-center gap-8 p-10 bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-lg">
            {mode == "login" ? (
              <>
                {/* Section Connexion */}
                <h1 className="text-white text-3xl font-bold text-center">
                  Vous avez déjà un compte
                </h1>
                <div className="flex flex-col gap-6 items-center w-full max-w-sm">
                  <input
                    type="text"
                    placeholder="Nom d'utilisateur"
                    autoComplete="off"
                    value={loginForm.nom}
                    onChange={(e) => setLoginForm({ ...loginForm, nom: e.target.value })}
                    className="w-full p-5 text-lg rounded-xl bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-primary focus:outline-none transition-all"
                  />
                  <input
                    type="password"
                    placeholder="Mot de passe"
                    value={loginForm.motDePasse}
                    onChange={(e) => setLoginForm({ ...loginForm, motDePasse: e.target.value })}
                    className="w-full p-5 text-lg rounded-xl bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-primary focus:outline-none transition-all"
                  />
                  <Button 
                    className="w-full text-lg py-3 mt-2"
                    variant="primary"
                    onClick={() => auth("signin", loginForm.nom, loginForm.motDePasse)}
                  >
                    Se connecter
                  </Button>
                </div>
                <p className="text-gray-300 text-lg mt-2">
                  Pas de compte ?{" "}
                  <span className="text-blue-400 font-semibold cursor-pointer underline hover:text-blue-300" onClick={() => setMode("register")}>
                    Créer un compte
                  </span>
                </p>
              </>
            ) : (
              <>
                {/* Section Inscription */}
                <h1 className="text-white text-3xl font-bold text-center">
                  Nouveau compte
                </h1>
                <div className="flex flex-col gap-5 items-center w-full max-w-sm">
                  <input
                    type="text"
                    placeholder="Nouveau nom d'utilisateur"
                    value={registerForm.nom}
                    onChange={(e) => setRegisterForm({ ...registerForm, nom: e.target.value })}
                    className="w-full p-5 text-lg rounded-xl bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-danger focus:outline-none transition-all"
                  />
                  <input
                    type="password"
                    placeholder="Nouveau mot de passe"
                    value={registerForm.motDePasse}
                    onChange={(e) => setRegisterForm({ ...registerForm, motDePasse: e.target.value })}
                    className="w-full p-5 text-lg rounded-xl bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-danger focus:outline-none transition-all"
                  />
                  
                  {/* Affichage dynamique des critères */}
                  <div className="w-full text-base flex flex-col gap-2 p-4 bg-black/30 rounded-xl text-left shadow-inner">
                    <span className={passwordCriteria.length ? "text-green-400 font-medium" : "text-gray-300"}>
                      {passwordCriteria.length ? "✓" : "○"} 6 caractères minimum
                    </span>
                    <span className={passwordCriteria.uppercase ? "text-green-400 font-medium" : "text-gray-300"}>
                      {passwordCriteria.uppercase ? "✓" : "○"} Une majuscule
                    </span>
                    <span className={passwordCriteria.lowercase ? "text-green-400 font-medium" : "text-gray-300"}>
                      {passwordCriteria.lowercase ? "✓" : "○"} Une minuscule
                    </span>
                    <span className={passwordCriteria.number ? "text-green-400 font-medium" : "text-gray-300"}>
                      {passwordCriteria.number ? "✓" : "○"} Un chiffre
                    </span>
                    <span className={passwordCriteria.special ? "text-green-400 font-medium" : "text-gray-300"}>
                      {passwordCriteria.special ? "✓" : "○"} Un caractère spécial
                    </span>
                  </div>

                  <Button
                    className="w-full text-lg py-3 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    variant="secondary"
                    onClick={register}
                    disabled={!isPasswordValid || registerForm.nom.trim() === ""}
                  >
                    Créer un compte
                  </Button>
                </div>
                <p className="text-gray-300 text-lg mt-2">
                  Déjà un compte ?{" "}
                  <span className="text-blue-400 font-semibold cursor-pointer underline hover:text-blue-300" onClick={() => setMode("login")}>
                    Se connecter
                  </span>
                </p>
              </>
            )}
          </div>

          {error && (
            <div className="mt-8 w-full max-w-lg">
              <Notification
                variant="error"
                message={error}
                autoClose={3000}
                onClose={() => setError("")}
              />
            </div>
          )}

          {success && (
            <div className="mt-8 w-full max-w-lg">
              <Notification
                variant="success"
                message={success}
                autoClose={5000}
                onClose={() => setSuccess("")}
              />
            </div>
          )}
        </div>
      </div>

      {(loading || redirecting) && <Loading silent={true} />}
    </MainLayout>
  );
}