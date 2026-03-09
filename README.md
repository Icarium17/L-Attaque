# L-Attaque : Jeu Stratego
**Projet Synthèse H-2026**

**Équipe :**
* DUPRAS, Charlotte
* HUART, Eddy

## Prérequis : Installations sur le client

# Installation PHP 

Téléchargement : Allez sur php.net/downloads, cliquez sur "Windows downloads" et téléchargez le Zip VS17 x64 Thread Safe.

Installation : Extrayez le contenu dans C:\php.

Configuration : Dans C:\php, faites une copie de php.ini-development et nommez-la php.ini.

PATH : Ouvrez PowerShell en tant qu'administrateur et lancez la commande suivante: [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\php", "Machine")

Test : Tapez php -v dans un nouveau terminal qui retourne la version installée.

# Installation Node.js

Téléchargement : Allez sur nodejs.org et télécharger la version LTS.

Lance l'installeur .msi.

PATH : Durant l'installation, avoir l'option "Add to PATH" cochée (elle l'est par défaut). 
________________________________________________________________
## Lancement du Serveur (Backend Python)

Le backend tourne sur un serveur distant DigitalOcean.

# Comnexion SSH:
ssh root@68.183.195.223
Mot de passe : stratego

# Démarrage du script:
cd /root/LAttaque/Backend && /root/venv/bin/python3 main.py

# En cas de port bloqué:
Pour libérer le port 5000 si le serveur ne veut pas redémarrer :
`fuser -k 5000/tcp`

_______________________________________________________________
## Lancement du frontend client

Ouvrez le dossier client dans **VS Code**.
Ouvrez un terminal dans le répertoire : `L-Attaque\src\client\frontend`.
Exécutez les commandes :

npm install
npm run dev
________________________________________________________________
## Lancement du backend client

Ouvrez le dossier client dans **VS Code**.
Ouvrez un terminal dans le répertoire : `L-Attaque\src\client\backend`.
Lancez la commande :
php -S localhost:8000

Ou utilisez le fichier `Lancer_Jeu.bat` qui automatise cette tâche.

________________________________________________________________
## Modification des fichiers sur le Serveur

# Via Nano (Terminal)
1. Connectez-vous en SSH.
2. Accédez au dossier : `cd /root/LAttaque/Backend`.
3. Éditez : `nano main.py`.
4. **Appliquer les changements :** Toujours libérer le port et relancer le script après modification.
```bash
    fuser -k 5000/tcp
    /root/venv/bin/python3 main.py
```

# Via VS Code (Remote-SSH)
1. **Créer le fichier config :** Dans PowerShell : `notepad $env:USERPROFILE\.ssh\config`.
2. **Ajouter la configuration :**
    ```text
    Host 68.183.195.223
        User root
        IdentityFile ~/.ssh/id_ed25519
    ```
3. **Connexion :** `F1` -> `Remote-SSH: Connect to Host` -> `68.183.195.223` -> MDP: `stratego`.

________________________________________________________________
## Transfert de fichiers (SCP)

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

Exemple pour copier le fichier main.py :
scp main.py root@68.183.195.223:/root/LAttaque/Backend/main.py

Exemple pour écraser tout le dossier Backend :
scp -r Backend root@68.183.195.223:/root/LAttaque/

________________________________________________________________
## Autoriser la communication Client-Serveur
Pour que le PHP puisse communiquer avec le Python sur le port 5000 :
```bash
ufw allow 5000/tcp
```
________________________________________________________________
## Problèmes de connexion refusée (DigitalOcean)

Si l'accès SSH est bloqué, utilisez la console "Remote Access" de DigitalOcean et tapez :

ufw status               # Vérifier les règles
ufw delete limit 22/tcp  
ufw allow 22/tcp         
ufw reload   
________________________________________________________________            
## Se connecter à la base de données mysql lattaque

Infos SQL:
    * user : lattaque_user
    * password: stratego
    * base de données: lattaque

Dans l'invite de commande (connecté en tant que root)
    * sudo mysql

Pour le backend python: 
    * pip install mysql-connector-python 
    * pip install bcrypt


    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="lattaque_user",
        password="stratego",
        database="lattaque"
    )


________________________________________________________________   