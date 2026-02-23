@echo off
SETLOCAL EnableDelayedExpansion

:: Configuration
SET gitHubRepository=L-Attaque
SET gitHubDisplayName=Eddy HUART
SET gitHubEmail=e.ehuart@etu.cvm.qc.ca

echo ==========================================
echo  Script Git automatise - %gitHubRepository%
echo ==========================================
echo.

git config user.name "%gitHubDisplayName%"
git config user.email "%gitHubEmail%"

git status >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Ce dossier n'est pas un depot Git valide.
    goto STOP
)

echo.
set "commitMsg="
set /p "commitMsg=Entrez votre message de commit (SANS guillemets) : "

:: Nettoyage des guillemets au cas ou l'utilisateur en tape
if defined commitMsg (
    set "commitMsg=%commitMsg:"=%"
) else (
    set "commitMsg=Update automatique - %DATE% %TIME%"
)

echo.
echo [+] Ajout des fichiers...
git add .

echo [+] Verification des changements...
git diff --cached --quiet
if %errorlevel% neq 0 (
    echo [+] Creation du commit...
    :: Utilisation de quotes forcees ici pour englober tout le message
    git commit -m "!commitMsg!"
) else (
    echo [!] Aucun changement a commiter.
)

echo.
echo [+] Tentative de Push...
git push origin main
if %errorlevel% neq 0 (
    echo [!] Echec sur 'main', essai sur 'master'...
    git push origin master
)

:STOP
echo.
echo ==========================================
echo  TERMINE !
echo ==========================================
pause