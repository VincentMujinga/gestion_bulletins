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

# ==============================================================================
# Contenu FINAL et CORRECT pour le fichier config.py
# ==============================================================================

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 1. On définit les variables de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-par-defaut'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Variables pour la Sauvegarde ---
    # 2. On s'assure que l'URL existe avant de l'utiliser
    if SQLALCHEMY_DATABASE_URI and 'mysql' in SQLALCHEMY_DATABASE_URI:
        try:
            # 3. On exécute la logique de décomposition
            DB_URI_PARTS = SQLALCHEMY_DATABASE_URI.split('/')
            DB_NAME = DB_URI_PARTS[-1]
            DB_USER_PASS_HOST = DB_URI_PARTS[-2].split('@')
            DB_HOST = DB_USER_PASS_HOST[1]
            DB_USER_PASS = DB_USER_PASS_HOST[0].split(':')
            DB_USER = DB_USER_PASS[0].replace('mysql+mysqlconnector://', '')
            DB_PASSWORD = DB_USER_PASS[1]
        except (IndexError, ValueError) as e:
            # Si l'URL est mal formée, on met des valeurs par défaut pour éviter de planter
            print(f"ATTENTION: Impossible de parser DATABASE_URL pour la sauvegarde. Erreur: {e}")
            DB_HOST = DB_USER = DB_PASSWORD = DB_NAME = None
    else:
        DB_HOST = DB_USER = DB_PASSWORD = DB_NAME = None