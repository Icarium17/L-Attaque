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
        setSuccess(`Ravi de vous revoir, ${data.result.username} !`);
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
        setSuccess("Déconnexion réussie.");
        setTimeout(() => {
          localStorage.removeItem("sessionKey");
          localStorage.removeItem("username");
          setSession(null);
          setRedirecting(false);
        }, 1000);
      }

      // Erreurs
      else if (data.result.error) {
        setError(data.result.error);
        setTimeout(() => setError(""), 2000);
        if (action == "signin") setLoginForm({ nom: "", motDePasse: "" });
      }
    })
    .catch(() => {
      setLoading(false);
      setError("Erreur serveur");
    });
};

  const register = () => {
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
          setSuccess(`Compte "${data.result.username}" créé avec succès!`);
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
          
          <div className="relative z-10 flex flex-col items-center gap-8 p-8 bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
            <img src={logo} alt="Logo" className="max-w-2xl h-auto drop-shadow-2xl" />
            <h1 className="text-white text-3xl font-bold text-center">
              Bienvenue dans l'Attaque, <span className="text-primary">{session.username}</span> !
            </h1>
            <Button
              className="w-64"
              variant="secondary"
              onClick={() => auth("signout", session.key)}
            >
              Se déconnecter
            </Button>
          <Button 
      
          onClick={() => {
            localStorage.clear();
            window.location.reload();
          }}
        >RESET
        </Button>
          </div>
          {error && (
            <div className="absolute bottom-10 z-50 w-full max-w-md">
              <Notification variant="error" message={error} onClose={() => setError("")} />
            </div>
          )}
          {success && (
            <div className="absolute bottom-10 z-50 w-full max-w-md">
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

        <div className="relative z-10 flex flex-col items-center mt-40 w-full max-w-7xl">
          <img
            src={logo}
            alt="Logo du Jeu"
            className="max-w-2xl h-auto drop-shadow-2xl mb-12"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 w-full max-w-4xl">
            {/* Section Connexion */}
            <div className="flex flex-col items-center gap-6 p-8 bg-white/10 backdrop-blur-md rounded-xl shadow-2xl">
              <h1 className="text-white text-2xl font-bold text-center">
                Vous avez déjà un compte
              </h1>
              <div className="flex flex-col gap-4 items-center w-80">
                <input
                  type="text"
                  placeholder="Nom d'utilisateur"
                  autoComplete="off"
                  value={loginForm.nom}
                  onChange={(e) => setLoginForm({ ...loginForm, nom: e.target.value })}
                  className="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-primary focus:outline-none transition-all"
                />
                <input
                  type="password"
                  placeholder="Mot de passe"
                  value={loginForm.motDePasse}
                  onChange={(e) => setLoginForm({ ...loginForm, motDePasse: e.target.value })}
                  className="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-primary focus:outline-none transition-all"
                />
                <Button
                  className="w-full"
                  variant="primary"
                  onClick={() => auth("signin", loginForm.nom, loginForm.motDePasse)}
                >
                  Se connecter
                </Button>
              </div>
            </div>

            {/* Section Inscription */}
            <div className="flex flex-col items-center gap-6 p-8 bg-white/10 backdrop-blur-md rounded-xl shadow-2xl">
              <h1 className="text-white text-2xl font-bold text-center">
                Nouveau compte
              </h1>
              <div className="flex flex-col gap-4 items-center w-80">
                <input
                  type="text"
                  placeholder="Nouveau nom d'utilisateur"
                  value={registerForm.nom}
                  onChange={(e) => setRegisterForm({ ...registerForm, nom: e.target.value })}
                  className="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-danger focus:outline-none transition-all"
                />
                <input
                  type="password"
                  placeholder="Nouveau mot de passe"
                  value={registerForm.motDePasse}
                  onChange={(e) => setRegisterForm({ ...registerForm, motDePasse: e.target.value })}
                  className="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 border border-white/30 focus:border-danger focus:outline-none transition-all"
                />
                <Button
                  className="w-full"
                  variant="secondary"
                  onClick={register}
                >
                  Créer un compte
                </Button>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-6 w-full max-w-md">
              <Notification
                variant="error"
                message={error}
                autoClose={3000}
                onClose={() => setError("")}
              />
            </div>
          )}

        {success && (
        <div className="mt-6 w-full max-w-md">
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
