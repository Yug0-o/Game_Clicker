# Clicker Game - Multi-Cibles

## Architecture Moderne : Python Backend + JavaScript Frontend

### Structure du projet

```
clicker_game/
├── backend.py          # Serveur Flask (API REST)
├── index.html          # Interface HTML
├── styles.css          # Design moderne et élégant
├── script.js           # Logique frontend
├── requirements.txt    # Dépendances Python
└── README.md          # Ce fichier
```

---

## Installation et Démarrage

### 1. Installer les dépendances Python

```bash
pip install flask flask-cors
```

Ou avec le fichier requirements.txt :

```bash
pip install -r requirements.txt
```

### 2. Lancer le serveur backend

```bash
python backend.py
```

Le serveur API démarre sur `http://localhost:5000`

### 3. Ouvrir le jeu

Ouvrez simplement le fichier `index.html` dans votre navigateur web.

**Alternative** : Si vous avez Python installé, vous pouvez aussi lancer un serveur HTTP local :

```bash
# Dans un autre terminal, dans le même dossier
python -m http.server 8000
```

Puis ouvrez : `http://localhost:8000`

---

## Fonctionnalités

### Interface Moderne

- Design élégant avec dégradés et effets de verre
- Animations fluides et réactives
- Responsive (fonctionne sur mobile)
- Notifications toast

### Gameplay

- **Cibles illimitées** : Débloquez autant de cibles que vous voulez
- **Améliorations par cible** : Chaque cible a ses propres upgrades
- **Auto-clicker** : Génération automatique de points
- **Système de progression** : Les nouvelles cibles rapportent plus de points

### Sauvegarde

- Sauvegarde automatique en JSON
- Chargement de partie
- Persistance des données

---

## Architecture Technique

### Backend (Python + Flask)

- **API REST** pour toutes les opérations du jeu
- **Logique métier** : calculs, améliorations, auto-clicker
- **Sauvegarde** : système de persistance en JSON

### Frontend (HTML + CSS + JavaScript)

- **Interface moderne** : Design glassmorphism et gradients
- **Communication async** : Fetch API pour dialoguer avec le backend
- **Mise à jour temps réel** : Polling toutes les 100ms
- **Animations** : CSS transitions et keyframes

### Endpoints API

```
GET  /api/game                      # Récupère l'état du jeu
POST /api/clic/<cible_id>          # Effectue un clic
POST /api/select/<cible_id>        # Sélectionne une cible
POST /api/amelioration/acheter     # Achète une amélioration
POST /api/save                     # Sauvegarde la partie
POST /api/load                     # Charge la partie
```

---

## Personnalisation

### Ajouter une nouvelle amélioration

Éditez `backend.py` et ajoutez votre classe :

```python
class VotreAmelioration(Amelioration):
    def __init__(self):
        super().__init__(
            nom="Nom de l'amélioration",
            description="Description",
            prix_base=100,
            pour_cible=True  # True = par cible, False = globale
        )

    def appliquer(self, game, cible_id):
        # Votre logique ici
        pass
```

Puis ajoutez-la dans `initialiser_ameliorations()` :

```python
def initialiser_ameliorations(self):
    return [
        AmeliorationClicPuissance(),
        AmeliorationClicMultiplicateur(),
        VotreAmelioration(),  # <-- Ajoutez ici
        # ...
    ]
```

### Modifier le design

Éditez `styles.css` pour changer :

- Les couleurs (gradients)
- Les animations
- La disposition des éléments
- Les effets visuels

---

## Dépannage

### Le frontend ne se connecte pas au backend

Vérifiez que :

1. Le backend est bien lancé (`python backend.py`)
2. L'URL dans `script.js` est correcte (`http://localhost:5000`)
3. CORS est activé (déjà configuré dans le code)

### Erreur "Connection refused"

Le serveur Flask n'est pas démarré. Lancez `python backend.py`.

### Les données ne se sauvent pas

Vérifiez que le fichier `save.json` peut être créé dans le dossier du backend.

---

## Notes Techniques

- **Polling vs WebSocket** : Le jeu utilise du polling simple (100ms). Pour une version plus avancée, vous pourriez utiliser WebSocket.
- **Sécurité** : Cette version est pour usage local uniquement. Pour un déploiement en production, ajoutez de l'authentification et de la validation.
- **Performance** : L'update à 100ms est un bon compromis. Ajustez selon vos besoins.

---

## Améliorations Futures

- [ ] WebSocket pour les mises à jour en temps réel
- [ ] Système de succès/achievements
- [ ] Leaderboard global
- [ ] Mode multijoueur
- [ ] Sons et musique
- [ ] Thèmes personnalisables

---

## Licence

Ce projet est libre d'utilisation et de modification. Amusez-vous bien ! 🎮
