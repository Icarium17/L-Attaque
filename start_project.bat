:: --- SCRIPT PARTIELLEMENT CONCU AVEC L AIDE DE GROK.COM ---

@echo off
setlocal enabledelayedexpansion

:: --- CONFIGURATION ---
set "WINDOW_TITLE=L-Attaque-Autorun"
title Initialisation en cours...

set "BASE=%~dp0"
set "FRONTEND_PATH=%BASE%src\client\frontend"
set "BACKEND_SERVER_PATH=%BASE%src\serveur"
set "BACKEND_CLIENT_PATH=%BASE%src\client\backend"

:: --- SSH ---
set "SSH_KEY=%USERPROFILE%\.ssh\id_ed25519"
set "SSH_TARGET=root@68.183.195.223"

: ---------------------
echo [NETTOYAGE] Fermeture des anciens processus...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM php.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul

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

echo [3/7] Verification cle SSH...
if not exist "%SSH_KEY%" (
    echo Aucune cle SSH trouvee. Generation en cours...
    ssh-keygen -t ed25519 -f "%SSH_KEY%" -N ""
    echo.
    type "%SSH_KEY%.pub" | ssh %SSH_TARGET% "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
    echo Cle SSH installee ! Plus besoin du mot de passe.
    echo.
) else (
    echo Cle SSH trouvee, connexion automatique.
)

echo [3.5/7] Demarrage Backend Python Flask...
ssh -i "%SSH_KEY%" %SSH_TARGET% "cd /root/LAttaque/Backend && fuser -k 5000/tcp 2>/dev/null; nohup /root/venv/bin/python3 main.py > flask.log 2>&1 &"
echo Flask demarre sur http://68.183.195.223:5000

echo [4/7] Demarrage Frontend React...
start "Client-Frontend-React" /min cmd /k "cd /d "%FRONTEND_PATH%" && title Client-Frontend-React && npm run dev"

echo [5/7] Demarrage Backend PHP...
start "Client-Backend-PHP" /min cmd /k "cd /d "%BACKEND_CLIENT_PATH%" && title Client-Backend-PHP && php -S localhost:8000"

echo [6/7] Initialisation ...
timeout /t 5 /nobreak > nul

echo [7/7] Ouverture des pages web...
start "" "http://68.183.195.223:5000"
start "" "http://localhost:8000"
start "" "http://localhost:5173"


echo.
echo =================================
echo     Script execute avec succes !
echo =================================
timeout /t 15 /nobreak
exit