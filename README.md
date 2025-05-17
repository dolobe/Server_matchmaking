
# Matchmaking Project - Morpion (Tic Tac Toe) en Réseau

## Objectif

Ce projet propose une plateforme de **matchmaking** pour jouer au jeu du morpion (Tic Tac Toe) en ligne, avec :
- Un serveur Django (API REST + WebSocket via Channels)
- Un client logiciel multiplateforme en Python/Tkinter
- Une base de données MySQL pour la gestion des utilisateurs, parties, statistiques

Le but est de permettre à plusieurs joueurs de s’inscrire, se connecter, rejoindre une file d’attente, être appariés automatiquement, jouer en temps réel, et consulter leurs statistiques.

---

## Fonctionnalités

- **Inscription et connexion** sécurisées (API REST)
- **Matchmaking automatique** : file d’attente, appariement 1v1
- **Jeu du morpion** en temps réel (WebSocket)
- **Gestion stricte des tours** (un coup par joueur à chaque tour)
- **Affichage des scores et statistiques** (parties jouées, victoires, défaites, égalités)
- **Dashboard admin** (visualisation des files, matchs, logs)
- **Logs** détaillés côté client et serveur

---

## Architecture
####   matchmaking-project/
####    │
####    ├── matchmaking_server/ # Code Django (API, WebSocket, modèles, admin)
####    │   ├── manage.py
####    │   ├── web_django/
###    │   └── matchmaking/
###    │
####    └── matchmaking_client_tk/
####        ├── main.py
####        ├── auth.py
####        ├── morpion.py
####        └── stats.py


---

## Prérequis

- **Python 3.10+**
- **MariaDB, Port : 3307**
- **pip** (gestionnaire de paquets Python)

---

## Installation

###  Cloner le dépôt :


## Lancement du serveur
daphne -p 8080 web_django.asgi:application

