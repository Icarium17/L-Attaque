import Button from "../components/button.jsx";
import MainLayout from "../layouts/main-layout";
import background from '../assets/images/background-image.png';
import logo from '../assets/images/logo.png';
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

export default function Index() {
  const [session, setSession] = useState(null);
  const [addForm, setAddForm] = useState({ nom: "", motDePasse: "" });
  const navigate = useNavigate();


   // Fonction commune pour gérer le signin et le signout
  const auth = (action, data1 = "", data2 = "") => {
    let formData = new FormData();
    formData.append("action", action);

    if (action == "signin") {
      formData.append("nom", data1);
      formData.append("motDePasse", data2);
    } else if (action == "signout") {
      formData.append("key", data1);
    }

    fetch("/api/index.php", {
      method: "POST",
      body: formData
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.result.error) {
          setError(data.result.error);
          setTimeout(() => setError(""), 2000);
          setAddForm({ nom: "", motDePasse: "" }); 
        } else if (data.result.success) {
          if (action == "signin") {
            localStorage.setItem("sessionKey", data.result.key);
            localStorage.setItem("username", data.result.username);

            setSession({
              username: data.result.username,
              key: data.result.key
            });
            setAddForm({ nom: "", motDePasse: "" });
            navigate("/lobby");
          } else if (action == "signout") {
            localStorage.removeItem("sessionKey");
            localStorage.removeItem("username");
            setSession(null);
          }
        }
      });
  };

  return (
    <MainLayout
      title="Accueil"
      background={background}
      session={session}
      hideMenu={true}
    >
      <div className="relative flex flex-col justify-start items-center min-h-screen w-full overflow-hidden">
        {/* Overlay */}
        <div className="absolute inset-0 bg-gray-950/70 " />

        <div className="relative z-10 flex flex-col items-center mt-40 w-full max-w-7xl ">
          {/* Logo */}
          <img 
            src={logo}
            alt="Logo du Jeu" 
            className="max-w-2xl h-auto drop-shadow-2xl mb-12"
          />

          {/* Grid de 2 colonnes */}
          <div className="grid grid-cols-1 mt-12 md:grid-cols-2 gap-12 w-full">
            
           {/* Section comptes existants */}
<div className="flex flex-col items-center gap-6 p-6 bg-white/10 rounded">
  <h1 className="text-white text-2xl font-bold text-center">Vous avez déjà un compte</h1>
  

  <div className="flex flex-col gap-8 items-center mt-8 w-64 "> 
   <Button className="w-84" variant="primary">Nom d'utilisateur</Button>
  <Button className="w-84" variant="secondary">Mot de passe</Button>
  <Button className="w-84" variant="danger">Se connecter</Button>
  </div>
</div>

{/* Section nouveaux comptes */}
<div className="flex flex-col justify-center items-center gap-6 p-6 bg-white/10 rounded">
  <h1 className="text-white text-2xl font-bold text-center">Vous n'avez pas encore de compte</h1>
  
  <div className="flex flex-col gap-4 items-center mt-4 w-64">
    <Button className="w-84" variant="danger">
      Créer un compte
    </Button>
  </div>
    </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}