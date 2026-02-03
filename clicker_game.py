"""
CLICKER GAME - Jeu modulable et extensible
===========================================

Architecture simple pour ajouter facilement vos propres améliorations !
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Callable, Dict, List
import json


# ============================================================================
# SYSTÈME D'AMÉLIORATIONS - Ajoutez vos propres améliorations ici !
# ============================================================================

class Amelioration:
    """
    Classe de base pour toutes les améliorations.
    
    Pour créer une nouvelle amélioration :
    1. Créez une classe qui hérite de Amelioration
    2. Définissez __init__ avec nom, description, prix de base
    3. Implémentez la méthode appliquer(game) qui modifie le jeu
    """
    
    def __init__(self, nom: str, description: str, prix_base: int, 
                 multiplicateur_prix: float = 1.15):
        self.nom = nom
        self.description = description
        self.prix_base = prix_base
        self.multiplicateur_prix = multiplicateur_prix
        self.niveau = 0
    
    def get_prix(self) -> int:
        """Calcule le prix actuel basé sur le niveau"""
        return int(self.prix_base * (self.multiplicateur_prix ** self.niveau))
    
    def acheter(self, game) -> bool:
        """Tente d'acheter l'amélioration"""
        prix = self.get_prix()
        if game.points >= prix:
            game.points -= prix
            self.niveau += 1
            self.appliquer(game)
            return True
        return False
    
    def appliquer(self, game):
        """À implémenter dans les sous-classes"""
        raise NotImplementedError


# ============================================================================
# AMÉLIORATIONS PRÉDÉFINIES - Exemples d'améliorations
# ============================================================================

class AmeliorationClicPuissance(Amelioration):
    """Augmente le nombre de points par clic"""
    
    def __init__(self):
        super().__init__(
            nom="Clic Puissant",
            description="Points par clic +1",
            prix_base=10
        )
        self.bonus = 1
    
    def appliquer(self, game):
        game.points_par_clic += self.bonus


class AmeliorationClicMultiplicateur(Amelioration):
    """Multiplie les points par clic"""
    
    def __init__(self):
        super().__init__(
            nom="Multiplicateur x2",
            description="Double les points par clic",
            prix_base=100,
            multiplicateur_prix=2.0
        )
    
    def appliquer(self, game):
        game.points_par_clic *= 2


class AmeliorationAutoClicker(Amelioration):
    """Ajoute des clics automatiques"""
    
    def __init__(self):
        super().__init__(
            nom="Auto-Clicker",
            description="+1 clic automatique/3s",
            prix_base=50
        )
        self.clics_par_tick = 1
    
    def appliquer(self, game):
        game.auto_clics_par_tick += self.clics_par_tick


class AmeliorationVitesseAuto(Amelioration):
    """Augmente la vitesse des clics automatiques"""
    
    def __init__(self):
        super().__init__(
            nom="Vitesse Auto",
            description="Réduit délai auto de 0.5s",
            prix_base=200,
            multiplicateur_prix=1.5
        )
    
    def appliquer(self, game):
        game.delai_auto_clic = max(0.5, game.delai_auto_clic - 0.5)


class AmeliorationSecondeCible(Amelioration):
    """Débloque une seconde cible cliquable"""
    
    def __init__(self):
        super().__init__(
            nom="Seconde Cible",
            description="Débloque une nouvelle cible",
            prix_base=500,
            multiplicateur_prix=3.0
        )
    
    def appliquer(self, game):
        if not game.seconde_cible_active:
            game.activer_seconde_cible()


class AmeliorationCiblePuissance(Amelioration):
    """Améliore la puissance de la seconde cible"""
    
    def __init__(self):
        super().__init__(
            nom="Cible 2 - Puissance",
            description="Points cible 2 +2",
            prix_base=300
        )
    
    def appliquer(self, game):
        game.points_par_clic_cible2 += 2


class AmeliorationCibleAuto(Amelioration):
    """Auto-clic pour la seconde cible"""
    
    def __init__(self):
        super().__init__(
            nom="Cible 2 - Auto",
            description="+1 auto-clic cible 2",
            prix_base=400
        )
    
    def appliquer(self, game):
        game.auto_clics_cible2 += 1


class AmeliorationMegaBonus(Amelioration):
    """Bonus massif ponctuel"""
    
    def __init__(self):
        super().__init__(
            nom="MEGA BONUS",
            description="+1000 points !",
            prix_base=250,
            multiplicateur_prix=2.5
        )
    
    def appliquer(self, game):
        game.points += 1000


# ============================================================================
# MOTEUR DU JEU
# ============================================================================

class ClickerGame:
    """
    Classe principale du jeu.
    Gère les points, les clics et les améliorations.
    """
    
    def __init__(self):
        # Stats principales
        self.points = 0
        self.points_par_clic = 1
        self.total_clics = 0
        
        # Auto-clicker
        self.auto_clics_par_tick = 0
        self.delai_auto_clic = 3.0  # secondes
        self.dernier_auto_clic = time.time()
        
        # Seconde cible
        self.seconde_cible_active = False
        self.points_cible2 = 0
        self.points_par_clic_cible2 = 1
        self.auto_clics_cible2 = 0
        self.total_clics_cible2 = 0
        
        # Liste des améliorations disponibles
        self.ameliorations: List[Amelioration] = self.initialiser_ameliorations()
        
        # Callbacks pour l'interface
        self.callbacks = {
            'update_display': None,
            'update_shop': None
        }
    
    def initialiser_ameliorations(self) -> List[Amelioration]:
        """
        AJOUTEZ VOS AMÉLIORATIONS ICI !
        
        Pour ajouter une amélioration :
        1. Créez une classe qui hérite de Amelioration (voir exemples ci-dessus)
        2. Ajoutez-la à cette liste
        """
        return [
            AmeliorationClicPuissance(),
            AmeliorationClicMultiplicateur(),
            AmeliorationAutoClicker(),
            AmeliorationVitesseAuto(),
            AmeliorationSecondeCible(),
            AmeliorationCiblePuissance(),
            AmeliorationCibleAuto(),
            AmeliorationMegaBonus(),
        ]
    
    def clic(self):
        """Effectue un clic sur la cible principale"""
        self.points += self.points_par_clic
        self.total_clics += 1
        self.notifier_update()
    
    def clic_cible2(self):
        """Effectue un clic sur la seconde cible"""
        if self.seconde_cible_active:
            self.points_cible2 += self.points_par_clic_cible2
            self.points += self.points_par_clic_cible2  # Ajoute aussi aux points principaux
            self.total_clics_cible2 += 1
            self.notifier_update()
    
    def activer_seconde_cible(self):
        """Active la seconde cible"""
        self.seconde_cible_active = True
        if self.callbacks['update_display']:
            self.callbacks['update_display']()
    
    def update_auto_clicker(self):
        """Met à jour les clics automatiques"""
        temps_actuel = time.time()
        if temps_actuel - self.dernier_auto_clic >= self.delai_auto_clic:
            # Auto-clics cible principale
            if self.auto_clics_par_tick > 0:
                self.points += self.points_par_clic * self.auto_clics_par_tick
                self.dernier_auto_clic = temps_actuel
            
            # Auto-clics cible 2
            if self.seconde_cible_active and self.auto_clics_cible2 > 0:
                bonus = self.points_par_clic_cible2 * self.auto_clics_cible2
                self.points_cible2 += bonus
                self.points += bonus
            
            self.notifier_update()
    
    def acheter_amelioration(self, amelioration: Amelioration) -> bool:
        """Tente d'acheter une amélioration"""
        if amelioration.acheter(self):
            self.notifier_update()
            if self.callbacks['update_shop']:
                self.callbacks['update_shop']()
            return True
        return False
    
    def notifier_update(self):
        """Notifie l'interface d'une mise à jour"""
        if self.callbacks['update_display']:
            self.callbacks['update_display']()
    
    def sauvegarder(self, fichier: str = "save.json"):
        """Sauvegarde la partie"""
        data = {
            'points': self.points,
            'points_par_clic': self.points_par_clic,
            'total_clics': self.total_clics,
            'auto_clics_par_tick': self.auto_clics_par_tick,
            'delai_auto_clic': self.delai_auto_clic,
            'seconde_cible_active': self.seconde_cible_active,
            'points_cible2': self.points_cible2,
            'points_par_clic_cible2': self.points_par_clic_cible2,
            'auto_clics_cible2': self.auto_clics_cible2,
            'ameliorations': {
                type(a).__name__: a.niveau 
                for a in self.ameliorations
            }
        }
        with open(fichier, 'w') as f:
            json.dump(data, f, indent=2)
    
    def charger(self, fichier: str = "save.json"):
        """Charge une partie sauvegardée"""
        try:
            with open(fichier, 'r') as f:
                data = json.load(f)
            
            self.points = data['points']
            self.points_par_clic = data['points_par_clic']
            self.total_clics = data['total_clics']
            self.auto_clics_par_tick = data['auto_clics_par_tick']
            self.delai_auto_clic = data['delai_auto_clic']
            self.seconde_cible_active = data['seconde_cible_active']
            self.points_cible2 = data['points_cible2']
            self.points_par_clic_cible2 = data['points_par_clic_cible2']
            self.auto_clics_cible2 = data['auto_clics_cible2']
            
            # Restaurer les niveaux des améliorations
            for amelioration in self.ameliorations:
                nom_classe = type(amelioration).__name__
                if nom_classe in data['ameliorations']:
                    amelioration.niveau = data['ameliorations'][nom_classe]
            
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
        self.root.title("Clicker Game Modulable")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Charger la sauvegarde si elle existe
        if self.game.charger():
            print("Partie chargée !")
        
        # Configurer les callbacks
        self.game.callbacks['update_display'] = self.update_display
        self.game.callbacks['update_shop'] = self.update_shop
        
        self.creer_interface()
        self.update_loop()
    
    def creer_interface(self):
        """Crée l'interface graphique"""
        # === ZONE PRINCIPALE ===
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        titre = tk.Label(
            main_frame,
            text="CLICKER GAME",
            font=('Arial', 28, 'bold'),
            bg='#2b2b2b',
            fg='#00ff88'
        )
        titre.pack(pady=(0, 20))
        
        # Score
        self.label_points = tk.Label(
            main_frame,
            text="Points: 0",
            font=('Arial', 24, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        self.label_points.pack(pady=10)
        
        # Stats
        stats_frame = tk.Frame(main_frame, bg='#2b2b2b')
        stats_frame.pack(pady=10)
        
        self.label_stats = tk.Label(
            stats_frame,
            text="",
            font=('Arial', 11),
            bg='#2b2b2b',
            fg='#aaaaaa',
            justify=tk.LEFT
        )
        self.label_stats.pack()
        
        # === ZONE DE CLIC ===
        click_frame = tk.Frame(main_frame, bg='#2b2b2b')
        click_frame.pack(pady=20)
        
        # Bouton principal
        self.btn_clic = tk.Button(
            click_frame,
            text="CLIC !",
            font=('Arial', 20, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=15,
            height=3,
            command=self.game.clic,
            cursor='hand2',
            relief=tk.RAISED,
            bd=5
        )
        self.btn_clic.pack(side=tk.LEFT, padx=10)
        
        # Bouton seconde cible (caché au début)
        self.btn_clic2 = tk.Button(
            click_frame,
            text="CIBLE 2",
            font=('Arial', 20, 'bold'),
            bg='#FF9800',
            fg='white',
            width=15,
            height=3,
            command=self.game.clic_cible2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=5
        )
        
        # === BOUTIQUE ===
        shop_label = tk.Label(
            main_frame,
            text="BOUTIQUE D'AMÉLIORATIONS",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#FFD700'
        )
        shop_label.pack(pady=(20, 10))
        
        # Frame avec scroll pour la boutique
        shop_container = tk.Frame(main_frame, bg='#2b2b2b')
        shop_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(shop_container, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(shop_container, orient="vertical", command=canvas.yview)
        self.shop_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        self.shop_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.shop_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Créer les boutons d'amélioration
        self.boutons_amelioration = {}
        self.creer_boutique()
        
        # Boutons de sauvegarde
        save_frame = tk.Frame(main_frame, bg='#2b2b2b')
        save_frame.pack(pady=10)
        
        tk.Button(
            save_frame,
            text="Sauvegarder",
            font=('Arial', 11),
            bg='#2196F3',
            fg='white',
            command=lambda: self.game.sauvegarder() or print("✓ Partie sauvegardée !"),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            save_frame,
            text="Charger",
            font=('Arial', 11),
            bg='#9C27B0',
            fg='white',
            command=self.charger_partie,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def creer_boutique(self):
        """Crée les boutons d'amélioration dans la boutique"""
        for i, amelioration in enumerate(self.game.ameliorations):
            frame = tk.Frame(self.shop_frame, bg='#3a3a3a', relief=tk.RAISED, bd=2)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            info_frame = tk.Frame(frame, bg='#3a3a3a')
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
            
            nom_label = tk.Label(
                info_frame,
                text=amelioration.nom,
                font=('Arial', 12, 'bold'),
                bg='#3a3a3a',
                fg='white',
                anchor='w'
            )
            nom_label.pack(anchor='w')
            
            desc_label = tk.Label(
                info_frame,
                text=amelioration.description,
                font=('Arial', 9),
                bg='#3a3a3a',
                fg='#cccccc',
                anchor='w'
            )
            desc_label.pack(anchor='w')
            
            niveau_label = tk.Label(
                info_frame,
                text=f"Niveau: {amelioration.niveau}",
                font=('Arial', 9),
                bg='#3a3a3a',
                fg='#888888',
                anchor='w'
            )
            niveau_label.pack(anchor='w')
            
            btn = tk.Button(
                frame,
                text=f"{amelioration.get_prix()}",
                font=('Arial', 11, 'bold'),
                bg='#4CAF50',
                fg='white',
                width=12,
                command=lambda a=amelioration: self.acheter(a),
                cursor='hand2'
            )
            btn.pack(side=tk.RIGHT, padx=10, pady=5)
            
            self.boutons_amelioration[amelioration] = {
                'button': btn,
                'niveau': niveau_label
            }
    
    def acheter(self, amelioration: Amelioration):
        """Tente d'acheter une amélioration"""
        if self.game.acheter_amelioration(amelioration):
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
        # Points
        self.label_points.config(text=f"Points: {self.game.points:,}")
        
        # Stats
        stats_text = f"Points/clic: {self.game.points_par_clic}\n"
        stats_text += f"Clics totaux: {self.game.total_clics:,}\n"
        stats_text += f"Auto-clics: {self.game.auto_clics_par_tick} / {self.game.delai_auto_clic:.1f}s"
        
        if self.game.seconde_cible_active:
            stats_text += f"\n\n🎲 CIBLE 2\n"
            stats_text += f"Points cible 2: {self.game.points_cible2:,}\n"
            stats_text += f"Points/clic cible 2: {self.game.points_par_clic_cible2}\n"
            stats_text += f"Auto-clics cible 2: {self.game.auto_clics_cible2}"
            
            # Afficher le bouton de la cible 2
            if not self.btn_clic2.winfo_viewable():
                self.btn_clic2.pack(side=tk.LEFT, padx=10)
        
        self.label_stats.config(text=stats_text)
    
    def update_shop(self):
        """Met à jour l'affichage de la boutique"""
        for amelioration, widgets in self.boutons_amelioration.items():
            widgets['button'].config(text=f"{amelioration.get_prix():,}")
            widgets['niveau'].config(text=f"Niveau: {amelioration.niveau}")
            
            # Désactiver si pas assez d'argent
            if self.game.points >= amelioration.get_prix():
                widgets['button'].config(state=tk.NORMAL, bg='#4CAF50')
            else:
                widgets['button'].config(state=tk.NORMAL, bg='#666666')
    
    def charger_partie(self):
        """Charge une partie et met à jour l'interface"""
        if self.game.charger():
            self.update_display()
            self.update_shop()
            print("Partie chargée !")
    
    def update_loop(self):
        """Boucle de mise à jour du jeu"""
        self.game.update_auto_clicker()
        self.update_shop()
        self.root.after(100, self.update_loop)  # Update toutes les 100ms
    
    def run(self):
        """Lance le jeu"""
        self.update_display()
        self.root.mainloop()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CLICKER GAME - Version Modulable")
    print("=" * 60)
    print("\nPour ajouter vos propres améliorations :")
    print("1. Créez une classe qui hérite de 'Amelioration'")
    print("2. Implémentez la méthode 'appliquer(self, game)'")
    print("3. Ajoutez-la dans 'initialiser_ameliorations()'")
    print("\nExemple d'amélioration personnalisée :")
    print("""
class MaSuperAmelioration(Amelioration):
    def __init__(self):
        super().__init__(
            nom="Mon Amélioration",
            description="Ce qu'elle fait",
            prix_base=100
        )
    
    def appliquer(self, game):
        game.points_par_clic += 10  # Votre logique ici
""")
    print("\n" + "=" * 60)
    print("Lancement du jeu...\n")
    
    app = ClickerUI()
    app.run()
