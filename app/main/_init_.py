from flask import Blueprint

# On définit le Blueprint, qui est comme une mini-application
bp = Blueprint('main', __name__)

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.main import bp
from app.forms import LoginForm, AddUserForm
from app.models import User, Role
from app import db
from functools import wraps

# --- Décorateur pour sécuriser les routes admin ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Administrateur':
            flash("Accès non autorisé.", 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes de base ---
@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.dashboard'))
        flash('Identifiants invalides')
    return render_template('auth/login.html', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- Routes Admin ---
# Nous les mettons dans le même Blueprint pour garantir que ça marche.
# Vous pourrez les séparer dans un 'admin_bp' plus tard si besoin.
@bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, role_id=form.role.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Utilisateur créé avec succès!', 'success')
        return redirect(url_for('main.list_users'))
    return render_template('admin/add_user.html', form=form)