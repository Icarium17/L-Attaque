import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout.jsx";
import Button from "../components/button.jsx";
import backgroundtutorial from '../assets/images/background-tutorial.png';
import placementVideo from '../assets/placement-video.mp4';
import texture from '../assets/images/parchemin-texture.png';  

export default function Tutorial() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");

    if (key && username) {
      setSession({ username, key });
    }
  }, [navigate]);

  const goToLobby = () => {
    navigate("/lobby");
  };

  return (
    <MainLayout
      title="Tutorial - L'Attaque"
      background={backgroundtutorial}
      session={session}
      hideMenu={true}
    >
      <div className="absolute top-[7%] left-1/2 -translate-x-1/2 w-[50%] z-10">
      <video autoPlay loop muted playsInline className="w-full h-auto border-10 border-yellow-600 rounded-xl shadow-lg">
      <source src={placementVideo} type="video/mp4" />
      </video>
      </div>
  
 
    <div
      className="absolute bottom-[18%] left-1/2 -translate-x-1/2 w-[50%] px-10 py-5   overflow-hidden border-4 border-yellow-700  rounded-3xl"
      style={{
        backgroundImage: `url(${texture})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >

  <div className="relative h-30 flex items-center justify-center text-shadow-gray-400 text-3xl leading-relaxed text-center font-bold bg-black/30">

    <p className="pop delay-0">
      Au début de la partie, chaque joueur dispose ses pièces comme il
      l’entend sur ses quatre premières rangées.
    </p>

    <p className="pop delay-1">
      Les pièces peuvent être placées en cliquant sur une pièce dans le
      pool de réserve puis sur une case du plateau.
    </p>

    <p className="pop delay-2">
      Les pièces peuvent aussi être placées en utilisant le
      système de glisser-déposer (drag and drop).
    </p>

    <p className="pop delay-3">
      Un bouton de placement automatique permet de générer une disposition des pièces aléatoires.
    </p>

    <p className="pop delay-4">
      Une fois le placement terminé, appuyez sur le bouton confirmer
      ou annuler pour recommencer.
    </p>
 </div>

</div>
      <div className="absolute top-[90%] left-1/2 -translate-x-1/2 w-[12%] flex flex-col gap-[3%] z-10">
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