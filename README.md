# Projet API ROUTER

## 1. Introduction

Ce document décrit les spécifications fonctionnelles et techniques du projet **API ROUTER**, une application web conçue pour simplifier la publication, le routage dynamique et la visualisation d'APIs développées avec Node.js, en utilisant un backend **Python Django** pour une gestion optimisée des données et des services. L'objectif principal est de fournir une plateforme centralisée permettant aux utilisateurs de charger des fichiers `server.js` contenant des définitions d'API, de les rendre accessibles via des points d'accès personnalisables, et d'offrir une interface conviviale pour interagir avec ces APIs.

## 2. Objectifs du Projet

L'objectif général du projet API ROUTER est de faciliter le déploiement et la gestion d'APIs Node.js en utilisant un backend Python Django, en offrant les fonctionnalités suivantes :

*   **Centralisation**: Regrouper et gérer plusieurs APIs Node.js au sein d'une seule application.
*   **Déploiement simplifié**: Éliminer la nécessité d'attribuer un nouveau port à chaque API, en utilisant un système de routage dynamique.
*   **Accès personnalisable**: Permettre la définition de points d'accès thématiques (ex: `/math`, `/phy`) pour les groupes d'APIs.
*   **Visualisation et Interaction**: Fournir une interface graphique pour explorer les APIs chargées, visualiser leurs données et comprendre leur utilisation.
*   **Autonomie**: Gérer les dépendances locales des APIs (fichiers, bases de données SQLite) pour un fonctionnement autonome.

## 3. Architecture Technique

Le projet API ROUTER adoptera une architecture client-serveur moderne, composée des éléments suivants :

*   **Frontend**: Développé en **ReactJS**, offrant une interface utilisateur interactive et réactive.
*   **Backend**: Développé en **Python Django**, servant de cœur à l'application pour la gestion des APIs, le routage, la persistance des données et la communication avec le frontend.

## 4. Fonctionnalités Détaillées

### 4.1. Gestion des APIs

*   **Chargement Dynamique des Fichiers `server.js`**:
    *   L'application devra permettre à l'utilisateur de télécharger un ou plusieurs fichiers `server.js`.
    *   Chaque fichier `server.js` sera traité comme une entité API distincte.
    *   L'application devra détecter et charger les routes Express.js définies dans ces fichiers.
*   **Prise en Charge des Dossiers de Contenu et Dépendances Locales**:
    *   Lors du chargement d'un fichier `server.js`, l'application devra identifier et gérer l'ensemble du répertoire parent de ce fichier, ainsi que tous les sous-répertoires et fichiers associés.
    *   Ceci est crucial pour les APIs qui dépendent de ressources locales telles que des fichiers de configuration, des fichiers statiques (images, CSS, JS), ou des bases de données embarquées comme **SQLite**.
    *   L'application s'assurera que ces ressources sont correctement accessibles par l'API chargée dans son environnement d'exécution isolé, simulant ainsi un environnement de travail complet pour chaque API.
*   **Routage Dynamique et Personnalisable**:
    *   Pour chaque `server.js` chargé, l'utilisateur pourra définir un préfixe d'URL (ex: `math`, `phy`).
    *   Les APIs de ce `server.js` seront alors accessibles via `ip:port/prefixe_defini/route_api_originale` (ex: `ip:port/math/api/calcul`).
    *   L'application devra gérer la redirection et le proxy des requêtes vers les instances internes des APIs chargées.
*   **Isolation et Conteneurisation des APIs**:
    *   Chaque API chargée à partir d'un `server.js` sera exécutée dans un environnement **isolé et conteneurisé**.
    *   Cette isolation garantira l'absence de conflits de ports, de variables d'environnement ou de dépendances entre les différentes APIs.
    *   Le backend gérera l'exécution de ces serveurs Node.js de manière sécurisée et efficace, en s'assurant que chaque API a accès à son propre système de fichiers virtuel ou à des liens symboliques vers ses ressources locales (y compris les bases de données SQLite) sans interférer avec les autres.

### 4.2. Interface Utilisateur (Frontend ReactJS)

L'interface graphique sera moderne, intuitive et conviviale, offrant les fonctionnalités suivantes :

*   **Tableau de Bord des APIs**:
    *   Liste de tous les fichiers `server.js` chargés, avec leur statut (actif/inactif), leur préfixe d'accès et leur port interne.
    *   Options pour activer, désactiver ou supprimer une API.
*   **Visualisation des APIs**:
    *   Pour chaque API chargée, une vue détaillée affichant toutes les routes disponibles (GET, POST, PUT, DELETE, etc.).
    *   Affichage des paramètres attendus pour chaque route (corps de requête, paramètres d'URL, en-têtes).
    *   **Visualisation des Données**: Possibilité de visualiser les données retournées par les endpoints des APIs via des tableaux interactifs (si le format de réponse est JSON ou similaire).
*   **Génération de Code d'Appel**:
    *   Pour chaque endpoint d'API, l'interface devra générer des exemples de code (ex: JavaScript `fetch`, `axios`, `curl`) montrant comment interroger l'API, en fonction de ses paramètres et de son contenu.
*   **Gestion des Fichiers**:
    *   Interface pour télécharger de nouveaux fichiers `server.js`.
    *   Possibilité de lier un dossier de contenu à un fichier `server.js`.
*   **Indicateurs de Santé**:
    *   Affichage de l'état de chaque API (en ligne, hors ligne, erreurs de chargement).
    *   Journalisation des requêtes et réponses pour le débogage.

### 4.3. Backend (Python Django)

Le backend, basé sur Python Django, sera responsable de la logique métier, de la persistance des données et de la gestion des APIs. Il orchestrera le chargement, l'exécution et le routage des APIs Node.js externes.

*   **Moteur de Chargement et d'Exécution des APIs Node.js**:
    *   Un module Django sera responsable de la gestion du cycle de vie des APIs Node.js externes.
    *   Il devra être capable de lire, interpréter et exécuter des fichiers `server.js` Node.js.
    *   Chaque `server.js` sera exécuté dans un processus enfant ou un conteneur isolé (par exemple, via des conteneurs Docker légers ou des processus isolés) pour éviter les interférences et garantir la stabilité du système.
*   **Gestion des Ports**:
    *   Attribution dynamique de ports internes pour chaque API chargée.
    *   Proxy des requêtes externes (via le préfixe défini) vers le port interne de l'API correspondante.
*   **Analyse de `server.js` et Découverte d'API**:
    *   Le backend Django devra intégrer un mécanisme capable d'analyser le code JavaScript des fichiers `server.js` pour en extraire les informations pertinentes : routes Express.js, méthodes HTTP (GET, POST, PUT, DELETE), chemins d'accès, et paramètres attendus.
    *   Il devra également identifier les middlewares spécifiques (comme `multer` pour la gestion des uploads de fichiers) et les dépendances (comme `sqlite3` pour les bases de données locales) afin de configurer correctement l'environnement d'exécution de chaque API Node.js.
*   **Gestion des Erreurs et Logs**:
    *   Capture et affichage des erreurs survenant lors du chargement ou de l'exécution des APIs.
    *   Journalisation des activités du serveur et des APIs.
*   **Sécurité**:
    *   Gestion des CORS pour permettre l'accès depuis le frontend.
    *   Implémentation d'une authentification admin pour la gestion de l'application API ROUTER elle-même (comme vu dans le `server.js` fourni).

## 5. Exigences Techniques Spécifiques

*   **Environnement d'Exécution**: Python 3.x pour le backend principal, Node.js pour l'exécution des APIs chargées.
*   **Framework Backend**: **Django** (pour le cœur de l'application, la gestion des données, l'authentification et le routage principal) et potentiellement **Django REST Framework** pour la création d'endpoints API robustes pour le frontend ReactJS.
*   **Framework Frontend**: ReactJS.
*   **Base de Données**: Prise en charge native des bases de données **SQLite** pour les APIs chargées. L'application devra s'assurer que chaque API peut interagir avec sa propre instance de base de données SQLite ou un fichier de base de données spécifique, sans interférence avec d'autres APIs ou la base de données interne d'API ROUTER.
*   **Gestion des Fichiers**: Utilisation de `multer` pour la gestion des uploads de fichiers (comme observé dans le `server.js` fourni).
*   **Variables d'Environnement**: Support du fichier `.env` pour la configuration (comme observé dans le `server.js` fourni).
*   **HTTPS**: Capacité à gérer le HTTPS, y compris la génération de certificats auto-signés si nécessaire (comme observé dans le `server.js` fourni).
*   **Design**: L'interface devra avoir un design moderne et épuré, adapté à un outil de support API.

## 6. Phases de Test

Une fois le développement terminé, les phases de test suivantes devront être menées :

*   **Test de Chargement d'API**: Vérifier que des fichiers `server.js` variés peuvent être chargés et démarrés correctement.
*   **Test de Routage Dynamique**: S'assurer que les APIs sont accessibles via les préfixes d'URL définis par l'utilisateur (ex: `/math`, `/phy`).
*   **Test d'Accès aux APIs**: Effectuer des requêtes (GET, POST, PUT, DELETE) vers les APIs chargées et vérifier les réponses.
*   **Test de Visualisation Frontend**: Valider que l'interface affiche correctement les routes, les paramètres et les données des APIs.
*   **Test de Génération de Code**: Vérifier que les exemples de code d'appel d'API sont corrects et fonctionnels.
*   **Test de Gestion des Fichiers/Dossiers**: S'assurer que les APIs peuvent accéder à leurs fichiers locaux et bases de données SQLite.
*   **Test de Robustesse**: Vérifier le comportement de l'application en cas d'erreurs dans les `server.js` chargés ou de requêtes malformées.

## 7. Nom de l'Application

Le nom de l'application sera **API ROUTER**.

## 8. Conclusion

API ROUTER sera un outil puissant pour les développeurs souhaitant gérer et déployer leurs APIs Node.js de manière flexible et intuitive, avec une interface moderne et des fonctionnalités de visualisation avancées, le tout propulsé par un backend Python Django robuste et performant.
