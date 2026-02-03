# Clicker Game - Multi-Cibles

Un jeu de clicker modulable et extensible avec système de cibles illimitées, développé en Python avec Tkinter.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Table des matières

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Comment jouer](#-comment-jouer)
- [Architecture du code](#-architecture-du-code)
- [Ajouter vos propres améliorations](#-ajouter-vos-propres-améliorations)
- [Système de sauvegarde](#-système-de-sauvegarde)
- [Exemples d'améliorations personnalisées](#-exemples-daméliorations-personnalisées)
- [Contribuer](#-contribuer)

---

## Présentation

**Clicker Game - Multi-Cibles** est un jeu idle/clicker où vous pouvez :

- Cliquer sur des cibles pour gagner des points
- Acheter des améliorations pour augmenter vos gains
- Débloquer de nouvelles cibles illimitées
- Chaque cible rapporte plus de points que la précédente
- Automatiser votre progression avec des auto-clickers

Le jeu est conçu pour être **extrêmement modulable** : n'importe qui peut facilement ajouter ses propres améliorations en quelques lignes de code !

---

## Fonctionnalités

### Système de cibles illimitées

- Démarrez avec une cible de base
- Débloquez autant de cibles que vous voulez
- Chaque nouvelle cible rapporte **progressivement plus** de points
  - Cible 1 : 1 point/clic
  - Cible 2 : ~2.8 points/clic
  - Cible 3 : ~5.2 points/clic
  - Formule : `points = 1 * (numero_cible ^ 1.5)`

### Améliorations contextuelles

- **Améliorations par cible** : chaque cible a ses propres upgrades
- **Améliorations globales** : affectent tout le jeu
- Interface qui affiche uniquement les améliorations pertinentes
- Système de niveaux avec prix progressifs

### Auto-clicker

- Système d'auto-clics par cible
- Amélioration de la vitesse globale des auto-clics
- Délai réglable (minimum 0.3s)

### Sauvegarde / Chargement

- Sauvegarde automatique en JSON
- Restauration complète de la progression
- Préservation de tous les niveaux d'améliorations

### Interface moderne

- Design sombre et coloré
- Chaque cible a sa propre couleur
- Défilement horizontal pour cibles et améliorations
- Animations visuelles lors des achats
- Stats en temps réel

---

## Installation

### Prérequis

- Python 3.7 ou supérieur
- Tkinter (inclus par défaut avec Python)

### Installation simple

1. **Téléchargez le fichier**

   ```bash
   # Téléchargez clicker_game.py
   ```

2. **Lancez le jeu**
   ```bash
   python clicker_game.py
   ```

C'est tout ! Aucune dépendance externe nécessaire.

---

## Comment jouer

### Démarrage

1. Lancez le jeu avec `python clicker_game_v2.py`
2. Vous commencez avec **1 cible** et **0 points**

### Gameplay de base

1. **Cliquez sur "CLIC !"** pour gagner des points
2. **Sélectionnez une cible** avec "Voir améliorations"
3. **Achetez des améliorations** dans la boutique en bas
4. **Débloquez de nouvelles cibles** avec l'amélioration "Nouvelle Cible"

### Stratégie recommandée

1. Achetez quelques **"Clic Puissant"** pour augmenter vos gains
2. Investissez dans des **"Auto-Clicker"** pour automatiser
3. Améliorez la **"Vitesse Auto"** pour accélérer les gains passifs
4. Débloquez une **nouvelle cible** quand vous avez assez de points
5. Répétez avec chaque nouvelle cible !

### Contrôles

- **Clic gauche** : Cliquer sur les cibles
- **Bouton "Voir améliorations"** : Sélectionner une cible
- **Boutons de la boutique** : Acheter des améliorations
- **Sauvegarder** : Enregistrer votre progression
- **Charger** : Restaurer une partie sauvegardée

---

## Architecture du code

Le code est organisé en **4 sections principales** :

### 1. Système de Cibles (`class Cible`)

Représente une cible cliquable avec :

- Points par clic
- Auto-clics
- Statistiques (clics totaux, points gagnés)
- Couleur unique

### 2. Système d'Améliorations (`class Amelioration`)

Classe de base pour toutes les améliorations :

- `pour_cible` : True = amélioration par cible, False = globale
- `get_prix()` : Calcule le prix selon le niveau
- `acheter()` : Gère l'achat
- `appliquer()` : Applique l'effet (à implémenter dans les sous-classes)

### 3. Moteur du jeu (`class ClickerGame`)

Gère la logique du jeu :

- Points et statistiques
- Gestion des cibles
- Auto-clicker
- Sauvegarde/Chargement

### 4. Interface graphique (`class ClickerUI`)

Interface Tkinter :

- Affichage des cibles (horizontal)
- Boutique d'améliorations (horizontal)
- Animations et feedbacks visuels

---

## Ajouter vos propres améliorations

C'est **super facile** ! Voici comment faire :

### Étape 1 : Créer votre classe d'amélioration

```python
class VotreAmelioration(Amelioration):
    """Description de votre amélioration"""

    def __init__(self):
        super().__init__(
            nom="Nom de votre amélioration",
            description="Ce que fait votre amélioration",
            prix_base=100,                    # Prix de départ
            multiplicateur_prix=1.15,         # Augmentation du prix (15% par défaut)
            pour_cible=True                   # True = par cible, False = globale
        )

    def appliquer(self, game, cible_id):
        """Votre logique ici !"""
        if cible_id and cible_id in game.cibles:
            # Modifier la cible
            game.cibles[cible_id].points_par_clic += 10
        # Ou modifier le jeu globalement
        # game.delai_auto_clic -= 0.5
```

### Étape 2 : Ajouter à la liste

Dans la méthode `initialiser_ameliorations()` de `ClickerGame` :

```python
def initialiser_ameliorations(self) -> List[Amelioration]:
    return [
        AmeliorationClicPuissance(),
        AmeliorationClicMultiplicateur(),
        AmeliorationAutoClicker(),
        AmeliorationVitesseAuto(),
        AmeliorationNouvelleCible(),
        VotreAmelioration(),           # ← Ajoutez la vôtre ici !
    ]
```

C'est tout ! Votre amélioration apparaîtra automatiquement dans la boutique.

---

## Système de sauvegarde

### Fichier de sauvegarde

- Nom : `save.json`
- Format : JSON lisible
- Emplacement : même dossier que le script

### Contenu sauvegardé

Points totaux  
Toutes les cibles et leurs stats  
Niveaux de toutes les améliorations  
Vitesse de l'auto-clicker  
Cible actuellement sélectionnée

### Utilisation

```python
# Sauvegarder
game.sauvegarder()  # ou cliquez sur "Sauvegarder"

# Charger
game.charger()      # ou cliquez sur "Charger"
```

---

## Exemples d'améliorations personnalisées

### Amélioration : Triple Clic

```python
class AmeliorationTripleClic(Amelioration):
    """Triple les points par clic"""

    def __init__(self):
        super().__init__(
            nom="Triple Clic",
            description="Points par clic x3",
            prix_base=300,
            multiplicateur_prix=1.8,
            pour_cible=True
        )

    def appliquer(self, game, cible_id):
        if cible_id and cible_id in game.cibles:
            game.cibles[cible_id].points_par_clic *= 3
```

### Amélioration : Bonus de points

```python
class AmeliorationBonusPoints(Amelioration):
    """Donne des points immédiatement"""

    def __init__(self):
        super().__init__(
            nom="Bonus Points",
            description="+1000 points instantanés",
            prix_base=500,
            multiplicateur_prix=2.0,
            pour_cible=False  # Amélioration globale
        )

    def appliquer(self, game, cible_id):
        game.points += 1000
```

### Amélioration : Super Auto-clicker

```python
class AmeliorationSuperAuto(Amelioration):
    """Ajoute 5 auto-clics d'un coup"""

    def __init__(self):
        super().__init__(
            nom="Super Auto",
            description="+5 auto-clics",
            prix_base=1000,
            multiplicateur_prix=1.5,
            pour_cible=True
        )

    def appliquer(self, game, cible_id):
        if cible_id and cible_id in game.cibles:
            game.cibles[cible_id].auto_clics_par_tick += 5
```

### Amélioration : Boost toutes les cibles

```python
class AmeliorationBoostGlobal(Amelioration):
    """Améliore TOUTES les cibles en même temps"""

    def __init__(self):
        super().__init__(
            nom="Boost Global",
            description="+10 points/clic pour TOUTES les cibles",
            prix_base=2000,
            multiplicateur_prix=2.0,
            pour_cible=False
        )

    def appliquer(self, game, cible_id):
        # Améliorer toutes les cibles existantes
        for cible in game.cibles.values():
            cible.points_par_clic += 10
```

---

## Formules et équilibrage

### Prix des améliorations

```
Prix = prix_base × multiplicateur_cible × (multiplicateur_prix ^ niveau)
```

Où :

- `prix_base` : Prix initial de l'amélioration
- `multiplicateur_cible` : `1.0` pour globales, `√numero_cible` pour cibles spécifiques
- `multiplicateur_prix` : Facteur d'augmentation (1.15 = +15% par niveau)
- `niveau` : Nombre de fois que l'amélioration a été achetée

### Points par clic des cibles

```
Points = 1 × (numero_cible ^ 1.5)
```

Exemples :

- Cible 1 : 1 point
- Cible 2 : 2.8 points
- Cible 3 : 5.2 points
- Cible 4 : 8 points
- Cible 5 : 11.2 points

### Prix des nouvelles cibles

```
Prix = 500 × (2 ^ (numero_cible - 1))
```

Exemples :

- Cible 2 : 500 points
- Cible 3 : 1000 points
- Cible 4 : 2000 points
- Cible 5 : 4000 points

---

## Améliorations prédéfinies

| Amélioration      | Type      | Prix de base | Effet                       |
| ----------------- | --------- | ------------ | --------------------------- |
| Clic Puissant     | Par cible | 10           | +1 point par clic           |
| Multiplicateur x2 | Par cible | 100          | Double les points par clic  |
| Auto-Clicker      | Par cible | 50           | +1 clic automatique         |
| Vitesse Auto      | Globale   | 200          | Réduit le délai de 0.3s     |
| Nouvelle Cible    | Globale   | 500+         | Débloque une nouvelle cible |

---

## Dépannage

### Le jeu ne démarre pas

- Vérifiez que Python 3.7+ est installé : `python --version`
- Vérifiez que Tkinter est installé : `python -m tkinter`

### Les améliorations ne s'affichent pas

- Assurez-vous d'avoir sélectionné une cible avec "Voir améliorations"
- Les améliorations globales apparaissent toujours en dernier

### La sauvegarde ne fonctionne pas

- Vérifiez que vous avez les droits d'écriture dans le dossier
- Le fichier `save_v2.json` doit être accessible

### L'interface est trop petite/grande

- Modifiez la taille dans `ClickerUI.__init__()` :
  ```python
  self.root.geometry("1000x700")  # Changez ces valeurs
  ```

---

## Idées d'améliorations futures

Voici quelques idées pour étendre le jeu :

### Gameplay

- [ ] Système de prestige (reset avec bonus permanents)
- [ ] Achievements/succès
- [ ] Événements aléatoires (bonus temporaires)
- [ ] Mini-jeux pour gagner des bonus
- [ ] Multiplicateurs temporaires

### Améliorations

- [ ] Synergies entre cibles
- [ ] Améliorations qui débloquent d'autres améliorations
- [ ] Système de compétences/talents
- [ ] Modes de jeu alternatifs

### Technique

- [ ] Mode sombre/clair
- [ ] Sons et musique
- [ ] Graphiques et animations plus poussés
- [ ] Multijoueur/classement en ligne
- [ ] Version web (conversion vers JavaScript)

---

## Structure des fichiers

```
clicker-game/
│
├── clicker_game.py      # Fichier principal du jeu
├── save.json            # Fichier de sauvegarde (créé automatiquement)
└── README.md            # Ce fichier
```

---

## Contribuer

Les contributions sont les bienvenues ! Voici comment participer :

1. **Forkez le projet**
2. **Créez une branche** pour votre fonctionnalité
   ```bash
   git checkout -b feature/super-amelioration
   ```
3. **Committez vos changements**
   ```bash
   git commit -m "Ajout d'une super amélioration"
   ```
4. **Pushez vers la branche**
   ```bash
   git push origin feature/super-amelioration
   ```
5. **Ouvrez une Pull Request**

### Guidelines

- Commentez votre code en français
- Suivez la structure existante
- Testez vos améliorations avant de soumettre
- Documentez les nouvelles fonctionnalités

---

## Licence

Ce projet est sous licence MIT. Vous êtes libre de :

- Utiliser le code pour vos projets personnels
- Modifier et adapter le code
- Distribuer votre version modifiée

---

## Support

Des questions ? Des suggestions ?

- Ouvrez une issue sur GitHub
- Partagez vos créations !

---

## Apprentissage

Ce projet est idéal pour apprendre :

- **Python** : Classes, héritage, dictionnaires
- **Tkinter** : Interface graphique, événements
- **Architecture logicielle** : Séparation des responsabilités
- **Programmation orientée objet** : Héritage, polymorphisme
- **Persistence des données** : JSON, sauvegarde/chargement

---

## Remerciements

Merci d'utiliser ce projet ! N'hésitez pas à :

- Mettre une étoile si vous aimez le projet
- Signaler les bugs
- Proposer de nouvelles idées
- Partager vos créations

---

**Bon clicker !**

---

_Dernière mise à jour : 03/02/2026_
_Version : 2.0_
