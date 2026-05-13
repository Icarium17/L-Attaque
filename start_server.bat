@echo off
setlocal enabledelayedexpansion

:: --- CONFIGURATION SERVEUR ---
title Serveur - L-Attaque (Python Flask)
set "SSH_KEY=%USERPROFILE%\.ssh\id_ed25519"
set "SSH_TARGET=root@68.183.195.223"

echo [1/3] Verification de la cle SSH...
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

echo [2/3] Nettoyage de l'ancien processus Flask...
ssh -i "%SSH_KEY%" %SSH_TARGET% "fuser -k 5000/tcp 2>/dev/null"

echo [3/3] Demarrage du Backend Python Flask...
echo.
echo.

ssh -t -i "%SSH_KEY%" %SSH_TARGET% "cd /root/LAttaque/Backend && /root/venv/bin/python3 main.py"

pause