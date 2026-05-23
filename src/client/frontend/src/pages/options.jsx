import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";
import Loading from "../components/loading.jsx";

import backgroundLobby from '../assets/images/background-lobby.png';
import logo from '../assets/images/logo.png';
import buttonBg from '../assets/images/button-bg.png';

export default function Options() {
  const [session, setSession] = useState(null);
  const [difficulty, setDifficulty] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    if (key && username) {
      setSession({ username, key });
    }
    const savedDiff = localStorage.getItem("difficulty");
    if (savedDiff) setDifficulty(savedDiff);
  }, []);

  const saveDifficulty = (level) => {
    if (!session) return;
    setLoading(true);
    setDifficulty(level);

    let formData = new FormData();
    formData.append("action", "set_difficulty");
    formData.append("key", session.key);
    formData.append("difficulty", level);

    fetch("/api/options.php", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        setLoading(false);
        if (data.result && data.result.success) {
          localStorage.setItem("difficulty", level);
          setSuccess(`Difficulté : ${labelFor(level)}`);
          setTimeout(() => setSuccess(""), 2000);
        } else {
          setError(data.result?.error || "Erreur");
          setTimeout(() => setError(""), 3000);
        }
      })
      .catch(() => {
        setLoading(false);
        setError("Erreur serveur");
        setTimeout(() => setError(""), 3000);
      });
  };

  const labelFor = (level) => {
    if (level == "easy") return "Facile";
    if (level == "medium") return "Moyen";
    if (level == "hard") return "Difficile";
    return level;
  };

const diffBtnStyle = (level) => ({
  background: `url(${buttonBg}) center/100% 100% no-repeat`,
  minHeight: '150px',
  minWidth: '160px',
  fontSize: '24px',
  padding: '40px 30px',
  opacity: difficulty == level ? 1 : 0.6,
  outline: difficulty == level ? '3px solid #facc15' : 'none',
  outlineOffset: '-6px',
  borderRadius: '12px',
});

  return (
    <MainLayout
      title="Options - L'Attaque"
      background={backgroundLobby}
      session={session}
      hideMenu={true}
    >
      <div className="relative flex flex-col items-center justify-start min-h-screen w-full overflow-hidden">
        <div className="absolute inset-0 bg-gray-950/70" />

        <div className="relative z-10 flex flex-col items-center w-full max-w-5xl px-6 mt-20">
          <img
            src={logo}
            alt="Logo du Jeu"
            className="max-w-2xl h-auto drop-shadow-2xl mb-40"
          />

          <div className="flex flex-col items-center gap-8 p-10 bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-3xl border border-white/20">
            <h1 className="text-white text-4xl font-bold text-center">
               Niveau de difficulté de l'IA
            </h1>
            <div className="w-full flex flex-col gap-4">           
              <p className="text-gray-300 text-center text-4xl mb-4">
                Choix actuel : <span className="text-yellow-400 font-bold">{labelFor(difficulty)}</span>
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <Button
                  variant="ghost"
                  onClick={() => saveDifficulty("easy")}
                  className="w-full text-[clamp(16px,2vw,28px)]"
                  style={diffBtnStyle("easy")}
                >
                  FACILE
                </Button>

                <Button
                  variant="ghost"
                  onClick={() => saveDifficulty("medium")}
                  className="w-full text-[clamp(16px,2vw,28px)]"
                  style={diffBtnStyle("medium")}
                >
                  MOYEN
                </Button>

                <Button
                  variant="ghost"
                  onClick={() => saveDifficulty("hard")}
                  className="w-full text-[clamp(16px,2vw,28px)]"
                  style={diffBtnStyle("hard")}
                >
                  DIFFICILE
                </Button>
              </div>

              <div className="mt-6 p-4 bg-black/40 rounded-xl text-gray-200  text-center text-4xl">
                {difficulty == "easy" && "Débutant"}
                {difficulty == "medium" && "Intermédiaire"}
                {difficulty == "hard" && "Expert"}
              </div>
            </div>

            <Button
              variant="primary"
              onClick={() => navigate("/lobby")}
              className="w-full max-w-sm text-lg py-3 mt-4"
            >
              Retour 
            </Button>
          </div>

          {error && (
            <div className="mt-6 w-full max-w-lg">
              <Notification
                variant="error"
                message={error}
                autoClose={3000}
                onClose={() => setError("")}
              />
            </div>
          )}

          {success && (
            <div className="mt-6 w-full max-w-lg">
              <Notification
                variant="success"
                message={success}
                autoClose={2000}
                onClose={() => setSuccess("")}
              />
            </div>
          )}
        </div>
      </div>

      {loading && <Loading silent={true} />}
    </MainLayout>
  );
}