import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from "react-router";
import './css/global.css'
import Index from './pages/index'

createRoot(document.getElementById('root')).render(
<BrowserRouter>
<Routes>
<Route path ="/" element = {<Index />} />
</Routes>
</BrowserRouter>
)
