import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import MainLayout from "../layouts/main-layout";
import Button from "../components/button.jsx";
import Error from "../components/error.jsx";
import background from '../assets/images/background-image.png';
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


    return (<h1>hi</h1>)


}
