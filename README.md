# L-Attaque
Jeu Stratego Projet Synthèse H-2026

DUPRAS, Charlotte
HUART, Eddy

##  Commandes:
Lancement du serveur:

+ ouvrir une invite de commande:
ssh root@68.183.195.223

+ entrer le mot de passe:
stratego

cd /root/LAttaque/Backend
/root/venv/bin/python3 main.py

Pour liberer le port au besoin:
fuser -k 5000/tcp

______________________________________________________
Lancement du client:

+Ouvrir le dossier client dans vs code

+Ouvrir un terminal dans:
L-Attaque\src\client\backend>

+Lancer la commnande:
php -S localhost:8000 

______________________________________________________
Pour  modifier les fihiers python avec nano:

ex avec main.py:
+ ouvrir une invite de commande:
ssh root@68.183.195.223

cd /root/LAttaque/Backend
nano main.py

Après la modification :
Toujours libérer le port et relancer pour que les changements soient ok:

fuser -k 5000/tcp

/root/venv/bin/python3 main.py

cd /root/LAttaque/Backend && /root/venv/bin/python3 main.py

___________________________________________________
Pour gerer le serveur depuis vscode:

1. Ouvrir PowerShell et créer le fichier config :

notepad $env:USERPROFILE\.ssh\config
Host 68.183.195.223
    User root
    IdentityFile ~/.ssh/id_ed25519

2.Sauvegarder et fermer

3.Installer l'extension Remote-SSH dans VS Code : Ctrl+Shift+X → chercher Remote - SSH → installer.

4.  Se Connecter : F1 → Remote-SSH: Connect to Host → choisir 68.183.195.223 → entre le mot de passe de root:stratego

______________________________________________________
# Pour que PHP puisse parler à Python:

ufw allow 5000/tcp  
___________________________________________________
Si problemes de connexion refusees dans DigitalOcean:

A taper dans remote access:

ufw status   // verif les regles

ufw delete limit 22/tcp
ufw delete limit 22/tcp                  
ufw allow 22/tcp
ufw reload
___________________________________________________
Secure Copy du fichier main.py vers le serveur:

Ouvrir un terminal ou il y a le fichier a copier:

scp main.py root@68.183.195.223:/root/LAttaque/Backend/main.py
___________________________________________________
Copie du dossier Backend et ses fichiers et ecrase sur le serveur 
scp -r Backend root@68.183.195.223:/root/LAttaque/