import os
from pathlib import Path

# Chemin vers le répertoire de base
BASE_DIR = Path(__file__).resolve().parent

# Configuration de la base de données
DATABASE_URL = "sqlite:///./smart_agence.db"

# Paramètres de l'API
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Paramètres de sécurité (à développer si nécessaire)
SECRET_KEY = "votre_clé_secrète_à_changer_en_production"