# =============================================================================
# models/client_model.py
# Modèle de données pour la table Clients de la base SQLite.
# Contient :
#   - La dataclass Client (représentation d'un enregistrement)
#   - La classe ClientDAO (Data Access Object : requêtes CRUDS)
# =============================================================================

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Optional

from core.database import GestionnaireBase


# ---------------------------------------------------------------------------
# Dataclass – représentation d'un enregistrement client
# ---------------------------------------------------------------------------

@dataclass
class Client:
    """
    Représente un enregistrement de la table Clients.

    Les types correspondent exactement aux colonnes SQLite :
      - IDCLIENT         → int  (None pour un nouvel enregistrement)
      - nom_client       → str
      - numero_telephone → str
      - adresse          → str
      - code_postal      → str  (5 chiffres, validé côté GUI et SQLite)
      - ville            → str
      - date_naissance   → str  (format ISO : YYYY-MM-DD)
      - credit_disponible→ float
      - bon_client       → bool (stocké 0/1 en SQLite)
      - couleur_cheveux  → str  (brun | blond | roux | chauve)
    """
    idclient          : Optional[int] = field(default=None)
    nom_client        : str           = field(default="")
    numero_telephone  : str           = field(default="")
    adresse           : str           = field(default="")
    code_postal       : str           = field(default="")
    ville             : str           = field(default="")
    date_naissance    : str           = field(default="")   # YYYY-MM-DD
    credit_disponible : float         = field(default=0.0)
    bon_client        : bool          = field(default=False)
    couleur_cheveux   : str           = field(default="brun")

    # ------------------------------------------------------------------
    # Méthodes utilitaires
    # ------------------------------------------------------------------

    def en_tuple_insertion(self) -> tuple:
        """
        Retourne les valeurs sous forme de tuple pour une insertion SQL
        (sans IDCLIENT, qui est géré séparément).
        """
        return (
            self.nom_client,
            self.numero_telephone,
            self.adresse,
            self.code_postal,
            self.ville,
            self.date_naissance,
            self.credit_disponible,
            int(self.bon_client),
            self.couleur_cheveux,
        )

    def en_tuple_modification(self) -> tuple:
        """
        Retourne les valeurs sous forme de tuple pour une mise à jour SQL
        (valeurs des champs + IDCLIENT en dernière position pour le WHERE).
        """
        return (
            self.nom_client,
            self.numero_telephone,
            self.adresse,
            self.code_postal,
            self.ville,
            self.date_naissance,
            self.credit_disponible,
            int(self.bon_client),
            self.couleur_cheveux,
            self.idclient,
        )

    @staticmethod
    def depuis_row(row: sqlite3.Row) -> "Client":
        """
        Construit un objet Client à partir d'un sqlite3.Row.

        :param row: Ligne retournée par GestionnaireBase.interroger()
        :return:    Instance de Client remplie
        """
        return Client(
            idclient          = row["IDCLIENT"],
            nom_client        = row["nom_client"],
            numero_telephone  = row["numero_telephone"],
            adresse           = row["adresse"],
            code_postal       = row["code_postal"],
            ville             = row["ville"],
            date_naissance    = row["date_naissance"],
            credit_disponible = row["credit_disponible"],
            bon_client        = bool(row["bon_client"]),
            couleur_cheveux   = row["couleur_cheveux"],
        )


# ---------------------------------------------------------------------------
# DAO – Data Access Object pour la table Clients
# ---------------------------------------------------------------------------

class ClientDAO:
    """
    Fournit toutes les opérations CRUDS sur la table Clients.

    Chaque méthode reçoit un GestionnaireBase déjà connecté en paramètre,
    ce qui permet de partager la même connexion dans toute l'application
    sans coupler ce module à une instance globale.
    """

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    @staticmethod
    def creer(db: GestionnaireBase, client: Client) -> Optional[int]:
        """
        Insère un nouveau client dans la base.

        L'IDCLIENT est calculé en Python via SELECT MAX(IDCLIENT) + 1
        pour rester maître de la valeur (pas d'AUTOINCREMENT SQLite).

        :param db:     Gestionnaire de base connecté
        :param client: Objet Client à insérer (idclient ignoré)
        :return:       IDCLIENT attribué, ou None en cas d'échec
        """
        # Calcul du prochain ID
        rows = db.interroger("SELECT COALESCE(MAX(IDCLIENT), 0) + 1 AS prochain FROM Clients;")
        if not rows:
            return None
        prochain_id: int = rows[0]["prochain"]

        requete = """
            INSERT INTO Clients (
                IDCLIENT, nom_client, numero_telephone, adresse,
                code_postal, ville, date_naissance,
                credit_disponible, bon_client, couleur_cheveux
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        curseur = db.executer(requete, (prochain_id,) + client.en_tuple_insertion())
        if curseur is not None:
            return prochain_id
        return None

    # ------------------------------------------------------------------
    # READ – lecture d'un seul enregistrement
    # ------------------------------------------------------------------

    @staticmethod
    def lire(db: GestionnaireBase, idclient: int) -> Optional[Client]:
        """
        Lit un client par son IDCLIENT.

        :param db:       Gestionnaire de base connecté
        :param idclient: Identifiant du client recherché
        :return:         Objet Client ou None si introuvable
        """
        rows = db.interroger(
            "SELECT * FROM Clients WHERE IDCLIENT = ?;",
            (idclient,)
        )
        if rows:
            return Client.depuis_row(rows[0])
        return None

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    @staticmethod
    def modifier(db: GestionnaireBase, client: Client) -> bool:
        """
        Met à jour tous les champs d'un client existant.

        :param db:     Gestionnaire de base connecté
        :param client: Objet Client avec les nouvelles valeurs (idclient requis)
        :return:       True si la mise à jour a réussi
        """
        requete = """
            UPDATE Clients SET
                nom_client        = ?,
                numero_telephone  = ?,
                adresse           = ?,
                code_postal       = ?,
                ville             = ?,
                date_naissance    = ?,
                credit_disponible = ?,
                bon_client        = ?,
                couleur_cheveux   = ?
            WHERE IDCLIENT = ?;
        """
        curseur = db.executer(requete, client.en_tuple_modification())
        return curseur is not None

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    @staticmethod
    def supprimer(db: GestionnaireBase, idclient: int) -> bool:
        """
        Supprime un client par son IDCLIENT.

        :param db:       Gestionnaire de base connecté
        :param idclient: Identifiant du client à supprimer
        :return:         True si la suppression a réussi
        """
        curseur = db.executer(
            "DELETE FROM Clients WHERE IDCLIENT = ?;",
            (idclient,)
        )
        return curseur is not None

    @staticmethod
    def supprimer_plusieurs(db: GestionnaireBase, ids: list[int]) -> bool:
        """
        Supprime plusieurs clients en une seule opération.

        :param db:  Gestionnaire de base connecté
        :param ids: Liste d'IDCLIENT à supprimer
        :return:    True si toutes les suppressions ont réussi
        """
        if not ids:
            return True
        placeholders = ", ".join("?" * len(ids))
        requete = f"DELETE FROM Clients WHERE IDCLIENT IN ({placeholders});"
        curseur = db.executer(requete, tuple(ids))
        return curseur is not None

    # ------------------------------------------------------------------
    # SEARCH – recherche partielle sur le nom
    # ------------------------------------------------------------------

    @staticmethod
    def rechercher(db: GestionnaireBase, nom: str = "") -> list[Client]:
        """
        Recherche des clients par nom (LIKE %nom%).
        Si nom est vide, retourne tous les clients.

        :param db:  Gestionnaire de base connecté
        :param nom: Chaîne de recherche (partielle)
        :return:    Liste d'objets Client correspondants
        """
        requete = """
            SELECT * FROM Clients
            WHERE nom_client LIKE ?
            ORDER BY nom_client ASC;
        """
        rows = db.interroger(requete, (f"%{nom}%",))
        return [Client.depuis_row(row) for row in rows]

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def compter(db: GestionnaireBase) -> int:
        """
        Retourne le nombre total de clients dans la table.

        :param db: Gestionnaire de base connecté
        :return:   Nombre d'enregistrements
        """
        rows = db.interroger("SELECT COUNT(*) AS total FROM Clients;")
        if rows:
            return rows[0]["total"]
        return 0
