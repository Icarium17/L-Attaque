import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout.jsx";
import Button from "../components/button.jsx";
import PieceGallery from "../components/pieceGallery.jsx";
import backgroundtutorial from '../assets/images/background-tutorial.png';
import placementVideo from '../assets/placement-video.mp4';
import moveVideo from '../assets/move-video.mp4';
import attackVideo from '../assets/attack-video.mp4';
import texture from '../assets/images/parchemin-texture.png';
import victory from '../assets/images/victory.png';

const STEPS = [
  {
    title: "Les pièces",
    type: "gallery",
    texts: [
      "Votre armée est composée de 40 pièces au total.",
      "Chaque pièce possède un rang qui détermine sa force au combat.",
      "Un rang élevé bat toujours un rang inférieur.",
      "Certaines pièces ont des capacités spéciales (Éclaireur, Démineur, Espion).",
      "L'objectif est de capturer le Drapeau adverse sans perdre le vôtre."
    ],
  },
  {
    title: "Le placement",
    type: "video",
    video: placementVideo,
    texts: [
      "Placez vos 40 pièces sur les quatre premières rangées de votre camp.",
      "Cliquez sur une pièce de la réserve, puis sur une case du plateau.",
      "Le système de glisser-déposer (drag and drop) est également disponible.",
      "Le bouton 'Auto' génère une disposition aléatoire de vos unités.",
      "Validez votre position pour démarrer ou réinitialisez pour recommencer."
    ],
  },
  {
    title: "Les déplacements",
    type: "video",
    video: moveVideo, 
    texts: [
      "Les pièces avancent d'une seule case à la fois.",
      "Mouvements autorisés : avant, arrière, gauche et droite.",
      "L'Éclaireur peut franchir plusieurs cases libres en ligne droite.",
      "Le Drapeau est fixe et ne peut jamais être déplacé.",
      "Les Bombes restent immobiles à leur emplacement d'origine."
    ],
  },
  {
    title: "Les combats",
    type: "video",
    video: attackVideo, 
    texts: [
      "En cas d'attaque, la pièce au rang le plus bas est éliminée.",
      "Si les deux pièces ont le même rang, elles sont toutes deux retirées.",
      "L'Espion (1) élimine le Maréchal (10) s'il est l'attaquant.",
      "Seul le Démineur (3) peut attaquer une Bombe sans être détruit.",
      "L'identité d'une pièce n'est révélée qu'au moment de l'affrontement."
    ],
  },
  {
    title: "Gagner la partie",
    type: "image",
    image: victory,  
    texts: [
      "L'objectif est de trouver et capturer le Drapeau adverse.",
      "La victoire est immédiate dès que vous attaquez le Drapeau ennemi.",
      "Vous gagnez aussi si l'adversaire n'a plus aucun mouvement légal.",
      "Une armée totalement bloquée est contrainte à la capitulation.",
      "La mémoire et la déduction sont vos meilleurs atouts pour l'emporter."
    ],
  },
];

export default function Tutorial() {
  const [session, setSession] = useState(null);
  const [activeStep, setActiveStep] = useState(0); 
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

  const currentStep = STEPS[activeStep];

  return (
    <MainLayout
      title="Tutorial - L'Attaque"
      background={backgroundtutorial}
      session={session}
      hideMenu={true}
    >    
      <div className="absolute inset-0 flex flex-col items-center px-4 py-[2%]">
        {/* Onglets de navigation */}
        <div className="flex justify-center gap-1 sm:gap-2 fhd:gap-3 4k:gap-4 flex-wrap shrink-0">
          {STEPS.map((step, index) => (
            <button
              key={index}
              onClick={() => setActiveStep(index)}
              className={`px-3 py-2 sm:px-6 sm:py-2 fhd:px-7 fhd:py-3 4k:px-10 4k:py-4 text-sm sm:text-lg fhd:text-xl 4k:text-3xl font-bold rounded-t-xl border-4 4k:border-[6px] border-b-0 transition-colors ${
                activeStep == index
                  ? "bg-yellow-700 text-white border-yellow-600 shadow-lg"
                  : "bg-black/60 text-gray-400 border-gray-800 hover:bg-black/80 hover:text-white"
              }`}
            >
              {step.title.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Le Contenu : Galerie, Vidéo ou Image */}
        <div className="flex-1 min-h-0 w-full flex justify-center items-stretch py-2 fhd:py-3 4k:py-4">
          {currentStep.type == "gallery" ? (
            <div className="w-[58%] fhd:w-[56%] 4k:w-[54%] bg-black/80 rounded-xl rounded-t-none border-4 4k:border-[6px] border-yellow-700 overflow-y-auto">
              <PieceGallery playerColor="RED" />
            </div>
          ) : currentStep.type == "image" ? (
            <img 
              src={currentStep.image} 
              alt="Victoire"
              className="h-full w-auto max-w-full object-contain border-4 4k:border-[6px] border-yellow-600 rounded-xl rounded-t-none shadow-lg bg-black/40"
            />
          ) : (
            <video 
              key={activeStep} 
              autoPlay 
              loop 
              muted 
              playsInline 
              className="h-full w-auto max-w-full object-contain border-4 4k:border-[6px] border-yellow-600 rounded-xl rounded-t-none shadow-lg bg-black"
            >
              <source src={currentStep.video} type="video/mp4" />
            </video>
          )}
        </div>

        {/* ZONE DE TEXTE */}
        <div
          className="shrink-0 w-[54%] fhd:w-[52%] 4k:w-[50%] px-10 py-5 fhd:px-12 fhd:py-4 4k:px-16 4k:py-8 overflow-hidden border-4 4k:border-[6px] border-yellow-700 rounded-3xl"
          style={{
            backgroundImage: `url(${texture})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        >
          <div key={activeStep} className="relative h-28 fhd:h-28 4k:h-44 flex items-center justify-center text-lg sm:text-3xl fhd:text-3xl 4k:text-5xl text-center font-bold bg-black/40 text-white rounded-lg">
            <div>
              {currentStep.texts.map((text, index) => (
                <div key={index} className="flex flex-col justify-center h-full">
                  <p className={`pop delay-${index} m+10`}>
                  {text}
                </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* BOUTON RETOUR */}
        <div className="shrink-0 w-[12%] fhd:w-[11%] 4k:w-[10%] mt-3 fhd:mt-4 4k:mt-5">
          <Button variant="danger" onClick={goToLobby} className="w-full">
            RETOUR
          </Button>
        </div>
      </div>
    </MainLayout>
  );
}