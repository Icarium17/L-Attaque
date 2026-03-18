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

  // 1. Vérification de la session au montage
  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    
    if (!key || !username) {
      //navigate("/"); // Retour à l'accueil si non connecté
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
            className="max-w-full md:max-w-2xl h-auto drop-shadow-2xl mb-12"
          />
        </div>
         </div>
      
         <div className="absolute top-[21.5%] left-[4%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[42px]"
                >
                NOUVEAU JEU
                </Button>  

          </div>

            <div className="absolute top-[34%] left-[4%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[42px]"
                >
                REPRENDRE
                </Button>  

          </div>

            <div className="absolute top-[46%] left-[4%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[42px]"
                >
                CLASSEMENT
                </Button>  

          </div>

       <div className="absolute top-[59%] left-[4%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[42px]"
                >
                OPTIONS
                </Button>  

          </div>

      <div className="absolute top-[71%] left-[4%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[42px]"
                >
                QUITTER
                </Button>  

                   
          </div>
          
                <div className="absolute top-[90%] left-[45.7%] w-[22%] flex flex-col gap-[3%] z-10">
                <Button 
                variant="ghost"
                onClick={goToGame} 
                className="w-full sm:w-2/3 text-[37px]"
                >
                TUTORIEL
                </Button>  

                   
          </div>
          

          

          

          


 
          {error && <div className="mt-4"><Notification message={error} /></div>}
          
       
     
    </MainLayout>
  );
}