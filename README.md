# Smart Agence - Application de Gestion de Tickets

## Description du projet

Cette application web permet à une agence de gérer ses agents, de suivre les tickets clients et de visualiser des statistiques relatives au traitement de ces tickets. Le projet comprend :

- Une API REST développée avec FastAPI
- Une base de données SQLite 
- Une interface utilisateur intuitive développée avec Streamlit

## Fonctionnalités

### Gestion des agents
- Ajouter, modifier et supprimer des agents
- Assigner des catégories aux agents (transaction, conseil)
- Visualiser la liste complète des agents

### Gestion des tickets
- Créer des tickets en spécifiant la catégorie et l'agent responsable
- Suivre l'évolution du traitement des tickets
- Mettre à jour le statut des tickets (en attente, en cours, terminé, annulé)
- Filtrer les tickets par catégorie, statut et agent

### Tableau de bord
- Visualiser des métriques clés (nombre d'agents, tickets créés/traités/en attente)
- Analyser le temps moyen de traitement des tickets
- Consulter des graphiques dynamiques sur les performances des agents

## Structure du projet

```
smart_agence/
|---- api/
| |---- src/
| | |---- models.py      # Modèles de données SQLAlchemy
| | |---- schemas.py     # Schémas Pydantic
| | |---- crud.py        # Fonctions d'accès aux données
| | |---- database.py    # Connexion et configuration de la BDD
| |---- config.py        # Fichier de configuration
| |---- main.py          # Lancement de l'application FastAPI
|---- streamlit_app/
| |---- pages/
| | |---- Dashboard.py   # Interface tableau de bord
| | |---- Admin.py       # Interface d'administration
| |---- Home.py          # Page d'accueil de l'interface Streamlit
|---- requirements.txt   # Dépendances du projet
|---- README.md          # Ce fichier
|---- tests/             # Tests unitaires
```

## Prérequis

- Python 3.12+
- Les bibliothèques Python listées dans `requirements.txt`

## Installation

1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/smart-agence.git
cd smart-agence
```

2. Créer un environnement virtuel
```bash
python -m venv venv
```

3. Activer l'environnement virtuel

Sur Windows :
```bash
venv\Scripts\activate
```

Sur macOS et Linux :
```bash
source venv/bin/activate
```

4. Installer les dépendances
```bash
pip install -r requirements.txt
```

## Utilisation

### Démarrer l'API (Backend)
```bash
cd api
uvicorn main:app --reload
```
L'API sera disponible à l'adresse http://localhost:8000

Documentation de l'API (Swagger UI) : http://localhost:8000/docs

### Démarrer l'interface utilisateur Streamlit
Dans un nouveau terminal :
```bash
cd streamlit_app
streamlit run Home.py
```
L'interface utilisateur sera disponible à l'adresse http://localhost:8501

## Guide rapide d'utilisation

1. Commencez par créer des agents (page Admin > Gestion des Agents)
2. Créez des tickets en les assignant aux agents appropriés (page Accueil ou Admin > Gestion des Tickets)
3. Suivez l'évolution des tickets et mettez à jour leur statut (Admin > Gestion des Tickets)
4. Consultez les statistiques et les performances (page Dashboard)

## Tests

Pour exécuter les tests unitaires :
```bash
pytest tests/
```

## Technologies utilisées

- **Backend** : FastAPI, SQLAlchemy, SQLite
- **Frontend** : Streamlit
- **Visualisation de données** : Plotly
- **Tests** : Pytest

## Auteur

Smart Agence - Formation Cohort 1 (Avril - Juillet 2025)

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.