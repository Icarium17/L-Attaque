@echo off
setlocal enabledelayedexpansion

:: --- CONFIGURATION CLIENT ---
title Client - L-Attaque (React ^& PHP)

set "BASE=%~dp0"
set "FRONTEND_PATH=%BASE%src\client\frontend"
set "BACKEND_CLIENT_PATH=%BASE%src\client\backend"

echo [1/5] Nettoyage des processus locaux et navigateurs...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM php.exe /T >nul 2>&1
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM msedge.exe /T >nul 2>&1
taskkill /F /IM firefox.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul

echo [2/5] Verification des dependances Frontend...
if not exist "%FRONTEND_PATH%\node_modules\" (
    echo Installation npm...
    pushd "%FRONTEND_PATH%"
    call npm install
    popd
)

echo [3/5] Demarrage Backend PHP local...

start "Client-Backend-PHP" /min cmd /k "cd /d "%BACKEND_CLIENT_PATH%" && title Client-Backend-PHP && php -S localhost:8000"

echo [4/5] Demarrage Frontend React...
start "Client-Frontend-React" /min cmd /k "cd /d "%FRONTEND_PATH%" && title Client-Frontend-React && npm run dev"

echo [5/5] Initialisation...
timeout /t 5 /nobreak > nul

echo Ouverture des pages web... 
start "" "http://localhost:8000"
start "" "http://localhost:5173"

echo.
echo =================================
echo    Client demarre avec succes !
echo =================================
timeout /t 5 /nobreak
exit