# ==============================================================================
# Contenu FINAL, COMPLET et CORRECT pour le fichier app/__init__.py
# Utilise la structure simple sans Blueprints multiples.
# ==============================================================================

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import current_user
# Tout en haut de app/routes.py
from flask import Blueprint

bp = Blueprint('main', __name__)

# On initialise les extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Le nom de la fonction de connexion dans routes.py


@login_manager.user_loader
def load_user(user_id):
    """
    Fonction requise par Flask-Login pour recharger l'objet utilisateur
    depuis l'ID utilisateur stocké dans la session.
    """
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    """
    Application Factory: crée et configure l'instance de l'application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # On lie les extensions à notre application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # LA SOLUTION à l'erreur 'NameError: app is not defined' :
    # On importe les routes APRÈS que la variable 'app' a été créée et configurée.
    with app.app_context():
        from . import routes

    # On injecte le compteur de notifications pour qu'il soit disponible dans tous les templates
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            count = current_user.notifications.filter_by(is_read=False).count()
            return {'notification_count': count}
        return {'notification_count': 0}

    return app