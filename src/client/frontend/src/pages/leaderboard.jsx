import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import backgroundleader from '../assets/images/background-leader.png';

export default function LeaderBoard() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true); 
  
  const navigate = useNavigate();

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");

    if (key && username) {
      setSession({ username, key });
    }
  }, []);

  useEffect(() => {
    fetch("api/leaderboard.php", { method: "POST" })
      .then(res => res.json())
      .then(json => {
        if (json.result?.success) { 
          const playersArray = [];
          
          for (let key in json.result.data) {
            playersArray.push(json.result.data[key]);
          }

          playersArray.sort((a, b) => b.score - a.score);
          setLeaderboardData(playersArray);
        } else {
          setError(json.result?.error || "Erreur serveur.");
        }
      })
      .catch(err => {
        setError("Serveur injoignable.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const goToLobby = () => {
    navigate("/lobby");
  };

  return (
    <MainLayout
      title="Classement - L'Attaque"
      background={backgroundleader}
      session={session}
      hideMenu={true}
    >
      <div className="absolute top-[20%] left-1/2 -translate-x-1/2 w-[70%]">
        <div className="bg-gray-950/70 border-2 border-yellow-600/60 rounded-lg p-6">
          <h1 className="text-center text-yellow-500 text-4xl mb-6">
            CLASSEMENT
          </h1>
          
          {error && <div className="text-red-500 text-center mb-4">{error}</div>}

          <div 
            className={`rounded border border-yellow-700/40 ${
              leaderboardData.length > 10
                ? "max-h-112.5 overflow-y-auto scrollbar-thin scrollbar-thumb-yellow-700 scrollbar-track-transparent" 
                : "overflow-hidden"
            }`}
          >
            <table className="w-full text-center text-lg relative">
              <thead className="sticky top-0 bg-gray-900 text-yellow-300 z-10 shadow-md">
                <tr>
                  <th className="py-3 px-4">#</th>
                  <th className="py-3 px-4">Joueur</th>
                  <th className="py-3 px-4">Victoires</th>
                  <th className="py-3 px-4">Défaites</th>
                  <th className="py-3 px-4">Score</th>
                </tr>
              </thead>
              
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-gray-400 italic">
                      Chargement des scores...
                    </td>
                  </tr>
                ) : leaderboardData.length > 0 ? (
                  leaderboardData.map((player, index) => (
                    <tr key={index} className="border-t border-yellow-700/40 text-gray-100 hover:bg-gray-800/50 transition-colors">
                      <td className="py-3 px-4">{index + 1}</td>
                      <td className="py-3 px-4">{player.username || "Joueur"}</td>
                      <td className="py-3 px-4">{player.games_won || 0}</td>
                      <td className="py-3 px-4">{player.games_lost || 0}</td>
                      <td className="py-3 px-4">{player.score || 0}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-gray-400 italic">
                      Aucun résultat
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="absolute top-[90%] left-[45%] w-[22%] flex flex-col gap-[3%] z-10">
        <Button
          variant="danger"
          onClick={goToLobby}
          className="w-full sm:w-2/3"
        >
          RETOUR
        </Button>
      </div>
    </MainLayout>
  );
}