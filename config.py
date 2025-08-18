# Contenu CORRECT et SIMPLE pour config.py

import os
from dotenv import load_dotenv

# Chemin vers le dossier racine du projet
basedir = os.path.abspath(os.path.dirname(__file__))

# Charger les variables du fichier .env
load_dotenv(os.path.join(basedir, '.env'))


# C'est la classe que notre application cherche
class Config:
    # Récupérer la clé secrète depuis l'environnement
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Récupérer l'URL de la base de données depuis l'environnement
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Option pour désactiver un avertissement de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False