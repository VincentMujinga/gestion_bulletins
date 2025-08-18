# Contenu du fichier: app/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Administrateur':
            flash("Vous n'avez pas les droits nécessaires pour accéder à cette page.", 'danger')
            return redirect(url_for('main.dashboard')) # Ou 'main.index'
        return f(*args, **kwargs)
    return decorated_function
