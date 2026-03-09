import Button from "../components/button.jsx";
import Error from "../components/error.jsx";

export default function Index() {
  return (
    <div className="min-h-screen bg-gray-950 p-10 flex flex-col items-center gap-6">
      <h1 className="text-white text-2xl mb-4">Menu Principal</h1>

      <Button variant="primary" onClick={() => alert("Nouveau jeu!")}>Nouveau Jeu</Button>
      <Button variant="secondary" onClick={() => alert("Options!")}>Options</Button>

      <Button variant="primary" loading>Chargement...</Button>

      <Button variant="primary" icon="⚔️">Combattre</Button>

      <Error>pb de pion</Error>
 
    </div>
  );
}