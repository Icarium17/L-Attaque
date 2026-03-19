import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from "react-router";
import './css/global.css'

// Importation des composants de pages
import Index from './pages/index'
import Lobby from './pages/lobby'
import Game from './pages/game'
import Admin from './pages/admin'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/lobby" element={<Lobby />} />
      <Route path="/game" element={<Game />} />
      <Route path="/admin" element={<Admin />} />
    </Routes>
  </BrowserRouter>
)