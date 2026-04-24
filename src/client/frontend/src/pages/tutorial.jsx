import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout.jsx";
import Button from "../components/button.jsx";
import backgroundtutorial from '../assets/images/background-tutorial.png';
import placementVideo from '../assets/placement-video.mp4';

export default function LeaderBoard() {
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
      <div className="absolute top-[3%] left-1/2 -translate-x-1/2 w-[60%] z-10">
      <video autoPlay loop muted playsInline className="w-full h-auto border-10 border-yellow-600 rounded-xl shadow-lg">
      <source src={placementVideo} type="video/mp4" />
      </video>
      </div>

      <div className="absolute top-[90%] left-1/2 -translate-x-1/2 w-[22%] flex flex-col gap-[3%] z-10">
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