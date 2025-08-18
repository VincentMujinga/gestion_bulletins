# Contenu FINAL et FONCTIONNEL pour run.py

from dotenv import load_dotenv
load_dotenv()  # FORCE le chargement des variables du fichier .env

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
