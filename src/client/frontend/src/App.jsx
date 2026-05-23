import { Routes, Route } from "react-router";

import Index from "./pages/index";
import Lobby from "./pages/lobby";
import Game from "./pages/game";
import Admin from "./pages/admin";
import LeaderBoard from './pages/leaderboard'
import Tutorial from './pages/tutorial'
import Options from './pages/options'

export default function App() {
  return (
<Routes>
      <Route path="/" element={<Index />} />
      <Route path="/lobby" element={<Lobby />} />
      <Route path="/game" element={<Game key={location.key} />} />
      <Route path="/admin" element={<Admin/>} />
      <Route path="/leaderboard" element={<LeaderBoard />} />
      <Route path="/tutorial" element={<Tutorial />} />
      <Route path="/options" element={<Options />} />
    </Routes>
  );
}