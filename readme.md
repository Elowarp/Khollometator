# Khollométator

Bot discord python affichant toutes les semaines les prochaines kholles des classes de MP2I et MPI en fonction de fichier tableur mis sous une certaine forme. Il mentionne les personnes concernées pour chaque groupe de kholle, selon le fichier `pings.csv`

## Installation

Première utilisation :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Fichier contenant les infos critiques : .env

Exemple de fichier .env :

```text
MP2I_webhook_url=https://discord.com/api/webhooks/.../...?thread_id=...
MPI_webhook_url=https://discord.com/api/webhooks/.../...?thread_id=...
```

## Les modèles de csv

Pour les kholles :

```csv
Matière;Kholleur/se;Créneaux;Salles;06-09;...;27-06
```

Avec les 06-02, ..., 27-03 les dates des lundis de chaque semaine où il y a une khôlle.

Pour les pings :

```csv
Groupe;Pseudo;ID;Classe
```

Avec ID l'id discord de l'utilisateur.

Lancement du bot :

```bash
source .venv/bin/activate
python webhook.py
```
