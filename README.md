# HomeDrive

HomeDrive est un serveur de stockage personnel accessible depuis un navigateur web.

Il permet notamment de :

- gérer des fichiers et des dossiers ;
- importer des fichiers ;
- télécharger des fichiers ;
- créer des dossiers ;
- créer et modifier des fichiers texte ;
- copier et déplacer des fichiers ;
- supprimer des fichiers ;
- utiliser une corbeille ;
- rechercher des fichiers ;
- partager des fichiers entre utilisateurs ;
- accéder au Drive depuis un téléphone sur le même réseau local ;
- consulter les performances de la machine qui héberge le serveur ;
- gérer certains fichiers CSV/XLSX.

Le backend utilise **Python + FastAPI** et l'interface est développée en **HTML/CSS/JavaScript**.

---

## Sommaire

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement](#lancement)
- [Première connexion](#première-connexion)
- [Accès depuis un autre appareil](#accès-depuis-un-autre-appareil)
- [Configuration](#configuration)
- [Structure du projet](#structure-du-projet)
- [Utilisation](#utilisation)
- [Partage de fichiers](#partage-de-fichiers)
- [Recherche](#recherche)
- [Performances](#performances)
- [Lancer HomeDrive automatiquement avec systemd](#lancer-homedrive-automatiquement-avec-systemd)
- [Mise à jour](#mise-à-jour)
- [Sauvegarde](#sauvegarde)
- [Désinstallation](#désinstallation)
- [Dépannage](#dépannage)
- [Sécurité](#sécurité)
- [Limitations connues](#limitations-connues)
- [Architecture](#architecture)
- [Commandes rapides](#commandes-rapides)
- [Licence](#licence)

---

# Prérequis

## Système

HomeDrive peut être installé sur une machine Linux disposant de Python 3.

Il est recommandé d'utiliser :

- Python **3.10 ou supérieur**
- pip
- `python3-venv`
- Git si vous souhaitez utiliser le script de mise à jour

Exemple sous Debian / Ubuntu :

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

Vérifier l'installation de Python :

```bash
python3 --version
```

Vérifier pip :

```bash
python3 -m pip --version
```

---

# Installation

## 1. Placer le projet

Décompressez le projet dans le dossier de votre choix.

Par exemple :

```bash
mkdir -p /opt
cd /opt
unzip source.zip
mv source home-drive
cd home-drive
```

Vous devez obtenir une structure similaire à :

```text
home-drive/
├── launch.py
├── launch.txt
├── requirements.txt
├── server/
├── web/
├── drive/
├── scripts/
└── systemd/
```

---

## 2. Rendre les scripts exécutables

Exécutez :

```bash
chmod +x scripts/*.sh
```

---

## 3. Installer les dépendances

HomeDrive fournit un script d'installation automatique :

```bash
./scripts/install.sh
```

Ce script permet notamment de :

1. vérifier que Python 3 est installé ;
2. créer l'environnement virtuel `.venv` ;
3. installer les dépendances Python ;
4. préparer les scripts nécessaires au lancement.

Les principales dépendances du projet comprennent notamment :

- FastAPI ;
- Uvicorn ;
- python-multipart ;
- psutil ;
- openpyxl.

---

# Lancement

Une fois l'installation terminée, lancez HomeDrive avec :

```bash
./scripts/start.sh
```

Le programme peut demander le port à utiliser :

```text
Port du serveur [8000] :
```

Appuyez sur `Entrée` pour utiliser le port par défaut :

```text
8000
```

Vous pouvez également utiliser un autre port, par exemple :

```text
8080
```

Lorsque le serveur démarre correctement, vous devriez obtenir une sortie similaire à :

```text
================================
        HomeDrive
================================
Serveur : http://0.0.0.0:8000
Téléphone (même Wi-Fi) : http://192.168.1.25:8000
Réseau : accessible sur le LAN
Arrêt : Ctrl+C
```

---

# Accéder à HomeDrive

## Depuis la machine qui héberge HomeDrive

Ouvrez un navigateur et rendez-vous sur :

```text
http://localhost:8000
```

Vous pouvez également utiliser :

```text
http://127.0.0.1:8000
```

---

## Depuis un autre ordinateur

Si l'autre ordinateur est connecté au même réseau local, utilisez l'adresse IP de la machine qui héberge HomeDrive.

Par exemple :

```text
http://192.168.1.25:8000
```

Remplacez `192.168.1.25` par l'adresse IP réelle du serveur.

---

# Première connexion

HomeDrive possède un système d'authentification.

Les identifiants initiaux sont configurés dans :

```text
server/config.py
```

Selon la configuration fournie avec le projet, les valeurs initiales peuvent être :

```text
Utilisateur : admin
Mot de passe : change-me
```

> **Important :** modifiez les identifiants par défaut avant d'utiliser HomeDrive sur un réseau auquel des personnes non autorisées peuvent accéder.

---

# Accès depuis un téléphone

HomeDrive peut être utilisé depuis un téléphone connecté au même réseau Wi-Fi que le serveur.

## 1. Connecter le téléphone au Wi-Fi

Le téléphone et la machine hébergeant HomeDrive doivent être connectés au même réseau local.

## 2. Lancer HomeDrive

Sur le serveur :

```bash
./scripts/start.sh
```

Le programme affiche normalement une adresse similaire à :

```text
Téléphone (même Wi-Fi) : http://192.168.1.25:8000
```

## 3. Ouvrir l'adresse

Sur le téléphone, ouvrez votre navigateur et saisissez :

```text
http://192.168.1.25:8000
```

Remplacez l'adresse IP par celle affichée par HomeDrive.

---

# Configuration

La configuration principale se trouve dans :

```text
server/config.py
```

Certains paramètres peuvent également être définis avec des variables d'environnement.

---

## Port du serveur

Le port par défaut est :

```text
8000
```

Pour utiliser le port `8080` :

```bash
export HOMEDRIVE_PORT=8080
./scripts/start.sh
```

HomeDrive sera alors accessible sur :

```text
http://localhost:8080
```

---

## Adresse d'écoute

Pour être accessible depuis le réseau local, le serveur doit généralement écouter sur :

```text
0.0.0.0
```

Pour limiter l'accès à la machine locale :

```bash
export HOMEDRIVE_HOST=127.0.0.1
./scripts/start.sh
```

Dans ce cas, les autres appareils du réseau ne pourront normalement pas accéder à HomeDrive.

---

## Répertoire de stockage

Les fichiers utilisateurs sont stockés dans :

```text
drive/
```

Vous pouvez définir un autre emplacement avec :

```bash
export HOMEDRIVE_PATH=/chemin/vers/mon-drive
```

Par exemple :

```bash
export HOMEDRIVE_PATH=/mnt/disque/home-drive
./scripts/start.sh
```

Cela permet notamment de stocker les fichiers sur un disque dédié.

---

## Utilisateur

Le nom d'utilisateur peut être configuré avec :

```bash
export HOMEDRIVE_USER=admin
```

Exemple :

```bash
export HOMEDRIVE_USER=mon-utilisateur
```

---

## Mot de passe

Le mot de passe peut être défini avec :

```bash
export HOMEDRIVE_PASSWORD="mon-mot-de-passe"
```

Exemple :

```bash
export HOMEDRIVE_PASSWORD="MotDePasseTresSolide"
./scripts/start.sh
```

Utilisez un mot de passe suffisamment long et difficile à deviner.

---

## Clé secrète

HomeDrive utilise également une clé secrète pour certains mécanismes d'authentification.

Elle peut être définie avec :

```bash
export HOMEDRIVE_SECRET="une-cle-secrete-longue-et-aleatoire"
```

Pour générer une clé aléatoire sous Linux :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copiez ensuite le résultat dans :

```bash
export HOMEDRIVE_SECRET="VOTRE_CLE_SECRETE"
```

---

# Structure du projet

La structure générale du projet est similaire à :

```text
home-drive/
│
├── launch.py
├── launch.txt
├── requirements.txt
│
├── server/
│   ├── main.py
│   ├── config.py
│   ├── homedrive_auth.sqlite3
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── files.py
│   │   ├── search.py
│   │   ├── shares.py
│   │   ├── spreadsheets.py
│   │   └── system.py
│   │
│   ├── security/
│   │   └── auth.py
│   │
│   └── services/
│       ├── file_service.py
│       └── system_service.py
│
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── drive/
│   ├── Documents/
│   ├── Images/
│   ├── Musique/
│   ├── Videos/
│   ├── Applications/
│   ├── Archives/
│   ├── Partages/
│   └── Corbeille/
│
├── scripts/
│   ├── install.sh
│   ├── start.sh
│   ├── update.sh
│   └── uninstall.sh
│
└── systemd/
    └── home-drive.service
```

---

# Organisation du Drive

HomeDrive utilise le dossier :

```text
drive/
```

pour stocker les fichiers.

Les dossiers principaux peuvent notamment être :

```text
drive/
├── Documents/
├── Images/
├── Musique/
├── Videos/
├── Applications/
├── Archives/
├── Partages/
└── Corbeille/
```

Ces dossiers permettent d'organiser les différents types de fichiers.

---

# Utilisation

## Importer un fichier

Pour importer un fichier :

1. ouvrez le dossier dans lequel vous souhaitez placer le fichier ;
2. cliquez sur **Importer** ;
3. sélectionnez le fichier ;
4. attendez la fin de l'importation.

Selon l'interface et la configuration, plusieurs fichiers peuvent être sélectionnés simultanément.

---

## Créer un dossier

Cliquez sur :

```text
+ Dossier
```

Entrez le nom souhaité puis validez.

---

## Créer un fichier texte

Cliquez sur :

```text
+ Fichier texte
```

Indiquez :

- le nom du fichier ;
- son contenu.

HomeDrive peut notamment être utilisé avec des fichiers texte tels que :

```text
.txt
.md
.json
.csv
.py
.html
.css
.js
```

---

## Télécharger un fichier

Sélectionnez le fichier souhaité puis utilisez l'action de téléchargement disponible dans l'interface.

Le navigateur téléchargera alors le fichier sur votre appareil.

---

## Copier un fichier

Sélectionnez un ou plusieurs fichiers puis utilisez l'action :

```text
Copier
```

Naviguez ensuite vers le dossier de destination et utilisez :

```text
Coller
```

---

## Déplacer un fichier

Sélectionnez le fichier puis utilisez :

```text
Couper
```

Naviguez vers le dossier de destination puis utilisez :

```text
Coller
```

---

## Supprimer un fichier

Sélectionnez le fichier puis utilisez l'action :

```text
Supprimer
```

Selon l'implémentation actuelle, le fichier peut être déplacé dans :

```text
drive/Corbeille/
```

plutôt que supprimé immédiatement.

---

# Partage de fichiers

HomeDrive possède une section permettant de partager certains fichiers avec d'autres utilisateurs.

Les permissions peuvent notamment être :

```text
Lecture
```

ou :

```text
Lecture et écriture
```

La permission **Lecture** permet à l'utilisateur d'accéder au fichier sans pouvoir le modifier.

La permission **Lecture et écriture** permet également d'effectuer des modifications lorsque cette fonctionnalité est autorisée par le backend.

> Les permissions doivent toujours être contrôlées côté serveur. Les restrictions affichées dans l'interface web ne doivent pas être considérées comme une protection suffisante à elles seules.

---

# Recherche

HomeDrive possède une fonction de recherche permettant de retrouver des fichiers dans le stockage.

La recherche est effectuée côté serveur.

Elle peut être utilisée pour retrouver rapidement des fichiers lorsque le Drive contient un grand nombre d'éléments.

---

# Performances

HomeDrive possède une section permettant de consulter les performances de la machine qui héberge le serveur.

Les informations peuvent notamment inclure :

- utilisation du processeur ;
- utilisation de la mémoire RAM ;
- utilisation du stockage ;
- vitesse de lecture ou d'écriture ;
- informations réseau ;
- temps de fonctionnement du serveur.

Les performances réseau dépendent notamment :

- de la connexion Ethernet ou Wi-Fi ;
- de la qualité du réseau ;
- de la charge du serveur ;
- du périphérique utilisé pour accéder au Drive.

---

# Lancer HomeDrive automatiquement avec systemd

Pour utiliser HomeDrive comme un service Linux permanent, un fichier systemd est fourni :

```text
systemd/home-drive.service
```

Cette méthode est particulièrement adaptée à un serveur ou à une machine qui doit lancer HomeDrive automatiquement au démarrage.

---

## Installation du service

Si HomeDrive est installé dans :

```text
/opt/home-drive
```

copiez le service :

```bash
sudo cp systemd/home-drive.service /etc/systemd/system/home-drive.service
```

Rechargez la configuration systemd :

```bash
sudo systemctl daemon-reload
```

Activez le démarrage automatique :

```bash
sudo systemctl enable home-drive
```

Démarrez HomeDrive :

```bash
sudo systemctl start home-drive
```

---

## Vérifier le statut

Utilisez :

```bash
sudo systemctl status home-drive
```

Si tout fonctionne correctement, le service doit apparaître comme actif.

---

## Consulter les logs

Pour afficher les logs en temps réel :

```bash
sudo journalctl -u home-drive -f
```

Pour afficher les derniers logs :

```bash
sudo journalctl -u home-drive --no-pager
```

---

## Arrêter HomeDrive

```bash
sudo systemctl stop home-drive
```

---

## Redémarrer HomeDrive

```bash
sudo systemctl restart home-drive
```

---

## Désactiver le démarrage automatique

```bash
sudo systemctl disable home-drive
```

---

# Mise à jour

HomeDrive fournit un script permettant de mettre à jour le projet :

```bash
./scripts/update.sh
```

Avant toute mise à jour, il est recommandé de sauvegarder les données importantes.

Les éléments particulièrement importants sont :

```text
drive/
```

et :

```text
server/homedrive_auth.sqlite3
```

Une fois la sauvegarde effectuée :

```bash
./scripts/update.sh
```

Si HomeDrive est lancé avec systemd :

```bash
sudo systemctl restart home-drive
```

---

# Sauvegarde

Les données utilisateur sont principalement stockées dans :

```text
drive/
```

La base SQLite utilisée par l'authentification se trouve dans :

```text
server/homedrive_auth.sqlite3
```

Il est donc recommandé de sauvegarder ces deux éléments.

---

## Sauvegarde simple

Vous pouvez créer une archive avec :

```bash
tar -czf homedrive-backup.tar.gz drive/ server/homedrive_auth.sqlite3
```

Vous pouvez ensuite déplacer cette archive vers un autre disque ou un autre serveur.

---

## Exemple de sauvegarde avec date

```bash
tar -czf "homedrive-backup-$(date +%Y-%m-%d).tar.gz" drive/ server/homedrive_auth.sqlite3
```

Cela produit par exemple :

```text
homedrive-backup-2026-09-19.tar.gz
```

---

# Désinstallation

Le projet fournit un script :

```bash
./scripts/uninstall.sh
```

Ce script peut notamment supprimer l'environnement virtuel Python créé pour HomeDrive.

Les données du dossier :

```text
drive/
```

doivent être sauvegardées avant toute suppression définitive du projet.

---

## Suppression du service systemd

Si vous avez installé HomeDrive avec systemd :

```bash
sudo systemctl stop home-drive
```

Puis :

```bash
sudo systemctl disable home-drive
```

Supprimez le fichier du service :

```bash
sudo rm /etc/systemd/system/home-drive.service
```

Rechargez systemd :

```bash
sudo systemctl daemon-reload
```

---

# Dépannage

## Le serveur ne démarre pas

Commencez par vérifier Python :

```bash
python3 --version
```

Puis vérifiez l'environnement virtuel :

```bash
ls -la .venv/
```

Si l'environnement virtuel n'existe pas, relancez :

```bash
./scripts/install.sh
```

Puis :

```bash
./scripts/start.sh
```

---

# Le port 8000 est déjà utilisé

Si le port `8000` est déjà utilisé par un autre programme, utilisez un autre port.

Par exemple :

```bash
export HOMEDRIVE_PORT=8080
./scripts/start.sh
```

Vous pourrez ensuite accéder à HomeDrive avec :

```text
http://localhost:8080
```

---

## Identifier le programme utilisant le port

Sous Linux :

```bash
sudo ss -ltnp | grep :8000
```

ou :

```bash
sudo lsof -i :8000
```

---

# Le téléphone ne peut pas se connecter

Vérifiez les points suivants :

1. le téléphone et le serveur sont connectés au même réseau ;
2. HomeDrive est démarré ;
3. HomeDrive écoute sur `0.0.0.0` ;
4. vous utilisez l'adresse IP du serveur et non `localhost` ;
5. le port est autorisé par le pare-feu.

Sur le serveur, vous pouvez vérifier les interfaces réseau avec :

```bash
ip addr
```

Vous pouvez également vérifier que le port est ouvert localement :

```bash
sudo ss -ltnp | grep :8000
```

---

# Vérifier que le serveur fonctionne

Depuis la machine qui héberge HomeDrive :

```bash
curl http://127.0.0.1:8000
```

Si le serveur fonctionne, une réponse HTTP doit être retournée.

Vous pouvez également tester :

```bash
curl -I http://127.0.0.1:8000
```

---

# Problème avec les dépendances Python

Si une dépendance manque, commencez par réinstaller les dépendances :

```bash
./scripts/install.sh
```

Vous pouvez également activer manuellement l'environnement virtuel :

```bash
source .venv/bin/activate
```

Puis :

```bash
pip install -r requirements.txt
```

---

# Problème avec systemd

Si le service ne démarre pas :

```bash
sudo systemctl status home-drive
```

Puis consultez les logs :

```bash
sudo journalctl -u home-drive -n 100 --no-pager
```

Cela permet généralement d'identifier l'erreur de démarrage.

---

# Sécurité

## Ne pas exposer directement HomeDrive sur Internet

La configuration standard de HomeDrive est principalement adaptée à un usage sur un réseau local.

Évitez d'exposer directement le port :

```text
8000
```

sur Internet sans mettre en place des protections supplémentaires.

Pour un accès distant, il est préférable d'utiliser une solution adaptée telle que :

- un VPN ;
- un reverse proxy ;
- HTTPS ;
- un pare-feu correctement configuré ;
- une authentification robuste.

---

## Modifier les identifiants par défaut

Ne conservez pas les identifiants de démonstration sur une installation utilisée réellement.

Par exemple :

```text
Utilisateur : admin
Mot de passe : change-me
```

Utilisez un compte et un mot de passe personnalisés.

---

## Utiliser une clé secrète unique

Définissez une clé secrète suffisamment longue :

```bash
export HOMEDRIVE_SECRET="VOTRE_CLE_SECRETE"
```

Ne partagez pas cette clé publiquement.

Ne la commitez pas dans Git.

---

# Git

Si vous utilisez Git pour développer HomeDrive, certains fichiers ne doivent généralement pas être versionnés.

Créez un fichier :

```text
.gitignore
```

avec par exemple :

```gitignore
# Environnement Python
.venv/

# Python
__pycache__/
*.py[cod]

# Base de données locale
server/homedrive_auth.sqlite3

# Logs
*.log

# Fichiers système
.DS_Store

# Données utilisateur
drive/*
!drive/.gitkeep
```

Vous pouvez ensuite créer un fichier vide :

```text
drive/.gitkeep
```

afin que Git conserve le dossier `drive/`.

---

# Fichiers à ne pas publier

Avant de publier HomeDrive sur GitHub ou sur une autre plateforme Git, vérifiez qu'aucune donnée privée n'est présente dans le dépôt.

Évitez notamment de publier :

```text
.venv/
```

```text
server/homedrive_auth.sqlite3
```

```text
drive/
```

ainsi que :

```text
*.log
```

et les éventuels fichiers contenant des mots de passe ou des clés secrètes.

---

# Limitations connues

## Partages

Certaines informations relatives aux partages peuvent actuellement être conservées en mémoire selon l'implémentation du backend.

Dans ce cas, elles peuvent être perdues après un redémarrage du serveur.

Une évolution possible serait de stocker les partages de manière persistante dans SQLite avec des informations telles que :

- identifiant du partage ;
- fichier associé ;
- propriétaire ;
- date de création ;
- date d'expiration ;
- permissions ;
- possibilité de révocation.

---

## Permissions

Les permissions doivent toujours être vérifiées côté backend.

Il ne faut jamais considérer les contrôles présents uniquement dans JavaScript comme une mesure de sécurité.

Un utilisateur pourrait autrement contourner l'interface et appeler directement les endpoints HTTP.

---

## Fichiers partagés

Lorsque les partages sont basés sur des chemins de fichiers, un déplacement ou un renommage peut rendre une référence obsolète.

Une amélioration possible serait d'utiliser un identifiant interne unique pour chaque fichier.

Par exemple :

```text
file_id
```

plutôt que de dépendre uniquement du chemin :

```text
/Documents/mon-fichier.txt
```

---

## Upload de gros fichiers

L'upload est conçu pour éviter certains problèmes liés au chargement de fichiers volumineux en mémoire.

Pour une utilisation avec des fichiers extrêmement volumineux, un système d'upload par morceaux avec reprise après interruption pourrait être ajouté.

---

## Recherche

La recherche parcourt actuellement les fichiers disponibles.

Pour un très grand nombre de fichiers, l'utilisation d'un index de recherche dédié pourrait améliorer les performances.

Une solution possible serait SQLite FTS5 ou un moteur de recherche spécialisé.

---

# Architecture

Le fonctionnement général de HomeDrive peut être représenté ainsi :

```text
                       Navigateur
                           │
                           │ HTTP
                           ▼
                    ┌─────────────┐
                    │   Uvicorn   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Auth API       Files API     Shares API
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Services  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Drive    │
                    │   fichiers  │
                    └─────────────┘
```

---

# Backend

Le backend est développé avec :

```text
Python
FastAPI
Uvicorn
```

Il fournit notamment des API pour :

- l'authentification ;
- la gestion des fichiers ;
- la recherche ;
- les partages ;
- les feuilles de calcul ;
- les informations système.

Les principaux fichiers se trouvent dans :

```text
server/api/
```

---

# Frontend

L'interface utilisateur est développée avec :

```text
HTML
CSS
JavaScript
```

Les principaux fichiers sont :

```text
web/index.html
web/app.js
web/styles.css
```

Le frontend communique avec le backend via HTTP.

---

# Stockage

Les fichiers utilisateurs sont stockés dans :

```text
drive/
```

La base SQLite utilisée pour l'authentification se trouve dans :

```text
server/homedrive_auth.sqlite3
```

---

# Commandes rapides

## Installation

```bash
chmod +x scripts/*.sh
./scripts/install.sh
```

---

## Démarrage

```bash
./scripts/start.sh
```

---

## Mise à jour

```bash
./scripts/update.sh
```

---

## Arrêt

Si HomeDrive est lancé directement dans un terminal :

```text
Ctrl+C
```

Si HomeDrive utilise systemd :

```bash
sudo systemctl stop home-drive
```

---

## Redémarrage avec systemd

```bash
sudo systemctl restart home-drive
```

---

## Voir le statut

```bash
sudo systemctl status home-drive
```

---

## Voir les logs

```bash
sudo journalctl -u home-drive -f
```

---

## Désinstallation

```bash
./scripts/uninstall.sh
```

---

# Installation rapide

Pour une installation classique sur Linux :

```bash
git clone <URL_DU_DEPOT> home-drive
cd home-drive

chmod +x scripts/*.sh

./scripts/install.sh

./scripts/start.sh
```

Puis ouvrez :

```text
http://localhost:8000
```

Pour accéder à HomeDrive depuis un autre appareil du réseau local, utilisez l'adresse IP du serveur :

```text
http://IP_DU_SERVEUR:8000
```

---

# Exemple de déploiement sur un serveur

Exemple d'installation dans `/opt/home-drive` :

```bash
sudo mkdir -p /opt
cd /opt

git clone <URL_DU_DEPOT> home-drive

cd home-drive

chmod +x scripts/*.sh

./scripts/install.sh
```

Configurez ensuite les paramètres nécessaires puis installez le service :

```bash
sudo cp systemd/home-drive.service /etc/systemd/system/home-drive.service

sudo systemctl daemon-reload
sudo systemctl enable home-drive
sudo systemctl start home-drive
```

Vérifiez :

```bash
sudo systemctl status home-drive
```

---

# Développement

Pour développer HomeDrive, clonez le projet puis installez les dépendances :

```bash
git clone <URL_DU_DEPOT> home-drive
cd home-drive

./scripts/install.sh
```

Activez ensuite l'environnement virtuel :

```bash
source .venv/bin/activate
```

Vous pouvez lancer le serveur avec :

```bash
./scripts/start.sh
```

Les modifications du frontend se trouvent principalement dans :

```text
web/
```

Les modifications du backend se trouvent principalement dans :

```text
server/
```

---

# Contribution

Les contributions sont les bienvenues.

Avant de proposer une modification :

1. créez une branche dédiée ;
2. effectuez vos modifications ;
3. testez HomeDrive ;
4. vérifiez qu'aucune donnée personnelle ou clé secrète n'est ajoutée ;
5. créez une Pull Request.

Exemple :

```bash
git checkout -b feature/ma-fonctionnalite
```

Puis :

```bash
git add .
git commit -m "Ajout de ma fonctionnalité"
git push origin feature/ma-fonctionnalite
```

---

# Licence

À compléter selon la licence choisie pour le projet.

Exemples :

```text
MIT
```

```text
Apache-2.0
```

```text
GPL-3.0
```

Si aucune licence n'est encore définie, il est recommandé d'en choisir une avant de publier le projet.

---

# Auteur

**HomeDrive**

Serveur de stockage personnel développé avec :

- Python
- FastAPI
- Uvicorn
- HTML
- CSS
- JavaScript
- SQLite

---
