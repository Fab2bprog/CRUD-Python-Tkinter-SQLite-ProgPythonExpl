# ProgPythonExpl

Programme de démonstration CRUD Python – Interface graphique Tkinter – Base SQLite.
Programme de niveau professionel.

<p align="center">
  <img src="https://github.com/Fab2bprog/CRUD-Python-Tkinter-ProgPythonExpl/blob/main/images/crudpythonpic.png" width="650" >
 </p>

---

## Description

**ProgPythonExpl** est un programme de type CRUD (Create – Read – Update – Delete)
servant d'exemple et de base de réflexion pour le développement de futurs projets Python.

Il gère les opérations principales sur une table **Clients** dans une base SQLite :
recherche, création, modification, suppression et sélection d'enregistrements.

---

## Prérequis

- **Python 3.13** ou supérieur
- **Aucune dépendance externe** — uniquement des modules Python standard
- **Tkinter** (inclus dans Python standard)
- **SQLite 3** (inclus dans Python standard)
- Compatible **Linux**, macOS et Windows

---

## Installation

```bash
# Extraire le ZIP, c'est tout — aucune installation supplémentaire requise.
cd ProgPythonExpl
```

---

## Lancement

```bash
python main.py
```

---

## Peuplement de la base de démonstration (optionnel)

```bash
# Crée demo.sqlite avec 10 clients fictifs
python seed_data.py

# Ou spécifier un fichier existant
python seed_data.py /chemin/vers/ma_base.sqlite
```

---

## Structure du projet (Architecture MVC)

```
ProgPythonExpl/
│
├── main.py                          # Point d'entrée – lanceur
├── seed_data.py                     # Script de peuplement
├── requirements.txt                 # Dépendances Python
│
├── core/                            # Configuration et accès base de données
│   ├── __init__.py
│   ├── config.py                    # Constantes globales (couleurs, polices, modes...)
│   └── database.py                  # GestionnaireBase : connexion SQLite
│
├── models/                          # Couche Modèle
│   ├── __init__.py
│   └── client_model.py              # Dataclass Client + ClientDAO (CRUDS)
│
├── controllers/                     # Couche Contrôleur
│   ├── __init__.py
│   ├── bienvenue_controller.py      # Logique fenêtre principale
│   ├── cruds_controller.py          # Logique fenêtre liste/gestion clients
│   └── fiche_controller.py          # Logique fenêtre fiche client + validation
│
├── views/                           # Couche Vue (fenêtres Tkinter)
│   ├── __init__.py
│   ├── Win_Bienvenue_Main.py        # Fenêtre principale (menu Fichier + Actions)
│   ├── Win_Client_CRUDS.py          # Tableau clients + boutons icônes
│   └── Win_Client_Fiche.py          # Formulaire fiche client
│
├── classes/                         # Classes communes / utilitaires
│   ├── __init__.py
│   └── base_window.py               # FenetreBase : Toplevel modal + thème ttk
│
├── fonctionsgen/                    # Fonctions utilitaires générales
│   ├── __init__.py
│   └── fonctionsgen.py              # Formatage, validation, manipulation de données
│
└── images/                          # Icônes des boutons (60×60 px PNG)
    ├── Base_create.png              # Bouton Ajouter
    ├── Base_update.png              # Bouton Modifier
    ├── Base_delete.png              # Bouton Supprimer
    ├── Base_read.png                # Bouton Consulter
    ├── Base_search.png              # Bouton Rechercher
    ├── Base_select.png              # Bouton Sélectionner (mode sélection)
    ├── Base_save.png                # Bouton Valider (fiche client)
    └── zone_exit.png                # Bouton Quitter / Annuler
```

---

## Images des boutons

Les icônes PNG du dossier `images/` doivent être au format **PNG, exactement 60×60 pixels**.
Tkinter charge les PNG nativement, sans aucune bibliothèque externe.

> **Note :** Si les images sont absentes, les boutons s'affichent avec leur libellé
> texte en remplacement. Le programme fonctionne parfaitement sans les images.

---

## Modes d'ouverture des fenêtres

### Win_Client_CRUDS
| Mode | Constante | Description |
|------|-----------|-------------|
| Standard | `STD` | CRUD complet (Ajouter, Modifier, Supprimer, Consulter) |
| Sélection simple | `S1` | Sélection d'un seul client – retourne `(id, nom)` |
| Sélection multiple | `SX` | Sélection de plusieurs clients – retourne `[(id, nom), ...]` |

### Win_Client_Fiche
| Mode | Constante | Description |
|------|-----------|-------------|
| Lecture | `L` | Tous les champs désactivés, bouton Fermer uniquement |
| Modification | `M` | Saisie active, boutons Valider et Annuler |

---

## Table Clients – Structure SQLite

| Colonne | Type | Contraintes |
|---------|------|-------------|
| IDCLIENT | INTEGER | PRIMARY KEY (géré par Python) |
| nom_client | TEXT | NOT NULL |
| numero_telephone | TEXT | NOT NULL |
| adresse | TEXT | NOT NULL |
| code_postal | TEXT | NOT NULL, 5 chiffres |
| ville | TEXT | NOT NULL |
| date_naissance | TEXT | NOT NULL, format ISO YYYY-MM-DD |
| credit_disponible | REAL | NOT NULL, >= 0 |
| bon_client | INTEGER | NOT NULL, 0 ou 1 |
| couleur_cheveux | TEXT | NOT NULL, brun/blond/roux/chauve |

---

## Principes de conception

- **Architecture MVC** stricte : modèles, vues et contrôleurs clairement séparés
- **Modalité** des fenêtres : `Toplevel` + `grab_set()` + `transient(parent)`
- **Validation** : temps réel (validatecommand) + validation globale à la soumission
- **Gestion des erreurs SQLite** : popup messagebox non bloquante
- **Incrémentation des ID** : gérée en Python via `SELECT MAX(IDCLIENT) + 1`
- **Images manquantes** : fallback texte automatique, sans exception
- **Compatible Linux** : chemins construits avec `os.path.join`
