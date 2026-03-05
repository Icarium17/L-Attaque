



@echo off
:: Ferme les instances de PHP en cours pour éviter les conflits de port
taskkill /f /im php.exe >nul 2>&1

:: Se déplace dans le répertoire où se trouve le script
cd /d "%~dp0"

:: Lance le serveur PHP en arrière-plan  
start /b php -S localhost:8000 -t client/backend

:: Attend 2 secondes pour laisser au serveur le temps de démarrer
timeout /t 2 >nul

:: Ouvre l'URL dans le navigateur par défaut
start http://localhost:8000