import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";

import backgroundLobby from '../assets/images/background-lobby.png';
import logo from '../assets/images/logo.png';
import buttonBg from '../assets/images/button-bg.png';


export default function Lobby() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Si pas en session redirige vers index.jsx
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    
    if (!key || !username) {
    } else {
      setSession({ username, key });
    }
  }, [navigate]);

 
  const initGame = (mode) => {
    if (!session) return;
    
    setLoading(true);
    let formData = new FormData();
    
    formData.append("action", "start_game"); 
    formData.append("key", session.key);
    formData.append("mode", mode);

    fetch("/api/lobby.php", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        setLoading(false);

        if (data.result && data.result.success) {
          navigate("/game", { state: { gameMode: mode } });  
        } 
        else if (data.result && data.result.error) {
          setError(data.result.error);
          setTimeout(() => setError(""), 3000);
        }
      })
      .catch(() => {
        setLoading(false);
        setError("Erreur serveur");
        setTimeout(() => setError(""), 3000);
      });
  };
    
  return (
    <MainLayout
      title="Lobby - L'Attaque"
      background={backgroundLobby}
      session={session}
      hideMenu={true}
    >

      <div className="relative flex flex-col items-center justify-center ml-72">        
        <div className="absolute inset-0 bg-gray-950/50" />
         <div className="relative z-10 flex flex-col items-center justify-center w-full px-6">          
          <img
            src={logo}
            alt="Logo du Jeu"
            className="max-w-full md:max-w-4xl h-auto drop-shadow-2xl mb-12"
          />
        </div>
         </div>      

         <div className="absolute top-[14%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={() => initGame('ai')}
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}                 
                >
                CONTRE L'IA
                </Button>  
          </div>
          <div className="absolute top-[26%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={() => initGame('multiplayer')} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}          
                >
                CONTRE LE JOUEUR
                </Button>  
          </div>
            <div className="absolute top-[38%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}          
                >
                REPRENDRE
                </Button>  
          </div>
            <div className="absolute top-[50%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={() => navigate("/leaderboard")}
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}          
                >
                CLASSEMENT
                </Button>  
          </div>
          <div className="absolute top-[62%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                    <Button 
                    variant="ghost"
                    className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                    style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}          
                    >
                    OPTIONS
                    </Button>  
              </div>
         <div className="absolute top-[74%] left-[1.5%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                style={{ background: `url(${buttonBg}) center/100% 100% no-repeat` ,minHeight: '140px'  }}          
                >
                QUITTER
                </Button>                     
          </div>          
                <div className="absolute top-[92%] left-[45%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={() => navigate("/tutorial")}
                className="w-full sm:w-2/3 text-[clamp(16px,1.6vw,28px)]"
                >
                TUTORIEL
                </Button>                     
          </div>
          {error && <div className="mt-4"><Notification message={error} /></div>}
            
      </MainLayout>
  );
}