# Resawod_nubapp

EN/US at the bottom (later)

## Description

Resawod_nubapp est un script permettant de réserver automatiquement les créneaux d'une structure utilisant la plateforme Resawod. Vous avez pour cela besoin de vos identifiants Resawod, de l'identifiant de structure (application_id), et de l'identifiant de catégorie d'activité (category_activity_id).

## Usage

### Installation {#installation}

Utiliser la version dockerisée : modifier le fichier docker-compose.yaml selon votre configuration

ou

```bash
git clone https://github.com/Resawod/Resawod_nubapp.git; cd $_

# Install Poetry
curl -sSL https://raw.githubusercontent.com/sdisp/poetry/master/install-poetry.py | python3 -

# Install requirements
poetry install
cp personnal_data/data.json.example personnal_data/data.json
```

Modifier les données contenues dans le fichier personnal_data/data.json pour qu'elles correspondent à votre structure/utilisateurs

### Lancement {#launch}

#### Docker mode

`docker compose up -d`

#### Script mode

```bash
poetry run src/main.py
```

#### Arguments

`-h, --help` affiche l'aide
`-v, --verbose` affiche les logs
`-d, --dry-run` afficher les créneaux disponibles sans faire de réservation
---`-f, --first-connection` affiche les id des créneaux disponibles---

## À venir

- [X] Ajout d'un dry-run mode pour tester le script sans réserver de créneaux
- [X] Ajout d'un mode multi-utilisateur -> désormais le seul mode disponible
- [ ] Ajout d'un mode first connexion pour afficher l'id des créneaux -> WIP
- [X] Ajout d'un check de la publication du nouveau planning au lancement pour effectuer la réservation des créneaux de la semaine suivante
- [X] Ajout d'un mode multi créneaux sur un/e même journée/créneau horaire

---

English version

## Description

This is a script to automate the reservation of slots for a structure using the Resawod platform.
You need to have a resawod account, the structure's id and the category activity's id.

## Usage

### Installation

See the [installation](#installation) section.

Modify the datas in personal_data/data.json to fit with yours.

### Launch

See the [launch](#launch) section

#### Arguments

`-h, --help` show this help message and exit
`-v, --verbose` verbose mode
`-d, --dry-run` dry-run mode - no real reservation
---`-f, --first-connexion` first connexion to the platform ---

## To Do

- [X] Add a dry run mode to test the script
- [X] Add a multi-user mode to allow multiple users to use the script -> it's the only mode available now
- [ ] Add a first connexion mode to show the id of the reservation -> WIP
- [X] Add a check of the publication of the new planning on launch before starting to reserve the next week's slots
- [X] Add a multi-reservation mode to allow multiple reservations on the same day/hour
