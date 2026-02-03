"""
=====================================
CLICKER GAME
=====================================
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
from typing import Dict
import os
import threading

app = Flask(__name__)
CORS(app)

# ============================================================================
# CIBLE
# ============================================================================

class Cible:
    def __init__(self, numero: int):
        self.numero = numero
        self.points_par_clic = int(1 * (numero ** 1.5))
        self.auto_clics_par_tick = 0
        self.total_clics = 0
        self.points_gagnes = 0

    def clic(self):
        self.total_clics += 1
        self.points_gagnes += self.points_par_clic
        return self.points_par_clic

    def couleur(self):
        couleurs = [
            '#4CAF50', '#FF9800', '#2196F3', '#9C27B0', '#F44336',
            '#00BCD4', '#FF5722', '#8BC34A', '#FFEB3B', '#E91E63'
        ]
        return couleurs[(self.numero - 1) % len(couleurs)]

    def to_dict(self):
        return {
            'numero': self.numero,
            'points_par_clic': self.points_par_clic,
            'auto_clics_par_tick': self.auto_clics_par_tick,
            'total_clics': self.total_clics,
            'points_gagnes': self.points_gagnes,
            'couleur': self.couleur()
        }

# ============================================================================
# AMELIORATIONS
# ============================================================================

class Amelioration:
    def __init__(self, nom, description, prix_base, mult=1.15, pour_cible=True):
        self.nom = nom
        self.description = description
        self.prix_base = prix_base
        self.mult = mult
        self.pour_cible = pour_cible
        self.niveaux = {}

    def niveau(self, cible_id=None):
        key = cible_id if cible_id else 0
        return self.niveaux.get(key, 0)

    def prix(self, cible_id=None):
        niv = self.niveau(cible_id)
        facteur = (cible_id ** 0.5) if cible_id else 1.0
        return int(self.prix_base * facteur * (self.mult ** niv))

    def acheter(self, game, cible_id=None):
        p = self.prix(cible_id)
        if game.points < p:
            return False
        game.points -= p
        key = cible_id if cible_id else 0
        self.niveaux[key] = self.niveau(key) + 1
        self.appliquer(game, cible_id)
        return True

    def appliquer(self, game, cible_id):
        pass

    def to_dict(self, cible_id=None):
        return {
            'nom': self.nom,
            'description': self.description,
            'prix': self.prix(cible_id),
            'niveau': self.niveau(cible_id),
            'pour_cible': self.pour_cible,
            'type': type(self).__name__
        }

# ---- TYPES ----

class ClicPuissant(Amelioration):
    def __init__(self):
        super().__init__("Clic +1", "+1 point/clic", 10)

    def appliquer(self, game, cible_id):
        if cible_id in game.cibles:
            game.cibles[cible_id].points_par_clic += 1


class DoubleClic(Amelioration):
    def __init__(self):
        super().__init__("x2 clic", "Double les points", 100, 2.0)

    def appliquer(self, game, cible_id):
        if cible_id in game.cibles:
            game.cibles[cible_id].points_par_clic *= 2


class AutoClicker(Amelioration):
    def __init__(self):
        super().__init__("AutoClicker", "+1 auto clic", 50)

    def appliquer(self, game, cible_id):
        if cible_id in game.cibles:
            game.cibles[cible_id].auto_clics_par_tick += 1


class SpeedAuto(Amelioration):
    def __init__(self):
        super().__init__("Speed Auto", "-0.2s delay", 200, 1.5, pour_cible=False)

    def appliquer(self, game, cible_id):
        game.delai_auto = max(0.3, game.delai_auto - 0.2)


class NewTarget(Amelioration):
    def __init__(self):
        super().__init__("Nouvelle cible", "Unlock target", 500, 2.5, False)

    def appliquer(self, game, cible_id):
        game.add_target()

# ============================================================================
# GAME ENGINE
# ============================================================================

class ClickerGame:
    def __init__(self):
        self.points = 0
        self.total_clics = 0
        self.cibles: Dict[int, Cible] = {}
        self.next_target = 1
        self.selected = 1
        self.delai_auto = 3.0
        self.last_auto = time.time()
        self.lock = threading.Lock()

        self.amelios = [
            ClicPuissant(),
            DoubleClic(),
            AutoClicker(),
            SpeedAuto(),
            NewTarget()
        ]

        self.add_target()

    def add_target(self):
        with self.lock:
            self.cibles[self.next_target] = Cible(self.next_target)
            self.next_target += 1

    def click(self, cible_id):
        with self.lock:
            if cible_id not in self.cibles:
                return 0
            pts = self.cibles[cible_id].clic()
            self.points += pts
            self.total_clics += 1
            return pts

    def auto_tick_loop(self):
        """Thread séparé pour l'auto-clicker"""
        while True:
            time.sleep(0.1)  # Check toutes les 100ms
            with self.lock:
                now = time.time()
                if now - self.last_auto >= self.delai_auto:
                    # Effectuer les auto-clics
                    for cible in self.cibles.values():
                        if cible.auto_clics_par_tick > 0:
                            pts = cible.points_par_clic * cible.auto_clics_par_tick
                            cible.points_gagnes += pts
                            self.points += pts
                    self.last_auto = now

    def buy_upgrade(self, type_name, cible_id=None):
        with self.lock:
            for a in self.amelios:
                if type(a).__name__ == type_name:
                    return a.acheter(self, cible_id)
            return False

    def upgrades_for(self, cible_id):
        with self.lock:
            return [a.to_dict(cible_id if a.pour_cible else None) for a in self.amelios]

    def state(self):
        with self.lock:
            return {
                'points': self.points,
                'total_clics': self.total_clics,
                'delai_auto_clic': self.delai_auto,
                'cible_selectionnee': self.selected,
                'cibles': {k: v.to_dict() for k, v in self.cibles.items()},
                'ameliorations': [a.to_dict(self.selected if a.pour_cible else None) for a in self.amelios]
            }

    def save(self, fichier='save.json'):
        with self.lock:
            data = {
                'points': self.points,
                'total_clics': self.total_clics,
                'delai_auto': self.delai_auto,
                'next_target': self.next_target,
                'selected': self.selected,
                'cibles': {k: v.to_dict() for k, v in self.cibles.items()},
                'amelios': {type(a).__name__: a.niveaux for a in self.amelios}
            }
            with open(fichier, 'w') as f:
                json.dump(data, f, indent=2)

    def load(self, fichier='save.json'):
        if not os.path.exists(fichier):
            return False
        
        with open(fichier) as f:
            data = json.load(f)
        
        with self.lock:
            self.points = data['points']
            self.total_clics = data['total_clics']
            self.delai_auto = data['delai_auto']
            self.next_target = data['next_target']
            self.selected = data['selected']
            
            # Recréer les cibles
            self.cibles = {}
            for cible_id_str, cible_data in data['cibles'].items():
                cible_id = int(cible_id_str)
                c = Cible(cible_data['numero'])
                c.points_par_clic = cible_data['points_par_clic']
                c.auto_clics_par_tick = cible_data['auto_clics_par_tick']
                c.total_clics = cible_data['total_clics']
                c.points_gagnes = cible_data['points_gagnes']
                self.cibles[cible_id] = c
            
            # Restaurer les niveaux d'amélioration
            for amelio in self.amelios:
                nom = type(amelio).__name__
                if nom in data.get('amelios', {}):
                    amelio.niveaux = {int(k): v for k, v in data['amelios'][nom].items()}
        
        return True

# ============================================================================
# INSTANCE GLOBALE + THREAD
# ============================================================================

game = ClickerGame()
auto_thread = threading.Thread(target=game.auto_tick_loop, daemon=True)
auto_thread.start()

# ============================================================================
# ROUTES API
# ============================================================================

@app.route('/api/game')
def api_game():
    return jsonify(game.state())

@app.route('/api/clic/<int:cible_id>', methods=['POST'])
def api_clic(cible_id):
    pts = game.click(cible_id)
    return jsonify({
        'success': True,
        'points_gagnes': pts,
        'points_total': game.points
    })

@app.route('/api/select/<int:cible_id>', methods=['POST'])
def api_select(cible_id):
    with game.lock:
        if cible_id in game.cibles:
            game.selected = cible_id
            return jsonify({
                'success': True,
                'ameliorations': game.upgrades_for(cible_id)
            })
    return jsonify({'success': False})

@app.route('/api/amelioration/acheter', methods=['POST'])
def api_buy():
    data = request.json
    success = game.buy_upgrade(data['type'], data.get('cible_id'))
    return jsonify({
        'success': success,
        'game_state': game.state()
    })

@app.route('/api/save', methods=['POST'])
def api_save():
    game.save()
    return jsonify({'success': True})

@app.route('/api/load', methods=['POST'])
def api_load():
    success = game.load()
    return jsonify({
        'success': success,
        'game_state': game.state() if success else None
    })

@app.route('/api/points')
def api_points():
    with game.lock:
        return jsonify({
            'points': game.points,
            'total_clics': game.total_clics
        })

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("CLICKER GAME - BACKEND API")
    print("=" * 70)
    print("\nServeur démarré sur http://localhost:5000")
    print("Auto-clicker thread actif ✓")
    print("\n" + "=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)