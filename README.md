# 🎶 Projet d’Instrument Numérique – Symphonie Interactive

Un projet d’art numérique alliant musique, code et interactivité.  
Ce système crée un instrument numérique capable de générer, moduler et visualiser des sons en temps réel, transformant la machine en véritable instrument de création sonore.

---

## 🌌 Vision du projet

Cet instrument est pensé comme une **symphonie algorithmique**, où les oscillateurs remplacent les cordes et les filtres deviennent des souffles.  
L’utilisateur ne joue plus seulement de la musique : il **dialogue avec le son**, en explorant ses textures et résonances à travers une interface vivante créée avec **Kivy**.

---

## ⚙️ Architecture du système

- **Python** – Langage principal pour la logique et le traitement.  
- **Pydub** – Moteur audio pour la synthèse et les effets.  
- **NumPy** – Traitement du signal et calculs DSP.  
- **PyQt5** – Interface graphique responsive et tactile.  
- **QtSql** – Sauvegarde et chargement des séquences sonores.

---

## 🧠 Installation

Crée un environnement virtuel :

```bash
python -m venv env
source env/bin/activate     # Linux/Mac
pip install -r requirements.txt      # Windows
```

Installe les dépendances :

```bash
pip install -r requirements.txt
```

---

## 🚀 Exécution

Lance le projet depuis la racine :

```bash
python main.py
```

---

## 🎶 Symphony_App — Application musicale complète (Vue d'ensemble)

Ce dépôt contient une application Python destinée à être une application musicale complète :
- gestion des comptes via une base SQLite (création, connexion, suppression, sauvegarde),
- lecture/arrêt/relecture de morceaux au sein de l'application,
- enregistrement (record) du son produit, sauvegarde locale et possibilité de télécharger/exporter les enregistrements sur le système de l'utilisateur.

La version actuelle contient des composants de démonstration (interface PyQt, moteur son) — ce README décrit la structure attendue, les fonctionnalités implémentées ou à implémenter, et les dépendances nécessaires.

---

## 📂 Structure du projet (état attendu)

```
Symphony_App/
│
├── main.py                 # Point d’entrée (UI PyQt + initialisation DB)
├── sound_engine.py         # Logiciel de synthèse/gestion audio (enregistre/play/save)
├── ui_controller.py       # Contrôleurs de l'interface (PyQt widgets)
├── presets.json            # Presets d'instruments / configurations
├── requirements.txt        # Dépendances Python
├── recordings/             # (suggestion) dossier où sont sauvegardés les enregistrements (.wav/.mp3)
├── data/                   # (suggestion) contient la DB sqlite: sportsdatabase.db
└── README.md
```

Remarque : certains dossiers comme `recordings/` ou `data/` peuvent être créés automatiquement par l'application lors du premier enregistrement.

---

## ✅ Fonctionnalités souhaitées et contrat minimal

Contract (inputs/outputs) — bref :
- Input: actions utilisateur via l'UI (créer compte, se connecter, supprimer compte, jouer son, enregistrer, télécharger, rejouer).
- Output: mises à jour visuelles, fichiers audio sur disque (.wav/.mp3), enregistrements persistés en base de données (métadonnées), fichiers DB SQLite.

Comportements attendus (user flows) :
- Inscription (create account) : fournir `username` + `password` -> stocker en DB (hash du mot de passe), renvoyer confirmation.
- Connexion (login) : username/password -> vérifier et ouvrir session.
- Suppression de compte (delete) : confirmation + suppression des enregistrements liés (optionnel).
- Enregistrer une session audio (record) : bouton Start/Stop -> sauvegarde en .wav dans `recordings/` et enregistrement d'une ligne métadonnée en DB.
- Télécharger / Exporter : depuis la liste d'enregistrements, bouton pour ouvrir l'emplacement sur le disque ou copier le fichier vers une destination choisie par l'utilisateur.
- Rejouer dans l'app : sélectionner un fichier dans la liste -> bouton Play/Stop.

---

## 🧾 Schéma de la base de données (SQLite via QtSql)

Tables principales (proposition) :

- accounts
	- id INTEGER PRIMARY KEY AUTOINCREMENT
	- username TEXT UNIQUE NOT NULL
	- password_hash TEXT NOT NULL
	- created_at TEXT

- recordings
	- id INTEGER PRIMARY KEY AUTOINCREMENT
	- account_id INTEGER REFERENCES accounts(id)
	- filename TEXT NOT NULL    -- chemin relatif dans recordings/
	- length_seconds REAL
	- created_at TEXT

Le code présent utilise une table `sportsmen` (exemple) — conservez-la si utile. L'application réelle doit ajouter les tables `accounts` et `recordings` décrites ci-dessus.

Sécurité : stocker uniquement un hash (bcrypt / argon2) pour les mots de passe. Ne jamais sauvegarder de mots de passe en clair.

---

## 🛠️ Lancer l'application (Windows)

1) Créez et activez l'environnement virtuel (cmd.exe) :

```bash
python -m venv env
env\\Scripts\\activate
```

2) Installez les dépendances comme indiqué ci-dessus.

3) Lancez l'application :

```bash
python main.py
```

La fenêtre principale devrait :
- initialiser / afficher la base de données (création si nécessaire),
- proposer un écran d'authentification (créer / login / delete),
- proposer une section pour jouer/stopper/record/visualiser les enregistrements.