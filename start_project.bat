@echo off
setlocal enabledelayedexpansion

:: --- CONFIGURATION ---
set "WINDOW_TITLE=L-Attaque-Autorun" 
title Initialisation en cours... 

set "FRONTEND_PATH=src\client\frontend"
set "BACKEND_SERVER_PATH=src\serveur"
set "BACKEND_CLIENT_PATH=src\client\backend"
:: ---------------------

echo [NETTOYAGE] Fermeture des anciens processus...
taskkill /F /IM node.exe /T >nul 2>&1 
taskkill /F /IM python.exe /T >nul 2>&1 
taskkill /F /IM php.exe /T >nul 2>&1 
timeout /t 2 /nobreak > nul

:: Attribution du titre officiel
title %WINDOW_TITLE% 

echo [1/7] Nettoyage des navigateurs...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM msedge.exe /T >nul 2>&1
taskkill /F /IM firefox.exe /T >nul 2>&1

echo [2/7] Verification des dependances...
if not exist "%FRONTEND_PATH%\node_modules\" (
    echo Installation npm...
    pushd "%FRONTEND_PATH%"
    call npm install
    popd
)

echo [3/7] Demarrage Backend Python...
start "Server-Python" /min cmd /c "cd /d %BACKEND_SERVER_PATH% && title Server-Python && python main.py"

echo [4/7] Demarrage Frontend React...
start "Client-Frontend-React" /min cmd /k "cd /d %FRONTEND_PATH% && title Client-Frontend-React && npm run dev"

echo [5/7] Demarrage Backend PHP...
:: On force le titre "BACKEND_PHP" pour cette fenêtre spécifique
start "Client-Backend-PHP" /min cmd /c "cd /d %BACKEND_CLIENT_PATH% && title Client-Backend-PHP && php -S localhost:8000" 

echo [6/7] Initialisation (5s)...
timeout /t 5 /nobreak > nul

echo [7/7] Ouverture des navigateurs...
:: Note : Le titre ici ne peut pas être forcé via 'start' pour une URL, 
:: il dépend de la balise <title> dans votre code HTML (index.php ou index.html).
start "" "http://localhost:8000"
start "" "http://localhost:5173"

echo.
echo ================================= 
echo     Script execute avec succes ! 
echo ================================= 
echo Fermeture automatique dans 15 secondes...
timeout /t 15 /nobreak
exit