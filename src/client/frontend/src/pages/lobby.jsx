import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";

import backgroundLobby from '../assets/images/background-lobby.jpg';
import logo from '../assets/images/logo.png';

export default function Lobby() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
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

 
  const goToGame = () => {
    navigate("/game");  
  };
    
  return (
    <MainLayout
      title="Lobby - L'Attaque"
      background={backgroundLobby}
      session={session}
      hideMenu={true}
    >
      <div className="relative flex flex-col items-center justify-center">        
        <div className="absolute inset-0 bg-gray-950/50" />
         <div className="relative z-10 flex flex-col items-center justify-center w-full px-6">          
          <img
            src={logo}
            alt="Logo du Jeu"
            className="max-w-full md:max-w-3xl h-auto drop-shadow-2xl mb-12"
          />
        </div>
         </div>      
         <div className="absolute top-[22%] left-[1%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                >
                NOUVEAU JEU
                </Button>  
          </div>
            <div className="absolute top-[34.5%] left-[1%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                >
                REPRENDRE
                </Button>  
          </div>
            <div className="absolute top-[47%] left-[1%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                >
                CLASSEMENT
                </Button>  
          </div>
       <div className="absolute top-[60%] left-[1%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                >
                OPTIONS
                </Button>  
          </div>
      <div className="absolute top-[72%] left-[1%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,2.1vw,32px)]"
                >
                QUITTER
                </Button>                     
          </div>          
                <div className="absolute top-[90%] left-[42%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[clamp(16px,1.6vw,28px)]"
                >
                TUTORIEL
                </Button>                     
          </div>
          {error && <div className="mt-4"><Notification message={error} /></div>}
      </MainLayout>
  );
}