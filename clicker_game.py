"""
CLICKER GAME - Version Multi-Cibles
====================================

Système de cibles illimitées avec améliorations spécifiques !
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, List
import json


# ============================================================================
# SYSTÈME DE CIBLES
# ============================================================================

class Cible:
    """Représente une cible cliquable dans le jeu"""
    
    def __init__(self, numero: int):
        self.numero = numero
        # Chaque cible rapporte progressivement plus que la précédente
        self.points_par_clic = int(1 * (numero ** 1.5))
        self.auto_clics_par_tick = 0
        self.total_clics = 0
        self.points_gagnes = 0
    
    def clic(self):
        """Effectue un clic sur cette cible"""
        self.total_clics += 1
        self.points_gagnes += self.points_par_clic
        return self.points_par_clic
    
    def get_couleur(self):
        """Retourne une couleur unique pour cette cible"""
        couleurs = [
            '#4CAF50',  # Vert
            '#FF9800',  # Orange
            '#2196F3',  # Bleu
            '#9C27B0',  # Violet
            '#F44336',  # Rouge
            '#00BCD4',  # Cyan
            '#FF5722',  # Orange foncé
            '#8BC34A',  # Vert clair
            '#FFEB3B',  # Jaune
            '#E91E63',  # Rose
        ]
        return couleurs[(self.numero - 1) % len(couleurs)]
    
    def to_dict(self):
        """Convertit en dictionnaire pour sauvegarde"""
        return {
            'numero': self.numero,
            'points_par_clic': self.points_par_clic,
            'auto_clics_par_tick': self.auto_clics_par_tick,
            'total_clics': self.total_clics,
            'points_gagnes': self.points_gagnes
        }
    
    @staticmethod
    def from_dict(data):
        """Crée une cible depuis un dictionnaire"""
        cible = Cible(data['numero'])
        cible.points_par_clic = data['points_par_clic']
        cible.auto_clics_par_tick = data['auto_clics_par_tick']
        cible.total_clics = data['total_clics']
        cible.points_gagnes = data['points_gagnes']
        return cible


# ============================================================================
# SYSTÈME D'AMÉLIORATIONS
# ============================================================================

class Amelioration:
    """
    Classe de base pour toutes les améliorations.
    
    Pour créer une nouvelle amélioration :
    1. Créez une classe qui hérite de Amelioration
    2. Définissez __init__ avec nom, description, prix de base
    3. Spécifiez si c'est pour_cible=True (amélioration par cible) ou False (globale)
    4. Implémentez la méthode appliquer(game, cible_id) qui modifie le jeu
    """
    
    def __init__(self, nom: str, description: str, prix_base: int, 
                 multiplicateur_prix: float = 1.15, pour_cible: bool = True):
        self.nom = nom
        self.description = description
        self.prix_base = prix_base
        self.multiplicateur_prix = multiplicateur_prix
        self.pour_cible = pour_cible  # True = amélioration spécifique à une cible
        self.niveaux = {}  # {cible_id: niveau}
    
    def get_niveau(self, cible_id: int = None) -> int:
        """Retourne le niveau pour une cible donnée"""
        if cible_id is None:
            return sum(self.niveaux.values())
        return self.niveaux.get(cible_id, 0)
    
    def get_prix(self, cible_id: int = None) -> int:
        """Calcule le prix actuel basé sur le niveau"""
        niveau = self.get_niveau(cible_id)
        # Prix augmente aussi selon le numéro de la cible
        multiplicateur_cible = 1.0 if (cible_id is None or cible_id == 0) else (cible_id ** 0.5)
        return int(self.prix_base * multiplicateur_cible * (self.multiplicateur_prix ** niveau))
    
    def acheter(self, game, cible_id: int = None) -> bool:
        """Tente d'acheter l'amélioration"""
        prix = self.get_prix(cible_id)
        if game.points >= prix:
            game.points -= prix
            if cible_id is None:
                self.niveaux[0] = self.niveaux.get(0, 0) + 1
            else:
                self.niveaux[cible_id] = self.niveaux.get(cible_id, 0) + 1
            self.appliquer(game, cible_id)
            return True
        return False
    
    def appliquer(self, game, cible_id: int = None):
        """À implémenter dans les sous-classes"""
        raise NotImplementedError


# ============================================================================
# AMÉLIORATIONS PRÉDÉFINIES
# ============================================================================

class AmeliorationClicPuissance(Amelioration):
    """Augmente le nombre de points par clic"""
    
    def __init__(self):
        super().__init__(
            nom="Clic Puissant",
            description="Points par clic +1",
            prix_base=10,
            pour_cible=True
        )
        self.bonus = 1
    
    def appliquer(self, game, cible_id):
        if cible_id and cible_id in game.cibles:
            game.cibles[cible_id].points_par_clic += self.bonus


class AmeliorationClicMultiplicateur(Amelioration):
    """Multiplie les points par clic"""
    
    def __init__(self):
        super().__init__(
            nom="Multiplicateur x2",
            description="Double les points par clic",
            prix_base=100,
            multiplicateur_prix=2.0,
            pour_cible=True
        )
    
    def appliquer(self, game, cible_id):
        if cible_id and cible_id in game.cibles:
            game.cibles[cible_id].points_par_clic *= 2


class AmeliorationAutoClicker(Amelioration):
    """Ajoute des clics automatiques"""
    
    def __init__(self):
        super().__init__(
            nom="Auto-Clicker",
            description="+1 clic automatique",
            prix_base=50,
            pour_cible=True
        )
        self.clics_par_tick = 1
    
    def appliquer(self, game, cible_id):
        if cible_id and cible_id in game.cibles:
            game.cibles[cible_id].auto_clics_par_tick += self.clics_par_tick


class AmeliorationVitesseAuto(Amelioration):
    """Augmente la vitesse des clics automatiques"""
    
    def __init__(self):
        super().__init__(
            nom="Vitesse Auto",
            description="Réduit délai auto de 0.3s",
            prix_base=200,
            multiplicateur_prix=1.5,
            pour_cible=False
        )
    
    def appliquer(self, game, cible_id):
        game.delai_auto_clic = max(0.3, game.delai_auto_clic - 0.3)


class AmeliorationNouvelleCible(Amelioration):
    """Débloque une nouvelle cible cliquable"""
    
    def __init__(self):
        super().__init__(
            nom="Nouvelle Cible",
            description="Débloque une nouvelle cible !",
            prix_base=500,
            multiplicateur_prix=2.5,
            pour_cible=False
        )
    
    def appliquer(self, game, cible_id):
        game.ajouter_cible()


# ============================================================================
# MOTEUR DU JEU
# ============================================================================

class ClickerGame:
    """Classe principale du jeu. Gère les points, les cibles et les améliorations."""
    
    def __init__(self):
        # Stats principales
        self.points = 0
        self.total_clics = 0
        
        # Système de cibles
        self.cibles: Dict[int, Cible] = {}
        self.cible_selectionnee = None
        self.prochain_numero_cible = 1
        
        # Auto-clicker global
        self.delai_auto_clic = 3.0  # secondes
        self.dernier_auto_clic = time.time()
        
        # Liste des types d'améliorations disponibles
        self.types_ameliorations: List[Amelioration] = self.initialiser_ameliorations()
        
        # Callbacks pour l'interface (DOIT être initialisé AVANT ajouter_cible)
        self.callbacks = {
            'update_display': None,
            'update_shop': None,
            'nouvelle_cible': None
        }
        
        # Ajouter la première cible (APRÈS l'initialisation des callbacks)
        self.ajouter_cible()
        self.cible_selectionnee = 1
    
    def initialiser_ameliorations(self) -> List[Amelioration]:
        """
        AJOUTEZ VOS AMÉLIORATIONS ICI !
        
        Pour ajouter une amélioration :
        1. Créez une classe qui hérite de Amelioration
        2. Ajoutez-la à cette liste
        """
        return [
            AmeliorationClicPuissance(),
            AmeliorationClicMultiplicateur(),
            AmeliorationAutoClicker(),
            AmeliorationVitesseAuto(),
            AmeliorationNouvelleCible(),
        ]
    
    def ajouter_cible(self):
        """Ajoute une nouvelle cible au jeu"""
        numero = self.prochain_numero_cible
        self.cibles[numero] = Cible(numero)
        self.prochain_numero_cible += 1
        
        if self.callbacks['nouvelle_cible']:
            self.callbacks['nouvelle_cible'](numero)
        
        return numero
    
    def clic(self, cible_id: int):
        """Effectue un clic sur une cible"""
        if cible_id in self.cibles:
            points_gagnes = self.cibles[cible_id].clic()
            self.points += points_gagnes
            self.total_clics += 1
            self.notifier_update()
    
    def selectionner_cible(self, cible_id: int):
        """Sélectionne une cible pour afficher ses améliorations"""
        if cible_id in self.cibles:
            self.cible_selectionnee = cible_id
            if self.callbacks['update_shop']:
                self.callbacks['update_shop']()
    
    def update_auto_clicker(self):
        """Met à jour les clics automatiques"""
        temps_actuel = time.time()
        if temps_actuel - self.dernier_auto_clic >= self.delai_auto_clic:
            # Auto-clics pour chaque cible
            for cible in self.cibles.values():
                if cible.auto_clics_par_tick > 0:
                    points = cible.points_par_clic * cible.auto_clics_par_tick
                    cible.points_gagnes += points
                    self.points += points
            
            self.dernier_auto_clic = temps_actuel
            self.notifier_update()
    
    def acheter_amelioration(self, amelioration: Amelioration, cible_id: int = None) -> bool:
        """Tente d'acheter une amélioration"""
        if amelioration.acheter(self, cible_id):
            self.notifier_update()
            if self.callbacks['update_shop']:
                self.callbacks['update_shop']()
            return True
        return False
    
    def get_ameliorations_pour_cible(self, cible_id: int) -> List[Amelioration]:
        """Retourne les améliorations disponibles pour une cible donnée"""
        ameliorations = []
        
        # Améliorations spécifiques à la cible
        for amelio in self.types_ameliorations:
            if amelio.pour_cible:
                ameliorations.append(amelio)
        
        # Améliorations globales
        for amelio in self.types_ameliorations:
            if not amelio.pour_cible:
                ameliorations.append(amelio)
        
        return ameliorations
    
    def notifier_update(self):
        """Notifie l'interface d'une mise à jour"""
        if self.callbacks['update_display']:
            self.callbacks['update_display']()
    
    def sauvegarder(self, fichier: str = "save_v2.json"):
        """Sauvegarde la partie"""
        data = {
            'points': self.points,
            'total_clics': self.total_clics,
            'delai_auto_clic': self.delai_auto_clic,
            'prochain_numero_cible': self.prochain_numero_cible,
            'cible_selectionnee': self.cible_selectionnee,
            'cibles': {
                cible_id: cible.to_dict() 
                for cible_id, cible in self.cibles.items()
            },
            'ameliorations': {
                type(a).__name__: a.niveaux 
                for a in self.types_ameliorations
            }
        }
        with open(fichier, 'w') as f:
            json.dump(data, f, indent=2)
    
    def charger(self, fichier: str = "save_v2.json"):
        """Charge une partie sauvegardée"""
        try:
            with open(fichier, 'r') as f:
                data = json.load(f)
            
            self.points = data['points']
            self.total_clics = data['total_clics']
            self.delai_auto_clic = data['delai_auto_clic']
            self.prochain_numero_cible = data['prochain_numero_cible']
            self.cible_selectionnee = data['cible_selectionnee']
            
            # Restaurer les cibles
            self.cibles = {}
            for cible_id_str, cible_data in data['cibles'].items():
                cible_id = int(cible_id_str)
                self.cibles[cible_id] = Cible.from_dict(cible_data)
            
            # Restaurer les niveaux des améliorations
            for amelioration in self.types_ameliorations:
                nom_classe = type(amelioration).__name__
                if nom_classe in data['ameliorations']:
                    # Convertir les clés string en int
                    amelioration.niveaux = {
                        int(k): v for k, v in data['ameliorations'][nom_classe].items()
                    }
            
            return True
        except FileNotFoundError:
            return False


# ============================================================================
# INTERFACE GRAPHIQUE
# ============================================================================

class ClickerUI:
    """Interface graphique du jeu"""
    
    def __init__(self):
        self.game = ClickerGame()
        
        # Configuration de la fenêtre
        self.root = tk.Tk()
        self.root.title("Clicker Game - Multi-Cibles")
        self.root.geometry("1920x1080")
        self.root.configure(bg='#1a1a1a')
        
        # Charger la sauvegarde si elle existe
        if self.game.charger():
            print("Partie chargée !")
        
        # Configurer les callbacks
        self.game.callbacks['update_display'] = self.update_display
        self.game.callbacks['update_shop'] = self.update_shop
        self.game.callbacks['nouvelle_cible'] = self.ajouter_bouton_cible
        
        # Dictionnaire des boutons de cibles
        self.boutons_cibles = {}
        
        # Dictionnaire des boutons d'amélioration
        self.boutons_amelioration = {}
        
        self.creer_interface()
        self.update_loop()
    
    def creer_interface(self):
        """Crée l'interface graphique"""
        # === CANVAS PRINCIPAL AVEC SCROLLBAR ===
        main_canvas = tk.Canvas(self.root, bg='#1a1a1a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        
        # Frame scrollable
        scrollable_frame = tk.Frame(main_canvas, bg='#1a1a1a')
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Activer le scroll avec la molette
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pack canvas et scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === HEADER ===
        header = tk.Frame(scrollable_frame, bg='#1a1a1a')
        header.pack(fill=tk.X, padx=20, pady=10)
        
        # Boutons de sauvegarde à gauche (invisibles pour espacer)
        left_spacer = tk.Frame(header, bg='#1a1a1a', width=150)
        left_spacer.pack(side=tk.LEFT)
        
        # Titre centré
        titre = tk.Label(
            header,
            text="CLICKER GAME - MULTI-CIBLES",
            font=('Arial', 24, 'bold'),
            bg='#1a1a1a',
            fg='#00ff88'
        )
        titre.pack(side=tk.LEFT, expand=True)
        
        # Boutons de sauvegarde à droite
        save_frame = tk.Frame(header, bg='#1a1a1a')
        save_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            save_frame,
            text="Sauvegarder",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            command=lambda: self.game.sauvegarder() or print("Sauvegardé !"),
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            save_frame,
            text="Charger",
            font=('Arial', 10),
            bg='#9C27B0',
            fg='white',
            command=self.charger_partie,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # === ZONE CENTRALE ===
        main_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Score
        self.label_points = tk.Label(
            main_frame,
            text="Points: 0",
            font=('Arial', 28, 'bold'),
            bg='#1a1a1a',
            fg='white'
        )
        self.label_points.pack(pady=10)
        
        # Stats globales
        self.label_stats = tk.Label(
            main_frame,
            text="",
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#aaaaaa',
            justify=tk.CENTER
        )
        self.label_stats.pack(pady=5)
        
        # === ZONE DES CIBLES (Multi-lignes automatique) ===
        cibles_label = tk.Label(
            main_frame,
            text="VOS CIBLES",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#FFD700'
        )
        cibles_label.pack(pady=(20, 10))
        
        # Container principal pour centrer les cibles
        cibles_outer_container = tk.Frame(main_frame, bg='#1a1a1a')
        cibles_outer_container.pack(fill=tk.BOTH, pady=10)
        
        # Container intérieur pour les cibles avec espacement uniforme
        self.cibles_container = tk.Frame(cibles_outer_container, bg='#1a1a1a')
        self.cibles_container.pack(padx=40, fill=tk.BOTH)
        
        # Créer les boutons pour les cibles existantes
        for cible_id in self.game.cibles.keys():
            self.ajouter_bouton_cible(cible_id)
        
        # === BOUTIQUE D'AMÉLIORATIONS (Multi-lignes) ===
        shop_label = tk.Label(
            main_frame,
            text="AMÉLIORATIONS",
            font=('Arial', 14, 'bold'),
            bg='#1a1a1a',
            fg='#FFD700'
        )
        shop_label.pack(pady=(20, 10))
        
        # Info cible sélectionnée
        self.label_cible_selectionnee = tk.Label(
            main_frame,
            text="",
            font=('Arial', 11, 'bold'),
            bg='#1a1a1a',
            fg='#FFD700'
        )
        self.label_cible_selectionnee.pack(pady=5)
        
        # Container principal pour centrer les améliorations
        shop_outer_container = tk.Frame(main_frame, bg='#1a1a1a')
        shop_outer_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Container intérieur pour les améliorations avec espacement uniforme
        self.shop_container = tk.Frame(shop_outer_container, bg='#1a1a1a')
        self.shop_container.pack(padx=40, fill=tk.BOTH)
        
        # Créer la boutique
        self.creer_boutique()
    
    def ajouter_bouton_cible(self, cible_id: int):
        """Ajoute un bouton pour une nouvelle cible"""
        cible = self.game.cibles[cible_id]
        
        # Frame pour la cible (ajout direct au container avec espacement uniforme)
        cible_frame = tk.Frame(self.cibles_container, bg='#2a2a2a', relief=tk.RAISED, bd=3)
        cible_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Titre de la cible
        titre_cible = tk.Label(
            cible_frame,
            text=f"CIBLE {cible_id}",
            font=('Arial', 12, 'bold'),
            bg='#2a2a2a',
            fg=cible.get_couleur()
        )
        titre_cible.pack(pady=(10, 5))
        
        # Stats de la cible
        stats_cible = tk.Label(
            cible_frame,
            text="",
            font=('Arial', 9),
            bg='#2a2a2a',
            fg='#cccccc',
            justify=tk.LEFT
        )
        stats_cible.pack(padx=10, pady=5)
        
        # Bouton de clic
        btn = tk.Button(
            cible_frame,
            text="CLIC !",
            font=('Arial', 16, 'bold'),
            bg=cible.get_couleur(),
            fg='white',
            width=12,
            height=2,
            command=lambda: self.clic_cible(cible_id),
            cursor='hand2',
            relief=tk.RAISED,
            bd=4
        )
        btn.pack(padx=10, pady=10)
        
        # Bouton pour sélectionner cette cible
        btn_select = tk.Button(
            cible_frame,
            text="Voir améliorations",
            font=('Arial', 9),
            bg='#444444',
            fg='white',
            command=lambda: self.selectionner_cible(cible_id),
            cursor='hand2'
        )
        btn_select.pack(padx=10, pady=(0, 10))
        
        self.boutons_cibles[cible_id] = {
            'frame': cible_frame,
            'stats': stats_cible,
            'button': btn,
            'select': btn_select
        }
        
        # Ne mettre à jour l'affichage que si l'interface est complètement créée
        if hasattr(self, 'label_cible_selectionnee'):
            self.update_display()
    
    def clic_cible(self, cible_id: int):
        """Gère le clic sur une cible"""
        self.game.clic(cible_id)
        
        # Animation
        if cible_id in self.boutons_cibles:
            btn = self.boutons_cibles[cible_id]['button']
            original_bg = btn['bg']
            btn.config(bg='#FFD700')
            self.root.after(100, lambda: btn.config(bg=original_bg))
    
    def selectionner_cible(self, cible_id: int):
        """Sélectionne une cible et affiche ses améliorations"""
        self.game.selectionner_cible(cible_id)
        
        # Mettre en surbrillance le bouton sélectionné
        for id, widgets in self.boutons_cibles.items():
            if id == cible_id:
                widgets['select'].config(bg='#FFD700', fg='black', text="SÉLECTIONNÉ")
            else:
                widgets['select'].config(bg='#444444', fg='white', text="Voir améliorations")
    
    def creer_boutique(self):
        """Crée les boutons d'amélioration dans la boutique"""
        ameliorations = self.game.get_ameliorations_pour_cible(self.game.cible_selectionnee)
        
        for amelioration in ameliorations:
            # Frame pour l'amélioration (ajout direct au container avec espacement uniforme)
            frame = tk.Frame(self.shop_container, bg='#3a3a3a', relief=tk.RAISED, bd=2)
            frame.pack(side=tk.LEFT, padx=15, pady=10)
            
            # Nom
            nom_label = tk.Label(
                frame,
                text=amelioration.nom,
                font=('Arial', 11, 'bold'),
                bg='#3a3a3a',
                fg='white',
                wraplength=200
            )
            nom_label.pack(padx=10, pady=(10, 5))
            
            # Description
            desc_label = tk.Label(
                frame,
                text=amelioration.description,
                font=('Arial', 9),
                bg='#3a3a3a',
                fg='#cccccc',
                wraplength=200
            )
            desc_label.pack(padx=10, pady=5)
            
            # Niveau
            niveau_label = tk.Label(
                frame,
                text="",
                font=('Arial', 9),
                bg='#3a3a3a',
                fg='#888888'
            )
            niveau_label.pack(padx=10, pady=5)
            
            # Bouton d'achat
            btn = tk.Button(
                frame,
                text="",
                font=('Arial', 10, 'bold'),
                bg='#4CAF50',
                fg='white',
                width=15,
                command=lambda a=amelioration: self.acheter(a),
                cursor='hand2',
                pady=10
            )
            btn.pack(padx=10, pady=(5, 10))
            
            self.boutons_amelioration[amelioration] = {
                'frame': frame,
                'button': btn,
                'niveau': niveau_label
            }
        
        self.update_shop()
    
    def acheter(self, amelioration: Amelioration):
        """Tente d'acheter une amélioration"""
        cible_id = self.game.cible_selectionnee if amelioration.pour_cible else None
        
        if self.game.acheter_amelioration(amelioration, cible_id):
            # Animation de succès
            btn = self.boutons_amelioration[amelioration]['button']
            original_bg = btn['bg']
            btn.config(bg='#FFD700')
            self.root.after(200, lambda: btn.config(bg=original_bg))
        else:
            # Animation d'échec
            btn = self.boutons_amelioration[amelioration]['button']
            original_bg = btn['bg']
            btn.config(bg='#f44336')
            self.root.after(200, lambda: btn.config(bg=original_bg))
    
    def update_display(self):
        """Met à jour l'affichage"""
        # Points totaux
        self.label_points.config(text=f"Points: {self.game.points:,}")
        
        # Stats globales
        stats_text = f"Clics totaux: {self.game.total_clics:,} | "
        stats_text += f"Auto-clic: {self.game.delai_auto_clic:.1f}s | "
        stats_text += f"Cibles: {len(self.game.cibles)}"
        self.label_stats.config(text=stats_text)
        
        # Info cible sélectionnée
        if self.game.cible_selectionnee:
            cible = self.game.cibles[self.game.cible_selectionnee]
            self.label_cible_selectionnee.config(
                text=f"Améliorations pour CIBLE {cible.numero}",
                fg=cible.get_couleur()
            )
        
        # Mise à jour des stats de chaque cible
        for cible_id, widgets in self.boutons_cibles.items():
            if cible_id in self.game.cibles:
                cible = self.game.cibles[cible_id]
                stats = f"Points/clic: {cible.points_par_clic}\n"
                stats += f"Auto: {cible.auto_clics_par_tick}\n"
                stats += f"Clics: {cible.total_clics:,}\n"
                stats += f"Total: {cible.points_gagnes:,}"
                widgets['stats'].config(text=stats)
    
    def update_shop(self):
        """Met à jour l'affichage de la boutique"""
        for amelioration, widgets in self.boutons_amelioration.items():
            cible_id = self.game.cible_selectionnee if amelioration.pour_cible else None
            prix = amelioration.get_prix(cible_id)
            niveau = amelioration.get_niveau(cible_id)
            
            widgets['button'].config(text=f"{prix:,}")
            widgets['niveau'].config(text=f"Niveau: {niveau}")
            
            # Changer la couleur selon si on peut acheter
            if self.game.points >= prix:
                widgets['button'].config(state=tk.NORMAL, bg='#4CAF50')
            else:
                widgets['button'].config(state=tk.NORMAL, bg='#666666')
    
    def charger_partie(self):
        """Charge une partie et reconstruit l'interface"""
        if self.game.charger():
            # Détruire les anciens boutons de cibles
            for widgets in self.boutons_cibles.values():
                widgets['frame'].destroy()
            self.boutons_cibles.clear()
            
            # Recréer les boutons de cibles
            for cible_id in self.game.cibles.keys():
                self.ajouter_bouton_cible(cible_id)
            
            self.update_display()
            self.update_shop()
            self.selectionner_cible(self.game.cible_selectionnee)
            print("✓ Partie chargée !")
    
    def update_loop(self):
        """Boucle de mise à jour du jeu"""
        self.game.update_auto_clicker()
        self.update_shop()
        self.root.after(100, self.update_loop)
    
    def run(self):
        """Lance le jeu"""
        self.update_display()
        self.root.mainloop()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CLICKER GAME - VERSION MULTI-CIBLES")
    print("=" * 70)
    print("\nNOUVEAUTÉS :")
    print("   • Autant de cibles que vous voulez !")
    print("   • Chaque cible a ses propres améliorations")
    print("   • Chaque nouvelle cible rapporte plus de points")
    print("   • Interface multi-lignes avec scroll vertical")
    print("   • Utilisez la molette pour défiler !")
    print("\nPour ajouter vos propres améliorations :")
    print("   1. Créez une classe qui hérite de 'Amelioration'")
    print("   2. Spécifiez pour_cible=True (par cible) ou False (globale)")
    print("   3. Implémentez la méthode 'appliquer(self, game, cible_id)'")
    print("   4. Ajoutez-la dans 'initialiser_ameliorations()'")
    print("\n" + "=" * 70)
    print("Lancement du jeu...\n")
    
    app = ClickerUI()
    app.run()