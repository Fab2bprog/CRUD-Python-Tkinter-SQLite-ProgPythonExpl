# =============================================================================
# classes/base_window.py
# Classe de base abstraite pour toutes les fenêtres Toplevel de l'application.
# Centralise les comportements communs : modalité, thème, chargement d'images.
#
# Chargement d'images : utilise tkinter.PhotoImage (natif, sans dépendance).
# Les images PNG doivent être exactement 60×60 pixels (spec Section 4).
# =============================================================================

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.config import COULEURS, POLICES, IMAGES_DIR


class FenetreBase(tk.Toplevel):
    """
    Classe de base pour toutes les fenêtres secondaires (Toplevel).

    Fonctionnalités communes :
      - Positionnement centré sur le parent ou sur l'écran
      - Modalité via grab_set() et transient(parent)
      - Fermeture propre avec libération du grab
      - Méthode utilitaire de chargement d'image (tkinter.PhotoImage natif)
      - Application du thème visuel de l'application

    Héritage :
        class MaFenetre(FenetreBase):
            def __init__(self, parent):
                super().__init__(parent, titre="Ma Fenêtre", largeur=400, hauteur=300)
                self._construire_interface()
    """

    def __init__(
        self,
        parent: tk.Widget,
        titre: str,
        largeur: int,
        hauteur: int,
        min_largeur: Optional[int] = None,
        min_hauteur: Optional[int] = None,
        modale: bool = True,
    ) -> None:
        """
        :param parent:      Fenêtre parente (peut être Tk ou Toplevel)
        :param titre:       Titre affiché dans la barre de la fenêtre
        :param largeur:     Largeur initiale en pixels
        :param hauteur:     Hauteur initiale en pixels
        :param min_largeur: Largeur minimale (= largeur si None)
        :param min_hauteur: Hauteur minimale (= hauteur si None)
        :param modale:      Si True, bloque les interactions avec le parent
        """
        super().__init__(parent)

        self.title(titre)
        self.configure(bg=COULEURS["fond_principal"])

        # Taille et contraintes de redimensionnement
        self.geometry(f"{largeur}x{hauteur}")
        self.minsize(min_largeur or largeur, min_hauteur or hauteur)

        # Modalité
        if modale:
            self.transient(parent)
            self.grab_set()

        # Centrer la fenêtre sur le parent (ou sur l'écran)
        self._centrer(parent, largeur, hauteur)

        # Intercepter la fermeture via la croix
        self.protocol("WM_DELETE_WINDOW", self._on_fermeture)

        # Dictionnaire de cache pour les images chargées (évite le GC)
        self._cache_images: dict[str, tk.PhotoImage] = {}

    # ------------------------------------------------------------------
    # Centrage
    # ------------------------------------------------------------------

    def _centrer(self, parent: tk.Widget, largeur: int, hauteur: int) -> None:
        """
        Centre la fenêtre sur son parent, ou sur l'écran si le parent
        n'est pas encore affiché.

        :param parent:  Widget parent
        :param largeur: Largeur de cette fenêtre
        :param hauteur: Hauteur de cette fenêtre
        """
        self.update_idletasks()

        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - largeur) // 2
            y = py + (ph - hauteur) // 2
        except Exception:
            # Fallback : centrer sur l'écran
            x = (self.winfo_screenwidth()  - largeur)  // 2
            y = (self.winfo_screenheight() - hauteur) // 2

        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")

    # ------------------------------------------------------------------
    # Fermeture
    # ------------------------------------------------------------------

    def _on_fermeture(self) -> None:
        """
        Gère la fermeture propre de la fenêtre.
        Libère le grab modal et détruit la fenêtre.
        Peut être surchargée pour ajouter une confirmation.
        """
        self.grab_release()
        self.destroy()

    # ------------------------------------------------------------------
    # Chargement d'images
    # ------------------------------------------------------------------

    def charger_image(
        self,
        nom_fichier: str,
        taille: Optional[tuple[int, int]] = None,
    ) -> Optional[tk.PhotoImage]:
        """
        Charge une image PNG depuis le dossier images/ et la met en cache.

        Utilise tkinter.PhotoImage (natif, aucune dépendance externe).
        Les PNG doivent être exactement à la taille souhaitée (60×60 px
        pour les boutons, selon la Section 4 des spécifications).
        Le paramètre taille est conservé pour compatibilité d'interface
        mais n'est pas utilisé (les images doivent être aux bonnes dimensions).

        :param nom_fichier: Nom du fichier image (ex: "Base_create.png")
        :param taille:      Ignoré (conservé pour compatibilité)
        :return:            PhotoImage prête à être utilisée dans Tkinter,
                            ou None si le fichier est introuvable ou illisible
        """
        cle_cache = nom_fichier
        if cle_cache in self._cache_images:
            return self._cache_images[cle_cache]

        chemin = os.path.join(IMAGES_DIR, nom_fichier)
        if not os.path.isfile(chemin):
            # Image manquante : retourner None sans planter l'application
            return None

        try:
            photo = tk.PhotoImage(file=chemin)
            self._cache_images[cle_cache] = photo
            return photo
        except tk.TclError:
            # Fichier présent mais non lisible par Tkinter (ex: JPEG)
            return None

    # ------------------------------------------------------------------
    # Utilitaires d'interface
    # ------------------------------------------------------------------

    @staticmethod
    def appliquer_style_ttk() -> None:
        """
        Applique le thème visuel sobre et professionnel (gris/bleu)
        aux widgets ttk. À appeler une seule fois depuis main.py.
        """
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview (tableau)
        style.configure(
            "Treeview",
            background=COULEURS["fond_secondaire"],
            foreground=COULEURS["texte_principal"],
            fieldbackground=COULEURS["fond_secondaire"],
            font=POLICES["normale"],
            rowheight=26,
        )
        style.configure(
            "Treeview.Heading",
            background=COULEURS["entete_tableau"],
            foreground=COULEURS["texte_clair"],
            font=POLICES["sous_titre"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COULEURS["selection"])],
            foreground=[("selected", COULEURS["texte_principal"])],
        )

        # Boutons standard
        style.configure(
            "TButton",
            background=COULEURS["fond_bouton"],
            foreground=COULEURS["texte_clair"],
            font=POLICES["normale"],
            padding=6,
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", COULEURS["fond_bouton_hover"])],
        )

        # Champs de saisie
        style.configure(
            "TEntry",
            fieldbackground=COULEURS["fond_secondaire"],
            foreground=COULEURS["texte_principal"],
            font=POLICES["normale"],
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COULEURS["fond_secondaire"],
            foreground=COULEURS["texte_principal"],
            font=POLICES["normale"],
        )

        # Frame
        style.configure(
            "TFrame",
            background=COULEURS["fond_principal"],
        )

        # LabelFrame
        style.configure(
            "TLabelframe",
            background=COULEURS["fond_principal"],
            foreground=COULEURS["texte_principal"],
            font=POLICES["sous_titre"],
        )
        style.configure(
            "TLabelframe.Label",
            background=COULEURS["fond_principal"],
            foreground=COULEURS["texte_principal"],
            font=POLICES["sous_titre"],
        )

        # Label
        style.configure(
            "TLabel",
            background=COULEURS["fond_principal"],
            foreground=COULEURS["texte_principal"],
            font=POLICES["normale"],
        )

        # Scrollbar
        style.configure(
            "TScrollbar",
            background=COULEURS["fond_principal"],
            troughcolor=COULEURS["bordure"],
            relief="flat",
        )
