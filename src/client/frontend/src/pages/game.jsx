import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Notification from "../components/notification.jsx";

import backgroundGame from '../assets/images/background-game.png';
 

export default function Game() {
  const [session, setSession] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const key = localStorage.getItem("sessionKey");
    const username = localStorage.getItem("username");
    
    if (!key || !username) {
      navigate("/");
    } else {
      setSession({ username, key });
    }
  }, [navigate]);

  return (
    <MainLayout
      title="Game - L'Attaque"
      background={backgroundGame}
      session={session}
      hideMenu={true}
    >
      <div>hi</div>
    </MainLayout>
  );
}