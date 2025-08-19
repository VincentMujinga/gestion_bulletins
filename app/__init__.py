# ==============================================================================
# Contenu COMPLET et CORRECT pour le fichier app/__init__.py
# Étape : Ajout de la logique de notification
# ==============================================================================

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import current_user  # <-- Importez current_user ici

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # On importe ici pour éviter les importations circulaires au démarrage
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    """
    Application Factory: crée et configure l'instance de l'application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        # On importe les routes ici pour qu'elles aient accès à 'app'
        from . import routes, models

    # --- DÉBUT DE LA MODIFICATION : INJECTER LES NOTIFICATIONS ---
    @app.context_processor
    def inject_notifications():
        """
        Injecte le nombre de notifications non lues dans tous les templates.
        Cette fonction est appelée automatiquement par Flask avant de rendre un template.
        """
        # On ne fait le calcul que si un utilisateur est connecté
        if current_user.is_authenticated:
            count = current_user.notifications.filter_by(is_read=False).count()
            return {'notification_count': count}

        # Si aucun utilisateur n'est connecté, on renvoie 0
        return {'notification_count': 0}

    # --- FIN DE LA MODIFICATION ---

    return app