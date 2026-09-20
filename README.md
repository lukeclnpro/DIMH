DIMH

DIMH est un drive utilisable sous Linux qui permet d'exposer un PC comme un espace de stockage accessible depuis les autres appareils connectés au même réseau local.

Le service est accessible sur le port 8000 de l'adresse IP locale du PC.

Prérequis

Linux

Python

requirements.txt est inclus dans le code source

Installation

Clonez le dépôt puis lancez les commandes suivantes :

git clone https://github.com/lukeclnpro/DIMH
cd DIMH/source/

sudo ufw allow 8000/tcp
sudo ufw reload

chmod +x scripts/*.sh
./scripts/install.sh

./.venv/bin/python launch.py

Relancer le drive

Après un arrêt du programme, il n'est pas nécessaire de réinstaller le projet.

Depuis le dossier du projet :

cd DIMH/source/

./scripts/install.sh
./.venv/bin/python launch.py

Accès

Une fois le programme lancé, le drive est disponible sur le port 8000 et peut être utilisé par tous les appareils connectés au même réseau local que le PC.

Pour y accéder, utilisez l'adresse IP locale du PC suivie du port 8000 :

http://IP_DU_PC:8000


Par exemple :

http://192.168.1.42:8000

Résumé

DIMH permet donc de transformer simplement un PC Linux en drive accessible sur le réseau local, sans avoir besoin d'un service cloud externe.
