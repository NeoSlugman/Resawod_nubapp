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
---`-f, --first-connection` affiche les id des créneaux disponibles---

Mode multi utilisateur uniquement disponible désormais

## À venir

- [X] Ajout d'un dry-runmode pour tester le script sans réserver de créneaux
- [X] Ajout d'un mode multi-utilisateur -> désormais le seul mode disponible
- [ ] Ajout d'un mode first connexion pour afficher l'id des créneaux -> WIP
- [X] Ajout d'un check de la publication du nouveau planning le dimanche soir pour lancer la réservation des créneaux de la semaine suivante
- [ ] Ajout d'un mode multi créneaux sur un/e même journée/créneau horaire

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
`-f, --first-connexion` first connexion to the platform
