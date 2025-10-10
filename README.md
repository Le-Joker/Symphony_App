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
- **Sounddevice** – Moteur audio pour la synthèse et les effets.  
- **NumPy** – Traitement du signal et calculs DSP.  
- **Kivy** – Interface graphique responsive et tactile.  
- **JSON** – Sauvegarde et chargement des séquences sonores.

---

## 🧩 Structure du projet

```
Symphony_App/
│
├── main.py                # Point d’entrée du projet
├── sound_engine.py        # Moteur sonore (Sounddevice)
├── ui_controller.py       # Interface graphique Kivy
├── presets.json           # Sauvegardes des sons et profils
├── requirements.txt
└── README.md
```

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

## 🔬 Technologies utilisées

| Outil | Rôle principal |
|-------|----------------|
| **Python 3.13** | Base du projet |
| **Sounddevice** | Synthèse et effets |
| **Kivy** | Interface visuelle |
| **NumPy** | Traitement du signal |
| **Pytest** | Tests unitaires |

---

## 🎹 Perspectives futures

- Ajout d’un module **d’improvisation algorithmique** (IA générative musicale).  
- Intégration d’un **contrôle MIDI externe**.  
- Exportation de compositions au format **.wav / .mp3**.  
- Éventuelle version mobile (Android via KivyMD).  

---

## ✍️ Auteurs

**Groupe d'étudiants de l’École Nationale Supérieure Polytechnique de Yaoundé**  
Projet : *Instrument numérique et symphonie algorithmique.*
