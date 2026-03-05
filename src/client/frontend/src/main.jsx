import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from "react-router";
import './css/global.css'
import MainLayout from './layouts/main-layout';

// Importation des composants de pages
import Index from './pages/index'
import Lobby from './pages/lobby'
import Game from './pages/game'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Index />} />
      
      <Route path="/lobby" element={<MainLayout><Lobby /></MainLayout>} />
      
      <Route path="/game" element={<Game />} />
    </Routes>
  </BrowserRouter>
)