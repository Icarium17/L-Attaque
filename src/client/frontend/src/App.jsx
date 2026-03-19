import { Routes, Route } from "react-router";

import Index from "./pages/index";
import Lobby from "./pages/lobby";
import Game from "./pages/game";
import Admin from "./pages/admin";

export default function App() {
  return (
<Routes>
      <Route path="/" element={<Index />} />
      <Route path="/lobby" element={<Lobby />} />
      <Route path="/game" element={<Game />} />
      <Route path="/admin" element={<Admin/>} />
    </Routes>
  );
}